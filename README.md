# Microbiome Analytics Pipeline

**Reproducible bioinformatics pipeline for gut microbiota analysis applied to a human dietary intervention RCT.**

---

## Overview

This repository demonstrates end-to-end computational biology workflow development for microbiome data analysis. The pipeline processes 16S rRNA amplicon sequencing data from a published randomised controlled trial, performing quality control, community composition analysis, differential abundance testing, regulatory biomarker mapping, and automated report generation.

Built entirely in Python and orchestrated with Snakemake, the pipeline follows the DRSWAE framework — Data, Reproducibility, Scripting, Workflow, Analysis, Execution — ensuring reproducibility, traceability, and scientific rigour at every stage. Development principles are consistent with translational and regulated research environments.

---

## Dataset

**Baxter NT et al. (2019).** Dynamics of Human Gut Microbiota and Short-Chain Fatty Acids in Response to Dietary Interventions with Three Fermentable Fibers. *mBio* 10:e02566-18. NCBI SRA: SRP128128.

Study design: Randomised controlled trial. 174 healthy adults. Four dietary intervention arms including chicory-derived inulin supplementation. Two-week intervention period. 16S rRNA amplicon sequencing of stool samples collected before and during intervention.

---

## Pipeline Architecture

Six analytical steps orchestrated as a Snakemake DAG:

- Step 1 — Quality Check: Load and validate input data. Verify column integrity. Identify significant taxa at FDR < 0.05 and FC >= 1.5. Output: data_summary.csv, quality_report.txt
- Step 2 — Diversity Analysis: Genus-level aggregation. Community composition visualisation — before vs during intervention. Output: abundance_chart.png, top_taxa_plot.png, genus_abundance_summary.csv
- Step 3 — Differential Abundance: Log2 fold change and -log10 adjusted p-value calculation. Volcano plot production. Output: volcano_plot.png, significant_results.csv
- Step 4 — Biological Interpretation: Expert narrative connecting findings to mechanism, health relevance, and regulatory context. Output: interpretation_text.py
- Step 5 — Regulatory Biomarker Mapping: Structured mapping of significant taxa against EFSA scientific opinions. Relevance tiers: HIGH / MODERATE / SUPPORTING. Output: efsa_mapped_results.csv
- Step 6 — Report Generation: Automated PDF assembly of all pipeline outputs using ReportLab.

The complete pipeline DAG is available at results/pipeline_dag.pdf.

---

## Key Findings

The pipeline identified two genera as statistically significant responders to inulin supplementation (FDR < 0.05):

| Genus | Fold Change | Adj. P-value | Regulatory Tier |
|-------|-------------|--------------|-----------------|
| *Bifidobacterium* | 3.54x | 0.0022 | HIGH |
| *Anaerostipes* | 2.16x | 0.0001 | MODERATE |

The co-enrichment of Bifidobacterium — the primary inulin fermenter via beta-fructosidase activity — and Anaerostipes — a cross-feeding butyrate producer — confirms the complete inulin-Bifidobacterium-acetate-Anaerostipes-butyrate cascade operating in vivo.

These findings independently reproduce the published results of Baxter et al. 2019, confirming pipeline analytical validity. Full validation statement: VALIDATION.md.

---

## Repository Structure
---

## How to Run

Prerequisites: Anaconda or Miniconda. Git.

```bash
git clone https://github.com/Mayorcool-lab/ogunbiome-mvp-pipeline.git
cd ogunbiome-mvp-pipeline
conda env create -f environment.yml
conda activate ogunbiome
python -m ipykernel install --user --name ogunbiome --display-name "Python (ogunbiome)"
snakemake --cores 1
```

Visualise the DAG:

```bash
snakemake --dag | dot -Tpdf > results/pipeline_dag.pdf
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Data manipulation | pandas, numpy |
| Visualisation | matplotlib, seaborn |
| Statistical analysis | scipy |
| Microbiome analysis | scikit-bio |
| Report generation | ReportLab |
| Pipeline orchestration | Snakemake |
| Environment management | Conda |
| Version control | Git / GitHub |

---

## Reproducibility Standards

- All parameters centralised in config/config.yaml — no hardcoding
- Full version control with meaningful commit history
- Conda environment specification for exact package reproducibility
- Snakemake DAG ensuring deterministic execution order
- VALIDATION.md documenting independent reproduction of published findings
- Jupyter notebooks providing interactive audit trail of analytical decisions

---

## Author

Dr. Oluwamayowa Ogun
Computational Biologist | CAU Kiel
PhD — Faculty of Agricultural and Nutritional Sciences (AEF), CAU Kiel (2023)
Specialisation: Computational biology, gut microbiome analytics, glyco-enzyme biology, dietary intervention science.
GitHub: https://github.com/Mayorcool-lab

---

Analysis performed on publicly available data: Baxter et al. 2019, mBio.
Pipeline developed at CAU Kiel, April 2026.
