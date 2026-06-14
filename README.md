# OgunBiome Insights Pipeline

**End-to-end reproducible microbiome analytics pipeline — from raw FASTQ sequencing data to automated analytical report.**

---

## Overview

This pipeline demonstrates complete computational biology workflow development for clinical microbiome data analysis. Starting from raw paired-end FASTQ files deposited in NCBI SRA, the pipeline performs raw data quality assessment, ASV-level amplicon denoising via DADA2, taxonomy assignment, community composition analysis, differential abundance testing, functional pathway profiling, regulatory biomarker mapping, and automated PDF report generation.

Built in Python and Bash, orchestrated with Snakemake, the pipeline follows the DRSWAE framework — Data, Reproducibility, Scripting, Workflow, Analysis, Execution — ensuring reproducibility, traceability, and scientific rigour at every stage. Development principles are consistent with translational and regulated research environments including pre-IND computational documentation standards.

---

## Dataset

**Baxter NT et al. (2019).** Dynamics of Human Gut Microbiota and Short-Chain Fatty Acids in Response to Dietary Interventions with Three Fermentable Fibers. *mBio* 10:e02566-18. NCBI SRA: SRP128128.

Study design: Randomised controlled trial. 174 healthy adults. Four dietary intervention arms — chicory-derived inulin, resistant potato starch, resistant maize starch, and accessible starch control. Two-week intervention period. Paired-end 16S rRNA amplicon sequencing (V4 region, 515F/806R primers, Illumina MiSeq 2x250bp) of stool samples collected before and during intervention.

Pipeline focus: Inulin arm. Complete wint17 semester cohort — 27 participants, 54 samples, paired before and during timepoints, complete butyrate SCFA measurements available. Single semester restricts analysis to one sequencing batch — no batch correction required.

---

## Pipeline Architecture

Two analytical streams orchestrated as a Snakemake DAG.

---

### Stream 1 — Validation Analysis (Steps 1-6)

Applied to the Baxter et al. 2019 pre-processed summary table — fold changes and adjusted p-values computed by the original authors using mothur OTU clustering across all 174 participants. This stream validates published findings and produces the automated PDF report with EFSA regulatory biomarker mapping.

**Step 1 — Quality Check**
Load and validate pre-processed input table. Verify column integrity. Identify significant taxa at FDR < 0.05 and FC >= 1.5. Output: data_summary.csv, quality_report.txt

**Step 2 — Diversity Analysis**
Genus-level aggregation. Community composition visualisation before vs during intervention. Output: abundance_chart.png, top_taxa_plot.png

**Step 3 — Differential Abundance**
Log2 fold change and -log10 adjusted p-value calculation. Volcano plot production. Output: volcano_plot.png, significant_results.csv

**Step 4 — Biological Interpretation**
Expert narrative connecting findings to mechanism, health relevance, and regulatory context. Written by Dr. Ogun.

**Step 5 — Regulatory Biomarker Mapping**
Structured mapping of significant taxa against EFSA scientific opinions. Relevance tiers: HIGH / MODERATE / SUPPORTING. Output: efsa_mapped_results.csv

**Step 6 — Report Generation**
Automated PDF assembly of all pipeline outputs using ReportLab. Output: OgunBiome_Inulin_Insight_Report.pdf

---

### Stream 2 — De Novo DADA2 Reanalysis (Steps 0a, 0b, 07, 08)

Applied to raw paired-end FASTQ files for the complete wint17 inulin cohort — 27 participants, 54 samples — downloaded directly from NCBI SRA. This stream independently reproduces and extends the Stream 1 findings at ASV resolution from raw sequencing data.

**Step 0a — Raw Data Download and Quality Assessment**
54 paired-end FASTQ files downloaded from NCBI SRA (SRP128128) via fasterq-dump. FastQC v0.12.1 quality assessment on all 108 files. MultiQC 1.35 aggregation across samples. Truncation lengths determined from per-base quality profiles — trunc_len_f=230, trunc_len_r=200 — confirmed consistent across all 27 participants. Output: FastQC reports, MultiQC HTML report.

**Step 0b — DADA2 Amplicon Processing via QIIME2**
QIIME2 2024.10 pipeline — paired-end manifest import, Cutadapt primer trimming (515F/806R), DADA2 1.30.0 paired-end denoising, SILVA 138 taxonomy assignment (human stool weighted naive Bayes classifier, sklearn 1.4.2, confidence 0.7). 882 ASVs detected across 54 samples. All 54 samples pass QC (67-95% non-chimeric read retention). QIIME2 automatic provenance tracking satisfies computational traceability requirements for regulatory submissions. Output: ASV count table, taxonomy table, denoising statistics.

**Step 07 — Expanded Diversity and Differential Abundance**
Alpha diversity — Shannon entropy, Chao1 richness, Faith's phylogenetic diversity. Beta diversity — Bray-Curtis and Weighted UniFrac PCoA, PERMANOVA, PERMDISP. Differential abundance — paired Wilcoxon signed-rank test across 149 genera. Responder vs non-responder comparison based on butyrate SCFA change. Individual butyrate trajectory visualisation. Output: 8 figures, 4 CSV files.

