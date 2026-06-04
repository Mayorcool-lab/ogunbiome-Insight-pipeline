# OgunBiome Insights Pipeline

**End-to-end reproducible microbiome analytics pipeline - from raw FASTQ sequencing data to automated analytical report.**

---

## Overview

This pipeline demonstrates complete computational biology workflow development for clinical microbiome data analysis. Starting from raw paired-end FASTQ files deposited in NCBI SRA, the pipeline performs raw data quality assessment, ASV-level amplicon denoising via DADA2, taxonomy assignment, community composition analysis, differential abundance testing, regulatory biomarker mapping, and automated PDF report generation.

Built in Python and Bash, orchestrated with Snakemake, the pipeline follows the DRSWAE framework - Data, Reproducibility, Scripting, Workflow, Analysis, Execution - ensuring reproducibility, traceability, and scientific rigour at every stage. Development principles are consistent with translational and regulated research environments including pre-IND computational documentation standards.

---

## Dataset

**Baxter NT et al. (2019).** Dynamics of Human Gut Microbiota and Short-Chain Fatty Acids in Response to Dietary Interventions with Three Fermentable Fibers. *mBio* 10:e02566-18. NCBI SRA: SRP128128.

Study design: Randomised controlled trial. 174 healthy adults. Four dietary intervention arms - chicory-derived inulin, resistant potato starch (RPS), resistant maize starch (RMS), and accessible starch control. Two-week intervention period. Paired-end 16S rRNA amplicon sequencing (V4 region, 515F/806R primers, Illumina MiSeq 2x250bp) of stool samples collected before and during intervention.

Pipeline focus: Inulin arm. 10 samples selected - 5 participants (U338, U328, U331, U317, U336), paired before and during timepoints, wint17 semester, complete SCFA measurements available.

---

## Pipeline Architecture

Eight analytical steps orchestrated as a Snakemake DAG:

**Step 0a - Raw Data Download and QC**
10 paired-end FASTQ files downloaded from NCBI SRA (SRP128128) via fasterq-dump. FastQC v0.12.1 quality assessment on all 20 files. MultiQC 1.35 aggregation across samples. Truncation lengths determined from per-base quality profiles - trunc_len_f=230, trunc_len_r=200. Output: FastQC reports, MultiQC HTML report.

**Step 0b - DADA2 Amplicon Processing via QIIME2**
QIIME2 2024.10 pipeline - paired-end manifest import, Cutadapt primer trimming (515F/806R), DADA2 1.30.0 paired-end denoising, SILVA 138 taxonomy assignment (human stool weighted naive Bayes classifier, sklearn 1.4.2, confidence 0.7). 279 ASVs detected. All 10 samples pass QC (69-90% non-chimeric read retention). QIIME2 automatic provenance tracking satisfies computational traceability requirements for regulatory submissions. Output: ASV count table, taxonomy table, denoising statistics.

**Step 1 - Quality Check**
Load and validate input data. Verify column integrity. Identify significant taxa at FDR < 0.05 and FC >= 1.5. Output: data_summary.csv, quality_report.txt

**Step 2 - Diversity Analysis**
Genus-level aggregation. Community composition visualisation before vs during intervention. Output: abundance_chart.png, top_taxa_plot.png, genus_abundance_summary.csv

**Step 3 - Differential Abundance**
Log2 fold change and -log10 adjusted p-value calculation. Volcano plot production. Output: volcano_plot.png, significant_results.csv

**Step 4 - Biological Interpretation**
Expert narrative connecting findings to mechanism, health relevance, and regulatory context. Written by Dr. Ogun.

**Step 5 - Regulatory Biomarker Mapping**
Structured mapping of significant taxa against EFSA scientific opinions. Relevance tiers: HIGH / MODERATE / SUPPORTING. Output: efsa_mapped_results.csv

**Step 6 - Report Generation**
Automated PDF assembly of all pipeline outputs using ReportLab. Output: OgunBiome_Inulin_Insight_Report.pdf

---

## Key Findings

### Original Analysis (Pre-processed OTU data, n=174)

Significant genera identified at FDR < 0.05 and fold change >= 1.5:

| Genus | Fold Change | Adj. P-value | Regulatory Tier |
|-------|-------------|--------------|-----------------|
| *Bifidobacterium* | 3.54x | 0.0022 | HIGH |
| *Anaerostipes* | 2.16x | 0.0001 | MODERATE |

### DADA2 Raw Data Reanalysis (ASV-level, n=5)

Independent reanalysis from raw FASTQ files confirms the biological direction:

| Genus | DADA2 mean FC | Original OTU FC | Direction preserved |
|-------|---------------|-----------------|---------------------|
| *Bifidobacterium* | 2.34x | 3.54x | Yes (4/5 participants) |
| *Anaerostipes* | 3.02x | 2.16x | Yes (5/5 participants) |

The co-enrichment of Bifidobacterium - the primary inulin fermenter via beta-fructosidase activity - and Anaerostipes - a cross-feeding butyrate producer via acetate-CoA transferase - confirms the complete inulin -> Bifidobacterium -> acetate -> Anaerostipes -> butyrate cascade at ASV resolution from raw sequencing data.

Full methodological comparison and per-participant fold changes: VALIDATION.md.

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

# Run full pipeline - Steps 0a through 6
snakemake --cores 4 --use-conda

# Run downstream analysis only - Steps 1-6 using pre-processed data
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
| Data manipulation | pandas, numpy |
| Visualisation | matplotlib, seaborn |
| Statistical analysis | scipy |
| Microbiome analysis | scikit-bio |
| Report generation | ReportLab |
| Pipeline orchestration | Snakemake 9.19.0 |
| Environment management | Conda |
| Version control | Git / GitHub |

---

## Reproducibility Standards

- All parameters centralised in config/config.yaml - no hardcoding anywhere
- Full version control with meaningful commit history documenting every analytical decision
- Conda environment specifications for exact package reproducibility
- Snakemake DAG ensuring deterministic execution order and fail-fast behaviour
- QIIME2 automatic provenance tracking - every step records inputs, outputs, parameters, and software versions
- VALIDATION.md documenting independent reproduction of published findings with per-participant fold change comparison between OTU and ASV approaches
- Jupyter notebooks providing interactive audit trail of analytical decisions
- Principles consistent with pre-IND computational documentation standards (EMA/BfArM traceability requirements)

---

## Author

Dr. Oluwamayowa Ogun
Computational Biologist | CAU Kiel
PhD - Faculty of Agricultural and Nutritional Sciences (AEF), CAU Kiel (2023)
Specialisation: Computational biology, gut microbiome analytics, glyco-enzyme biology, translational science.
GitHub: https://github.com/Mayorcool-lab
LinkedIn: https://www.linkedin.com/in/oluwamayowaogun

---

Analysis performed on publicly available data: Baxter et al. 2019, mBio. Pipeline developed April-June 2026.
