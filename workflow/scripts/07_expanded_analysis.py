#!/usr/bin/env python3
"""
Step 07 — Expanded DADA2 Analysis
Author: Dr. Oluwamayowa Ogun
Dataset: Baxter et al. 2019 — SRP128128 — wint17 inulin arm
Framework: DRSWAE — S phase (Scripting)

Formalised from notebooks/07_expanded_analysis.ipynb.
Runs alpha diversity, beta diversity, differential abundance,
and responder vs non-responder comparison on the complete
wint17 cohort (27 participants, 882 ASVs).
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for script execution
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests
from skbio.diversity import alpha_diversity, beta_diversity
from skbio.stats.ordination import pcoa
from skbio.stats.distance import permanova
import os
import sys

# set working directory to pipeline root
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

EXPORT_DIR = "results/qiime2/exported"

print("=== Step 07: Expanded DADA2 Analysis ===")
print("Complete wint17 inulin cohort — 27 participants")
print()

# ============================================================
# participant metadata — butyrate measurements from HPLC
# ============================================================
participant_metadata = {
    'U307': {'butyrate_before': 5.93,  'butyrate_during': 14.80, 'response': 'moderate_responder'},
    'U310': {'butyrate_before': 15.83, 'butyrate_during': 12.34, 'response': 'non_responder'},
    'U311': {'butyrate_before': 10.96, 'butyrate_during': 15.68, 'response': 'moderate_responder'},
    'U312': {'butyrate_before': 11.68, 'butyrate_during': 10.38, 'response': 'non_responder'},
    'U313': {'butyrate_before': 11.31, 'butyrate_during': 13.08, 'response': 'moderate_responder'},
    'U315': {'butyrate_before': 12.06, 'butyrate_during': 33.05, 'response': 'strong_responder'},
    'U316': {'butyrate_before': 22.74, 'butyrate_during': 30.47, 'response': 'moderate_responder'},
    'U317': {'butyrate_before': 3.68,  'butyrate_during': 24.98, 'response': 'strong_responder'},
    'U318': {'butyrate_before': 25.92, 'butyrate_during': 26.67, 'response': 'non_responder'},
    'U322': {'butyrate_before': 5.15,  'butyrate_during': 8.22,  'response': 'moderate_responder'},
    'U323': {'butyrate_before': 12.30, 'butyrate_during': 10.97, 'response': 'non_responder'},
    'U325': {'butyrate_before': 20.17, 'butyrate_during': 27.76, 'response': 'moderate_responder'},
    'U326': {'butyrate_before': 14.75, 'butyrate_during': 13.40, 'response': 'non_responder'},
    'U327': {'butyrate_before': 7.09,  'butyrate_during': 13.77, 'response': 'moderate_responder'},
    'U328': {'butyrate_before': 5.86,  'butyrate_during': 14.39, 'response': 'moderate_responder'},
    'U329': {'butyrate_before': 2.06,  'butyrate_during': 20.36, 'response': 'strong_responder'},
    'U331': {'butyrate_before': 5.96,  'butyrate_during': 19.75, 'response': 'strong_responder'},
    'U332': {'butyrate_before': 22.38, 'butyrate_during': 6.85,  'response': 'decreaser'},
    'U333': {'butyrate_before': 43.66, 'butyrate_during': 15.45, 'response': 'decreaser'},
    'U334': {'butyrate_before': 13.83, 'butyrate_during': 43.01, 'response': 'strong_responder'},
    'U335': {'butyrate_before': 9.86,  'butyrate_during': 16.73, 'response': 'moderate_responder'},
    'U336': {'butyrate_before': 10.93, 'butyrate_during': 10.19, 'response': 'non_responder'},
    'U338': {'butyrate_before': 4.51,  'butyrate_during': 10.94, 'response': 'moderate_responder'},
    'U339': {'butyrate_before': 7.59,  'butyrate_during': 5.61,  'response': 'non_responder'},
    'U341': {'butyrate_before': 11.09, 'butyrate_during': 9.37,  'response': 'non_responder'},
    'U343': {'butyrate_before': 13.00, 'butyrate_during': 9.64,  'response': 'non_responder'},
    'U344': {'butyrate_before': 11.04, 'butyrate_during': 34.44, 'response': 'strong_responder'},
}

meta_df = pd.DataFrame(participant_metadata).T
meta_df['butyrate_change'] = (meta_df['butyrate_during'].astype(float) -
                               meta_df['butyrate_before'].astype(float))
participants_ordered = sorted(participant_metadata.keys())

response_colors = {
    'strong_responder':   '#1A6B3C',
    'moderate_responder': '#C47F0A',
    'non_responder':      '#888888',
    'decreaser':          '#A32D2D'
}

# ============================================================
# 1. Load data
# ============================================================
print("[1/7] Loading ASV table and taxonomy...")
asv_table = pd.read_csv(
    f'{EXPORT_DIR}/feature-table.tsv',
    sep='\t', skiprows=1, index_col=0)

taxonomy = pd.read_csv(
    f'{EXPORT_DIR}/taxonomy.tsv',
    sep='\t', index_col=0)

taxonomy['Genus'] = (taxonomy['Taxon'].str.split(';')
                     .str[5].str.strip().str.replace('g__', ''))

# join and aggregate to genus level
asv_tax = asv_table.join(taxonomy[['Genus']])
sample_cols = [c for c in asv_tax.columns if c != 'Genus']
genus_table = asv_tax.groupby('Genus')[sample_cols].sum()

# relative abundance normalisation
rel_abund = genus_table.div(genus_table.sum(axis=0), axis=1) * 100

print(f"  ASV table: {asv_table.shape}")
print(f"  Genera: {genus_table.shape[0]}")

# ============================================================
# 2. Save metadata and butyrate response figure
# ============================================================
print("[2/7] Generating butyrate response figure...")
meta_df.to_csv(f'{EXPORT_DIR}/participant_metadata.csv')

sorted_meta = meta_df.sort_values('butyrate_change', ascending=False)
colors = [response_colors[r] for r in sorted_meta['response']]

fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(sorted_meta.index, sorted_meta['butyrate_change'].astype(float),
       color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
ax.axhline(y=0, color='black', linewidth=0.8)
legend_elements = [
    mpatches.Patch(facecolor='#1A6B3C', label='Strong responder (n=6)'),
    mpatches.Patch(facecolor='#C47F0A', label='Moderate responder (n=10)'),
    mpatches.Patch(facecolor='#888888', label='Non-responder (n=9)'),
    mpatches.Patch(facecolor='#A32D2D', label='Decreaser (n=2)'),
]
ax.legend(handles=legend_elements, fontsize=10, loc='upper right')
ax.set_xlabel('Participant', fontsize=12)
ax.set_ylabel('Butyrate Change (mmol/kg)', fontsize=12)
ax.set_title('Individual Butyrate Response to Inulin Supplementation\n'
             'Baseline vs During — 27 Participants, wint17 cohort', fontsize=12)
ax.tick_params(axis='x', rotation=45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/butyrate_response_27participants.png',
            dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 3. Per-participant fold changes
# ============================================================
print("[3/7] Computing fold changes and individual response figure...")
target_genera = ['Bifidobacterium', 'Anaerostipes', 'Akkermansia']
targets_rel = rel_abund.loc[rel_abund.index.isin(target_genera)]

# fold changes with presence filter
detection_threshold = 0.01
fc_filtered = {}
for participant in participants_ordered:
    before_col = f"{participant}-before"
    during_col = f"{participant}-during"
    if before_col in targets_rel.columns and during_col in targets_rel.columns:
        before_vals = targets_rel[before_col]
        during_vals = targets_rel[during_col]
        detected = (before_vals > detection_threshold) | (during_vals > detection_threshold)
        fc = pd.Series(index=before_vals.index, dtype=float)
        fc[detected] = ((during_vals[detected] + 0.001) /
                        (before_vals[detected] + 0.001)).round(2)
        fc[~detected] = np.nan
        fc_filtered[participant] = fc

fc_filtered_df = pd.DataFrame(fc_filtered)
fc_filtered_df.to_csv(f'{EXPORT_DIR}/fold_changes_27participants.csv')

# individual bar chart
fig, axes = plt.subplots(2, 1, figsize=(18, 12))
for ax, genus in zip(axes, ['Bifidobacterium', 'Anaerostipes']):
    x = np.arange(len(participants_ordered))
    width = 0.35
    before_vals = []
    during_vals = []
    bar_colors = []
    for p in participants_ordered:
        before_col = f"{p}-before"
        during_col = f"{p}-during"
        if genus in rel_abund.index:
            before_vals.append(rel_abund.loc[genus, before_col])
            during_vals.append(rel_abund.loc[genus, during_col])
        else:
            before_vals.append(0)
            during_vals.append(0)
        bar_colors.append(response_colors[participant_metadata[p]['response']])
    ax.bar(x - width/2, before_vals, width, color='#CCCCCC',
           alpha=0.85, label='Before', edgecolor='white')
    ax.bar(x + width/2, during_vals, width, color=bar_colors,
           alpha=0.85, label='During', edgecolor='white')
    ax.set_title(f'{genus} — Relative Abundance Before vs During Inulin',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Participant', fontsize=11)
    ax.set_ylabel('Relative Abundance (%)', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(participants_ordered, rotation=45, ha='right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

legend_elements = [
    mpatches.Patch(facecolor='#CCCCCC', label='Before intervention'),
    mpatches.Patch(facecolor='#1A6B3C', label='During — strong responder'),
    mpatches.Patch(facecolor='#C47F0A', label='During — moderate responder'),
    mpatches.Patch(facecolor='#888888', label='During — non-responder'),
    mpatches.Patch(facecolor='#A32D2D', label='During — decreaser'),
]
fig.legend(handles=legend_elements, loc='upper right',
           fontsize=10, bbox_to_anchor=(1.0, 1.0))
plt.suptitle('Individual Inulin Response — 27 Participants, wint17 cohort\n'
             'DADA2 ASV Reanalysis — Baxter et al. 2019', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/individual_response_27participants.png',
            dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 4. Alpha diversity
# ============================================================
print("[4/7] Computing alpha diversity — Shannon entropy...")
asv_counts = asv_table.astype(int)
shannon_values = {}
for sample in asv_counts.columns:
    counts = asv_counts[sample].values
    shannon_values[sample] = alpha_diversity('shannon', counts)[0]
shannon_series = pd.Series(shannon_values, name='shannon')

shannon_before = np.array([shannon_series[f"{p}-before"]
                            for p in participants_ordered])
shannon_during = np.array([shannon_series[f"{p}-during"]
                            for p in participants_ordered])
stat, pvalue = wilcoxon(shannon_before, shannon_during)

print(f"  Shannon before: {shannon_before.mean():.3f}")
print(f"  Shannon during: {shannon_during.mean():.3f}")
print(f"  Wilcoxon W={stat:.1f}, p={pvalue:.4f}")

# alpha diversity figure
fig, ax = plt.subplots(figsize=(8, 6))
for i, p in enumerate(participants_ordered):
    color = response_colors[participant_metadata[p]['response']]
    ax.plot([0, 1], [shannon_before[i], shannon_during[i]],
            color=color, alpha=0.5, linewidth=1.2)
bp = ax.boxplot([shannon_before, shannon_during], positions=[0, 1],
                widths=0.35, patch_artist=True,
                medianprops={'color': 'black', 'linewidth': 2})
bp['boxes'][0].set_facecolor('#CCCCCC')
bp['boxes'][0].set_alpha(0.6)
bp['boxes'][1].set_facecolor('#4A90A4')
bp['boxes'][1].set_alpha(0.6)
ax.set_xticks([0, 1])
ax.set_xticklabels(['Before', 'During'], fontsize=12)
ax.set_ylabel('Shannon Entropy', fontsize=12)
ax.set_title(f'Alpha Diversity — Shannon Entropy\n'
             f'Inulin Supplementation, n=27\n'
             f'Paired Wilcoxon W={stat:.1f}, p={pvalue:.4f}', fontsize=11)
legend_elements = [
    mpatches.Patch(facecolor='#1A6B3C', label='Strong responder'),
    mpatches.Patch(facecolor='#C47F0A', label='Moderate responder'),
    mpatches.Patch(facecolor='#888888', label='Non-responder'),
    mpatches.Patch(facecolor='#A32D2D', label='Decreaser'),
]
ax.legend(handles=legend_elements, fontsize=9, loc='lower left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/alpha_diversity_shannon.png',
            dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 5. Beta diversity
# ============================================================
print("[5/7] Computing beta diversity — Bray-Curtis PCoA and PERMANOVA...")
sample_ids = list(asv_counts.columns)
counts_matrix = asv_counts.T.values
bc_dm = beta_diversity('braycurtis', counts_matrix, ids=sample_ids)
pcoa_results = pcoa(bc_dm)
pcoa_df = pcoa_results.samples[['PC1', 'PC2']].copy()
pcoa_df['timepoint'] = ['before' if 'before' in s else 'during'
                         for s in pcoa_df.index]
pcoa_df['participant'] = [s.split('-')[0] for s in pcoa_df.index]
pcoa_df['response'] = [participant_metadata[p]['response']
                        for p in pcoa_df['participant']]
pc1_var = pcoa_results.proportion_explained.iloc[0] * 100
pc2_var = pcoa_results.proportion_explained.iloc[1] * 100

# PERMANOVA
grouping = pd.Series(
    ['before' if 'before' in s else 'during' for s in sample_ids],
    index=sample_ids, name='timepoint')
permanova_results = permanova(bc_dm, grouping, permutations=999)
print(f"  PERMANOVA pseudo-F={permanova_results['test statistic']:.4f}, "
      f"p={permanova_results['p-value']:.4f}")

# PCoA figure
fig, ax = plt.subplots(figsize=(10, 8))
for participant in participants_ordered:
    color = response_colors[participant_metadata[participant]['response']]
    before_row = pcoa_df[pcoa_df.index == f"{participant}-before"]
    during_row = pcoa_df[pcoa_df.index == f"{participant}-during"]
    if not before_row.empty and not during_row.empty:
        ax.plot([before_row['PC1'].values[0], during_row['PC1'].values[0]],
                [before_row['PC2'].values[0], during_row['PC2'].values[0]],
                color=color, alpha=0.4, linewidth=0.8, zorder=2)
        ax.scatter(before_row['PC1'], before_row['PC2'], color=color,
                   s=60, alpha=0.7, facecolors='none', edgecolors=color,
                   linewidth=1.5, zorder=3)
        ax.scatter(during_row['PC1'], during_row['PC2'], color=color,
                   s=60, alpha=0.7, zorder=3)
ax.set_xlabel(f'PC1 ({pc1_var:.1f}% variance)', fontsize=12)
ax.set_ylabel(f'PC2 ({pc2_var:.1f}% variance)', fontsize=12)
ax.set_title('Beta Diversity — Bray-Curtis PCoA\n'
             'Inulin Supplementation, n=27\n'
             'Open = Before, Filled = During', fontsize=11)
legend_elements = [
    mpatches.Patch(facecolor='#1A6B3C', label='Strong responder'),
    mpatches.Patch(facecolor='#C47F0A', label='Moderate responder'),
    mpatches.Patch(facecolor='#888888', label='Non-responder'),
    mpatches.Patch(facecolor='#A32D2D', label='Decreaser'),
]
ax.legend(handles=legend_elements, fontsize=9, loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/beta_diversity_pcoa.png',
            dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 6. Differential abundance — paired Wilcoxon
# ============================================================
print("[6/7] Running differential abundance — paired Wilcoxon...")
wilcoxon_results = []
for genus in rel_abund.index:
    before_vals = [rel_abund.loc[genus, f"{p}-before"]
                   for p in participants_ordered]
    during_vals = [rel_abund.loc[genus, f"{p}-during"]
                   for p in participants_ordered]
    before_arr = np.array(before_vals)
    during_arr = np.array(during_vals)
    if np.all(before_arr == during_arr):
        continue
    try:
        stat, pval = wilcoxon(before_arr, during_arr)
        mean_fc = (during_arr.mean() + 0.001) / (before_arr.mean() + 0.001)
        wilcoxon_results.append({
            'Genus': genus,
            'mean_before': round(before_arr.mean(), 4),
            'mean_during': round(during_arr.mean(), 4),
            'fold_change': round(mean_fc, 3),
            'pvalue': pval
        })
    except:
        continue

wilcoxon_df = pd.DataFrame(wilcoxon_results)
wilcoxon_df['adjusted_pvalue'] = multipletests(
    wilcoxon_df['pvalue'], method='fdr_bh')[1]
wilcoxon_df = wilcoxon_df.sort_values('adjusted_pvalue').reset_index(drop=True)
wilcoxon_df['log2_fc'] = np.log2(wilcoxon_df['fold_change'].clip(lower=0.001))
wilcoxon_df['neg_log10_p'] = -np.log10(wilcoxon_df['pvalue'].clip(lower=1e-10))
wilcoxon_df.to_csv(f'{EXPORT_DIR}/differential_abundance_27participants.csv',
                   index=False)

print(f"  Genera tested: {len(wilcoxon_df)}")
print(f"  Significant after FDR: {(wilcoxon_df['adjusted_pvalue'] < 0.05).sum()}")

# volcano plot
label_genera = ['Bifidobacterium', 'Anaerostipes', 'Akkermansia',
                'Faecalibacterium', 'Alistipes', 'Intestinibacter']
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(wilcoxon_df['log2_fc'], wilcoxon_df['neg_log10_p'],
           color='lightgrey', alpha=0.6, s=40, zorder=2)
enriched = (wilcoxon_df['pvalue'] < 0.05) & (wilcoxon_df['log2_fc'] > 0)
depleted = (wilcoxon_df['pvalue'] < 0.05) & (wilcoxon_df['log2_fc'] < 0)
ax.scatter(wilcoxon_df.loc[enriched, 'log2_fc'],
           wilcoxon_df.loc[enriched, 'neg_log10_p'],
           color='#1A6B3C', s=60, zorder=3, label='Enriched (p<0.05)')
ax.scatter(wilcoxon_df.loc[depleted, 'log2_fc'],
           wilcoxon_df.loc[depleted, 'neg_log10_p'],
           color='#A32D2D', s=60, zorder=3, label='Depleted (p<0.05)')
for _, row in wilcoxon_df[wilcoxon_df['Genus'].isin(label_genera)].iterrows():
    ax.annotate(row['Genus'],
                xy=(row['log2_fc'], row['neg_log10_p']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=9, fontweight='bold',
                color='#1A6B3C' if row['log2_fc'] > 0 else '#A32D2D')
ax.axhline(y=-np.log10(0.05), color='orange', linestyle='--',
           linewidth=1, label='p = 0.05', alpha=0.8)
ax.axvline(x=0, color='grey', linestyle='-', linewidth=0.5, alpha=0.4)
ax.set_xlabel('log₂ Fold Change (during / before)', fontsize=12)
ax.set_ylabel('-log₁₀ p-value (raw)', fontsize=12)
ax.set_title('Differential Abundance — Inulin Supplementation\n'
             'Paired Wilcoxon test, n=27 — raw p-values shown\n'
             'Note: no genera survive BH FDR correction', fontsize=11)
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/volcano_plot_27participants.png',
            dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 7. Responder vs non-responder baseline comparison
# ============================================================
print("[7/7] Running responder vs non-responder baseline comparison...")
strong_responders = [p for p, m in participant_metadata.items()
                     if m['response'] == 'strong_responder']
non_responders = [p for p, m in participant_metadata.items()
                  if m['response'] == 'non_responder']

responder_before = rel_abund[[f"{p}-before" for p in strong_responders]]
non_responder_before = rel_abund[[f"{p}-before" for p in non_responders]]

mw_results = []
for genus in rel_abund.index:
    resp_vals = responder_before.loc[genus].values
    non_resp_vals = non_responder_before.loc[genus].values
    if np.all(resp_vals == 0) and np.all(non_resp_vals == 0):
        continue
    stat, pval = stats.mannwhitneyu(resp_vals, non_resp_vals,
                                     alternative='two-sided')
    mw_results.append({
        'Genus': genus,
        'Mean Responder (%)': round(resp_vals.mean(), 4),
        'Mean Non-Responder (%)': round(non_resp_vals.mean(), 4),
        'Difference': round(resp_vals.mean() - non_resp_vals.mean(), 4),
        'pvalue': pval
    })

mw_df = pd.DataFrame(mw_results)
mw_df['adjusted_pvalue'] = multipletests(mw_df['pvalue'], method='fdr_bh')[1]
mw_df = mw_df.sort_values('adjusted_pvalue').reset_index(drop=True)
mw_df.to_csv(f'{EXPORT_DIR}/baseline_responder_comparison.csv', index=False)

# baseline comparison figure
top_genera = (responder_before.mean(axis=1) +
              non_responder_before.mean(axis=1)).nlargest(15).index
plot_df = pd.DataFrame({
    'Strong Responder': responder_before.loc[top_genera].mean(axis=1),
    'Non-Responder': non_responder_before.loc[top_genera].mean(axis=1)
})
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(top_genera))
width = 0.35
ax.bar(x - width/2, plot_df['Strong Responder'], width,
       color='#1A6B3C', alpha=0.85, label='Strong Responder (n=6)')
ax.bar(x + width/2, plot_df['Non-Responder'], width,
       color='#888888', alpha=0.85, label='Non-Responder (n=9)')
ax.set_xticks(x)
ax.set_xticklabels(top_genera, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Mean Relative Abundance (%)', fontsize=12)
ax.set_title('Baseline Microbiome Composition\n'
             'Strong Responders vs Non-Responders — Before Inulin Intervention',
             fontsize=12)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/baseline_responder_comparison.png',
            dpi=150, bbox_inches='tight')
plt.close()

print()
print("=== Step 07 Complete ===")
print(f"Figures saved to {EXPORT_DIR}/")
print(f"CSV results saved to {EXPORT_DIR}/")