**Step 08 — PICRUSt2 Functional Profiling and Extended Analysis**
PICRUSt2 2.6.3 functional pathway prediction — EPA-ng phylogenetic placement of 882 ASVs onto 26,868-organism reference tree, hidden state prediction via castor, MetaCyc pathway inference via MinPath. Rarefaction curves confirming sequencing depth sufficiency. Spearman correlation between genus abundance change and butyrate change. LEfSe biomarker discovery. PICRUSt2 MetaCyc pathway analysis. Random Forest responder prediction from baseline genus abundances. Output: 7 figures.

---

## Key Findings

### Stream 1 — Validation Analysis (Pre-processed OTU data, n=174)

Significant genera at FDR < 0.05 and fold change >= 1.5:

| Genus | Fold Change | Adj. P-value | EFSA Tier |
|-------|-------------|--------------|-----------|
| *Bifidobacterium* | 3.54x | 0.0022 | HIGH |
| *Anaerostipes* | 2.16x | 0.0001 | MODERATE |

### Stream 2 — De Novo DADA2 Reanalysis (ASV-level, n=27)

| Analysis | Result |
|----------|--------|
| Shannon entropy | Significant decrease p=0.0229 |
| Chao1 richness | Not significant p=0.0625 |
| Faith's PD | Not significant p=0.0772 |
| Bray-Curtis PERMANOVA | Not significant p=0.999 |
| Weighted UniFrac PERMANOVA | Not significant p=0.747 |
| PERMDISP | Not significant p=0.832 |
| Anaerostipes Wilcoxon | 2.19x enrichment, raw p=0.0009 |
| Bifidobacterium Wilcoxon | 1.73x enrichment, raw p=0.024 |
| Spearman top hit | Fusicatenibacter rho=0.484, p=0.010 |
| Anaerostipes Spearman | rho=0.398, p=0.040 |
| PICRUSt2 significant pathways | 6 pathways at p < 0.05 |
| LEfSe biomarker | Intestinibacter depleted during intervention |
| Random Forest top predictor | Monoglobus baseline abundance |

**Butyrate response distribution across 27 participants:**

| Response | n | Butyrate change |
|----------|---|-----------------|
| Strong responder | 6 | > +10 mmol/kg |
| Moderate responder | 10 | +3 to +10 mmol/kg |
| Non-responder | 9 | < 3 mmol/kg change |
| Decreaser | 2 | Butyrate decreased |

Both streams confirm the inulin -> Bifidobacterium -> acetate -> Anaerostipes -> butyrate cascade — validated at OTU level (n=174) and independently at ASV level (n=27) from raw sequencing data.

Full methodological details and per-participant results: VALIDATION.md

---

## How to Run

Prerequisites: Anaconda or Miniconda. Git.

```bash
# Clone repository
git clone https://github.com/Mayorcool-lab/ogunbiome-Insight-pipeline.git
cd ogunbiome-Insight-pipeline

# Create ogunbiome environment
conda env create -f environment.yml
conda activate ogunbiome
python -m ipykernel install --user --name ogunbiome --display-name "Python (ogunbiome)"

# Create QIIME2 environment (required for Steps 0a and 0b)
conda env create -n qiime2-amplicon -f envs/qiime2.yaml

# Run full pipeline
snakemake --cores 4 --use-conda

# Run Stream 1 only — Steps 1-6 using pre-processed data
snakemake --cores 1

# Visualise DAG
snakemake --dag | dot -Tpdf > results/pipeline_dag.pdf
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11, Bash |
| Amplicon processing | QIIME2 2024.10, DADA2 1.30.0 |
| Taxonomy | SILVA 138, scikit-learn 1.4.2 |
| Quality assessment | FastQC 0.12.1, MultiQC 1.35 |
| SRA download | SRA Toolkit 3.4.1 (fasterq-dump) |
| Functional profiling | PICRUSt2 2.6.3 |
| Data manipulation | pandas, numpy |
| Visualisation | matplotlib, seaborn |
| Statistical analysis | scipy, scikit-bio, statsmodels |
| Machine learning | scikit-learn |
| Report generation | ReportLab |
| Pipeline orchestration | Snakemake 9.19.0 |
| Environment management | Conda |
| Version control | Git / GitHub |

---

## Reproducibility Standards

- All parameters centralised in config/config.yaml — no hardcoding anywhere
- Full version control with meaningful commit history documenting every analytical decision
- Conda environment specifications for exact package reproducibility
- Snakemake DAG ensuring deterministic execution order and fail-fast behaviour
- QIIME2 automatic provenance tracking — every step records inputs, outputs, parameters, and software versions
- VALIDATION.md documenting independent reproduction of published findings across two analytical streams
- Jupyter notebooks providing interactive audit trail of analytical decisions
- Principles consistent with pre-IND computational documentation standards (EMA/BfArM traceability requirements)

---

## Author

Dr. Oluwamayowa Ogun
Computational Biologist | CAU Kiel
PhD — Faculty of Agricultural and Nutritional Sciences (AEF), CAU Kiel (2023)
Specialisation: Computational biology, gut microbiome analytics, glyco-enzyme biology, translational science.
GitHub: https://github.com/Mayorcool-lab
LinkedIn: https://www.linkedin.com/in/oluwamayowaogun

---

Analysis performed on publicly available data: Baxter et al. 2019, mBio. Pipeline developed April-June 2026.
