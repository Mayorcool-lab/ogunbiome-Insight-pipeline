#!/usr/bin/env python3
"""
Step 08 — PICRUSt2 Functional Profiling and Extended Diversity Analysis
Author: Dr. Oluwamayowa Ogun
Dataset: Baxter et al. 2019 — SRP128128 — wint17 inulin arm
Framework: DRSWAE — S phase (Scripting)
Formalised from notebooks/08_picrust2_functional_analysis.ipynb.
Runs Faith's PD, Weighted UniFrac, PERMDISP, rarefaction curves,
Spearman correlation, LEfSe, PICRUSt2 pathway analysis, and
Random Forest responder prediction on the complete wint17 cohort.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
from scipy.stats import wilcoxon, kruskal
from skbio.diversity import alpha_diversity, beta_diversity
from skbio.stats.ordination import pcoa
from skbio.stats.distance import permanova, permdisp
from skbio import TreeNode
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import warnings
import os
import sys
warnings.filterwarnings('ignore')

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

GREEN = '#1A6B3C'
GOLD  = '#C47F0A'
EXPORT_DIR = "results/qiime2/exported"
PICRUST_DIR = "results/picrust2"

print("=== Step 08: PICRUSt2 Functional Profiling and Extended Diversity ===")
print("Complete wint17 inulin cohort — 27 participants")
print()
# ============================================================
# load input data
# ============================================================
asv_table = pd.read_csv('results/qiime2/exported/feature-table.tsv',
                         sep='\t', index_col=0, skiprows=1)
taxonomy = pd.read_csv('results/qiime2/exported/taxonomy.tsv',
                        sep='\t', index_col=0)
pathway_abun = pd.read_csv('results/picrust2/path_abun_unstrat.tsv.gz',
                            sep='\t', index_col=0, compression='gzip')
tree = TreeNode.read('results/picrust2/bac_reduced.tre')

print(f"ASV table: {asv_table.shape[0]} ASVs x {asv_table.shape[1]} samples")
print(f"Pathways: {pathway_abun.shape[0]} x {pathway_abun.shape[1]} samples")
print(f"Tree tips: {sum(1 for _ in tree.tips())}")

# participant metadata
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
meta_df['butyrate_change'] = meta_df['butyrate_during'].astype(float) - meta_df['butyrate_before'].astype(float)
# ============================================================
# prepare ASV matrix and filter to tree taxa
# ============================================================
asv_matrix = asv_table.T.fillna(0).astype(int)
tree_tips = set([tip.name for tip in tree.tips()])
asv_in_tree = [asv for asv in asv_table.index if asv in tree_tips]
asv_matrix_filtered = asv_matrix[asv_in_tree]
print(f"ASVs in tree: {len(asv_in_tree)} of {len(asv_table.index)}")

# ============================================================
# rarefaction curve
# ============================================================
depths = sorted(set([500, 1000, 2000, 5000, 9000, 15000, 20000,
                     int(asv_matrix.sum(axis=1).min())]))
rarefaction_results = []
for depth in depths:
    for sample in asv_matrix.index:
        counts = asv_matrix.loc[sample].values
        if counts.sum() >= depth:
            np.random.seed(42)
            indices = np.repeat(np.arange(len(counts)), counts)
            subsampled = np.random.choice(indices, size=depth, replace=False)
            observed = len(np.unique(subsampled))
            rarefaction_results.append({'sample': sample, 'depth': depth,
                                        'observed_asvs': observed})
raref_df = pd.DataFrame(rarefaction_results)

fig, ax = plt.subplots(figsize=(10, 6))
for sample in asv_matrix.index:
    sample_data = raref_df[raref_df['sample'] == sample]
    color = GREEN if 'before' in sample else GOLD
    ax.plot(sample_data['depth'], sample_data['observed_asvs'],
            color=color, alpha=0.4, linewidth=1)
before_patch = mpatches.Patch(color=GREEN, label='Before intervention')
during_patch = mpatches.Patch(color=GOLD, label='During intervention')
ax.legend(handles=[before_patch, during_patch], fontsize=11)
ax.set_xlabel('Sequencing depth (reads)', fontsize=12)
ax.set_ylabel('Observed ASVs', fontsize=12)
ax.set_title('Rarefaction Curves — 54 Samples (27 Participants x 2 Timepoints)', fontsize=13)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/rarefaction_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print("Rarefaction curve saved")

# ============================================================
# alpha diversity — Shannon, Chao1, Faith's PD
# ============================================================
shannon_values = alpha_diversity('shannon', asv_matrix.values, ids=asv_matrix.index)
chao1_values = alpha_diversity('chao1', asv_matrix.values, ids=asv_matrix.index)
faiths_pd = alpha_diversity('faith_pd', asv_matrix_filtered.values,
                             ids=asv_matrix_filtered.index, tree=tree,
                             taxa=asv_in_tree)

alpha_df = pd.DataFrame({'shannon': shannon_values, 'chao1': chao1_values})
alpha_df['participant'] = alpha_df.index.str.extract(r'(U\d+)')
alpha_df['timepoint'] = ['Before' if 'before' in s else 'During' for s in alpha_df.index]

faiths_df = pd.DataFrame({'faiths_pd': faiths_pd})
faiths_df['participant'] = faiths_df.index.str.extract(r'(U\d+)')
faiths_df['timepoint'] = ['Before' if 'before' in s else 'During' for s in faiths_df.index]

before_shannon = alpha_df[alpha_df['timepoint']=='Before'].set_index('participant')['shannon']
during_shannon = alpha_df[alpha_df['timepoint']=='During'].set_index('participant')['shannon']
before_chao1 = alpha_df[alpha_df['timepoint']=='Before'].set_index('participant')['chao1']
during_chao1 = alpha_df[alpha_df['timepoint']=='During'].set_index('participant')['chao1']
before_fpd = faiths_df[faiths_df['timepoint']=='Before'].set_index('participant')['faiths_pd']
during_fpd = faiths_df[faiths_df['timepoint']=='During'].set_index('participant')['faiths_pd']

_, p_shannon = wilcoxon(before_shannon, during_shannon)
_, p_chao1 = wilcoxon(before_chao1, during_chao1)
_, p_faiths = wilcoxon(before_fpd, during_fpd)

print(f"Shannon p = {p_shannon:.4f}")
print(f"Chao1 p = {p_chao1:.4f}")
print(f"Faith's PD p = {p_faiths:.4f}")

# alpha diversity figures
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
for ax, metric, p_val, label, before_vals, during_vals in zip(
    axes,
    ['shannon', 'chao1', 'faiths_pd'],
    [p_shannon, p_chao1, p_faiths],
    ["Shannon Entropy (H')", 'Chao1 Richness', "Faith's PD"],
    [before_shannon, before_chao1, before_fpd],
    [during_shannon, during_chao1, during_fpd]):
    bp = ax.boxplot([before_vals.values, during_vals.values],
                    patch_artist=True, labels=['Before', 'During'])
    bp['boxes'][0].set_facecolor(GREEN)
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor(GOLD)
    bp['boxes'][1].set_alpha(0.7)
    sig = '*' if p_val < 0.05 else 'ns'
    ax.set_title(f'{label}\np = {p_val:.4f} ({sig})', fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
plt.suptitle('Alpha Diversity — Before vs During Inulin Supplementation (n=27)', fontsize=13)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/alpha_diversity_all_metrics.png', dpi=150, bbox_inches='tight')
plt.close()
print("Alpha diversity figure saved")

# ============================================================
# beta diversity — Weighted UniFrac + PERMDISP
# ============================================================
wu_dm = beta_diversity('weighted_unifrac', asv_matrix_filtered.values,
                        ids=asv_matrix_filtered.index, tree=tree,
                        taxa=asv_in_tree)
wu_pcoa = pcoa(wu_dm)
pc1_var = wu_pcoa.proportion_explained[0] * 100
pc2_var = wu_pcoa.proportion_explained[1] * 100

grouping = pd.Series(
    ['Before' if 'before' in s else 'During' for s in asv_matrix_filtered.index],
    index=asv_matrix_filtered.index, name='timepoint')

permanova_result = permanova(wu_dm, grouping, column='timepoint', permutations=999)
permdisp_result = permdisp(wu_dm, grouping, column='timepoint', permutations=999)
p_permanova = permanova_result['p-value']
p_permdisp = permdisp_result['p-value']
print(f"Weighted UniFrac PERMANOVA p = {p_permanova:.4f}")
print(f"PERMDISP p = {p_permdisp:.4f}")

fig, ax = plt.subplots(figsize=(8, 7))
pc1 = wu_pcoa.samples['PC1']
pc2 = wu_pcoa.samples['PC2']
for sample in asv_matrix_filtered.index:
    color = GREEN if 'before' in sample else GOLD
    ax.scatter(pc1[sample], pc2[sample], c=color, s=60, alpha=0.8,
               edgecolors='white', linewidth=0.5)
before_patch = mpatches.Patch(color=GREEN, label='Before (n=27)')
during_patch = mpatches.Patch(color=GOLD, label='During (n=27)')
ax.legend(handles=[before_patch, during_patch], fontsize=11)
ax.set_xlabel(f'PC1 ({pc1_var:.1f}% variance explained)', fontsize=12)
ax.set_ylabel(f'PC2 ({pc2_var:.1f}% variance explained)', fontsize=12)
ax.set_title(f'Weighted UniFrac PCoA\nPERMANOVA p = {p_permanova:.3f}, PERMDISP p = {p_permdisp:.3f}', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/beta_diversity_weighted_unifrac.png', dpi=150, bbox_inches='tight')
plt.close()
print("Weighted UniFrac PCoA saved")

# ============================================================
# longitudinal butyrate trajectory
# ============================================================
response_colors = {
    'strong_responder': '#1A6B3C',
    'moderate_responder': '#C47F0A',
    'non_responder': '#888888',
    'decreaser': '#C0392B'
}
fig, ax = plt.subplots(figsize=(8, 7))
for participant, row in meta_df.iterrows():
    color = response_colors[row['response']]
    ax.plot([0, 1], [float(row['butyrate_before']), float(row['butyrate_during'])],
            color=color, alpha=0.7, linewidth=1.5, marker='o', markersize=6)
for label, color in response_colors.items():
    ax.plot([], [], color=color, linewidth=2, label=label.replace('_', ' ').title())
ax.set_xticks([0, 1])
ax.set_xticklabels(['Before', 'During'], fontsize=12)
ax.set_ylabel('Butyrate (mmol/kg)', fontsize=12)
ax.set_title('Individual Butyrate Trajectories\nInulin Supplementation (n=27)', fontsize=13)
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/butyrate_trajectory.png', dpi=150, bbox_inches='tight')
plt.close()
print("Butyrate trajectory saved")

# ============================================================
# genus-level preparation
# ============================================================
def get_genus(taxon):
    parts = taxon.split(';')
    for part in parts:
        if 'g__' in part:
            return part.strip().replace('g__', '')
    return 'Unknown'

taxonomy['genus'] = taxonomy['Taxon'].apply(get_genus)
asv_with_genus = asv_table.copy()
asv_with_genus['genus'] = taxonomy['genus']
genus_table = asv_with_genus.groupby('genus').sum()
genus_rel = genus_table.div(genus_table.sum(axis=0), axis=1) * 100
genera_to_remove = ['Chloroplast', 'Unknown', 'uncultured', 'Incertae_Sedis']
genus_rel_clean = genus_rel[~genus_rel.index.isin(genera_to_remove)]
print(f"Genera after cleaning: {genus_rel_clean.shape[0]}")

# ============================================================
# Spearman correlation
# ============================================================
butyrate_change = meta_df['butyrate_change'].astype(float)
genus_change_clean = pd.DataFrame({
    p: genus_rel_clean[f'{p}-during'] - genus_rel_clean[f'{p}-before']
    for p in meta_df.index
})

spearman_results = []
for genus in genus_change_clean.index:
    rho, pval = stats.spearmanr(genus_change_clean.loc[genus], butyrate_change)
    spearman_results.append({'genus': genus, 'rho': rho, 'pval': pval})
spearman_df = pd.DataFrame(spearman_results).sort_values('rho', ascending=False)

top15 = spearman_df.reindex(
    spearman_df['rho'].abs().sort_values(ascending=False).index).head(15)
colors = [GREEN if r > 0 else '#C0392B' for r in top15['rho']]

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(top15['genus'], top15['rho'], color=colors, alpha=0.8)
ax.axvline(x=0, color='black', linewidth=0.8)
ax.set_xlabel("Spearman's rho", fontsize=12)
ax.set_title("Spearman Correlation — Genus Abundance Change vs Butyrate Change\nTop 15 genera (n=27)", fontsize=12)
for i, (_, row) in enumerate(top15.iterrows()):
    if row['pval'] < 0.05:
        ax.text(row['rho'] + 0.01 if row['rho'] > 0 else row['rho'] - 0.01,
                i, '*', ha='center', va='center', fontsize=14)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/spearman_correlation.png', dpi=150, bbox_inches='tight')
plt.close()
print("Spearman correlation saved")

# ============================================================
# PICRUSt2 pathway analysis
# ============================================================
pathway_results = []
for pathway in pathway_abun.index:
    before_vals = [pathway_abun.loc[pathway, f'{p}-before'] for p in meta_df.index]
    during_vals = [pathway_abun.loc[pathway, f'{p}-during'] for p in meta_df.index]
    _, pval = wilcoxon(before_vals, during_vals)
    mean_change = np.mean(np.array(during_vals) - np.array(before_vals))
    pathway_results.append({'pathway': pathway, 'pval': pval, 'mean_change': mean_change})

pathway_results_df = pd.DataFrame(pathway_results).sort_values('pval')
significant_pathways = pathway_results_df[pathway_results_df['pval'] < 0.05].copy()

pathway_descriptions = {
    'PWY-7913': 'Bifidobacterium shunt',
    'PROTOCATECHUATE-ORTHO-CLEAVAGE-PWY': 'Protocatechuate degradation',
    'PWY-4702': 'Phytate degradation',
    'PWY-1861': 'Formaldehyde assimilation',
    'P163-PWY': 'L-glutamate degradation',
    'PWY0-1477': 'Fatty acid beta-oxidation'
}
significant_pathways['description'] = significant_pathways['pathway'].map(
    pathway_descriptions).fillna('Unknown')

colors = [GREEN if c > 0 else '#C0392B' for c in significant_pathways['mean_change']]
labels = [f"{row['pathway']}\n{row['description']}" for _, row in significant_pathways.iterrows()]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(labels, significant_pathways['mean_change'], color=colors, alpha=0.8)
ax.axvline(x=0, color='black', linewidth=0.8)
ax.set_xlabel('Mean pathway abundance change (during minus before)', fontsize=11)
ax.set_title('PICRUSt2 Significant Pathway Changes\nPaired Wilcoxon p < 0.05 (n=27)', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/picrust2_pathway_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("PICRUSt2 pathway analysis saved")

# ============================================================
# Random Forest responder prediction
# ============================================================
baseline_samples = [f'{p}-before' for p in meta_df.index]
X = genus_rel_clean[baseline_samples].T
X.index = meta_df.index
y = meta_df['response']

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)

feature_importance = pd.DataFrame({
    'genus': X.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

top15_rf = feature_importance.head(15)
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(top15_rf['genus'], top15_rf['importance'], color=GREEN, alpha=0.8)
ax.set_xlabel('Feature Importance (Mean Decrease Impurity)', fontsize=12)
ax.set_title('Random Forest Baseline Predictor\nTop 15 Genera by Feature Importance (n=27)', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{EXPORT_DIR}/random_forest_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Random Forest figure saved")

print()
print("=== Step 08 Complete ===")
