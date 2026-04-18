# OgunBiome Insights — MVP Pipeline

**Translating microbiome data into actionable gut health insights for the food and ingredient industry.**

---

## What Is OgunBiome Insights?

Food and ingredient companies increasingly run microbiome studies to demonstrate that their products support gut health. The challenge is not generating the data — it is interpreting it. Complex sequencing outputs require specialist bioinformatics expertise, biological domain knowledge, and regulatory awareness that most food companies do not have in-house.

OgunBiome Insights solves this problem. We take raw microbiome study data and return a professionally formatted biological interpretation report — within days, at a fraction of traditional consultancy cost, with findings mapped directly to EFSA health claim evidence standards.

Every report is produced by an automated analytical pipeline and reviewed by Dr. Oluwamayowa Ogun (PhD, CAU Kiel) before delivery. The pipeline provides the speed. The PhD provides the credibility.

---

## The Business Case

The European prebiotic and probiotic ingredient market exceeded €4 billion in 2024 and continues to grow. Food companies investing in gut health product development need two things simultaneously — scientific evidence that their ingredients work, and regulatory-aware interpretation of that evidence for EFSA health claim substantiation.

Current options are expensive specialist consultancies charging €500-1,000 per hour, slow manual interpretation taking weeks, and no standardised framework connecting microbiome findings to EFSA regulatory evidence.

OgunBiome Insights delivers the same quality of interpretation faster, more consistently, and at a price point accessible to mid-size food ingredient companies. Every report connects microbiome findings directly to specific EFSA scientific opinions — telling clients not just what changed in the microbiome but whether those changes are regulatorily defensible in Europe.

---

## The Founding Team

**Dr. Oluwamayowa Ogun** — Computational Biologist | CAU Kiel
PhD from the Faculty of Agricultural and Nutritional Sciences (AEF), CAU Kiel (2023). Specialisation in computational biology with expertise in gut microbiome data analysis, glyco-enzyme biology, structural bioinformatics, and dietary intervention science. Four peer-reviewed publications. The AEF mandate — connecting agricultural production, food processing, and human nutrition across the full value chain — is the scientific foundation on which OgunBiome is built. Responsible for pipeline architecture, biological interpretation, and scientific leadership.

**Oluwatimilehin Sarah Ogun** — Co-Founder | Food Business & Industry Relations
MSc International Food Business and Consumer Studies (University of Kassel / Hochschule Fulda). BSc Food Technology. International Customer Service Consultant in the food ingredient industry with direct commercial relationships with European food ingredient manufacturers. Responsible for business development, client relations, and market strategy.

---

## What This Pipeline Demonstrates

This repository contains the OgunBiome MVP Pipeline — an end-to-end automated microbiome data analysis system demonstrated on a published human dietary intervention dataset.

**Dataset:** Baxter NT et al. (2019). Dynamics of Human Gut Microbiota and Short-Chain Fatty Acids in Response to Dietary Interventions with Three Fermentable Fibers. mBio 10:e02566-18. NCBI SRA: SRP128128.

The dataset is a randomised controlled trial of chicory-derived inulin supplementation in 174 healthy adults — the same prebiotic compound class used in commercial gut health products. The pipeline independently reproduces the published finding of significant Bifidobacterium and Anaerostipes enrichment, validating the analytical approach.

---

## Pipeline Architecture

The pipeline follows the DRSWAE framework — Data, Reproducibility, Scripting, Workflow, Analysis, Execution — and consists of six analytical steps:

Step 1 — Quality Check
Load and validate input data. Identify significant taxa at FDR < 0.05.
Output: data_summary.csv, quality_report.txt

Step 2 — Diversity Analysis
Genus-level aggregation. Community composition visualisation.
Output: abundance_chart.png, top_taxa_plot.png, genus_abundance_summary.csv

Step 3 — Differential Abundance
Volcano plot production. Significant results table.
Output: volcano_plot.png, significant_results.csv

Step 4 — Biological Interpretation
Expert narrative by Dr. Ogun connecting findings to mechanism,
health relevance, and EFSA regulatory context.
Output: interpretation_text.py

Step 5 — EFSA Biomarker Mapping
Structured mapping of significant taxa against EFSA scientific opinions.
Relevance tiers: HIGH / MODERATE / SUPPORTING.
Output: efsa_mapped_results.csv

Step 6 — Report Generation
Automated assembly of all outputs into a branded PDF client report.
Output: OgunBiome_Inulin_Insight_Report.pdf

The complete pipeline DAG is available at results/pipeline_dag.pdf.

---

## Key Findings — Inulin Intervention

The pipeline identified two genera as statistically significant responders to chicory-derived inulin supplementation (FDR < 0.05):

Genus            | Fold Change | Adj. P-value | EFSA Tier
-----------------|-------------|--------------|----------
Bifidobacterium  | 3.54x       | 0.0022       | HIGH
Anaerostipes     | 2.16x       | 0.0001       | MODERATE

Bifidobacterium enrichment is directly cited in EFSA Opinion EFSA-Q-2013-00341 as an indicator of prebiotic activity following inulin-type fructan consumption. Anaerostipes enrichment reflects cross-feeding interactions producing butyrate — recognised by EFSA as a functional indicator of colonic health.

These findings reproduce the published results of Baxter et al. 2019, confirming analytical validity. Full validation statement: VALIDATION.md.

---

## Repository Structure

ogunbiome-mvp-pipeline/
├── config/config.yaml                         # Central pipeline configuration
├── data/baxter2019_inulin_intervention.xlsx   # Input dataset
├── notebooks/                                 # Interactive exploration notebooks
├── resources/efsa_biomarker_database.csv      # EFSA biomarker reference database
├── results/                                   # All pipeline outputs
├── workflow/scripts/                          # All pipeline scripts
├── Snakefile                                  # Pipeline orchestration
├── environment.yml                            # Conda environment specification
└── README.md                                  # This file

---

## How to Run the Pipeline

Prerequisites: Anaconda or Miniconda installed, Git installed.

Setup:

git clone https://github.com/Mayorcool-lab/ogunbiome-mvp-pipeline.git
cd ogunbiome-mvp-pipeline
conda env create -f environment.yml
conda activate ogunbiome
python -m ipykernel install --user --name ogunbiome --display-name "Python (ogunbiome)"

Run the complete pipeline:

snakemake --cores 1

One command. The complete pipeline runs from raw data to PDF report automatically.

View the report:

results/report/OgunBiome_Inulin_Insight_Report.pdf

Visualise the pipeline DAG:

snakemake --dag | dot -Tpdf > results/pipeline_dag.pdf

---

## Technology Stack

Component            | Technology
---------------------|------------------
Language             | Python 3.11
Data manipulation    | pandas, numpy
Visualisation        | matplotlib, seaborn
Statistical analysis | scipy
Microbiome analysis  | scikit-bio
Report generation    | ReportLab
Pipeline orchestration | Snakemake
Environment management | Conda
Version control      | Git / GitHub

---

## The OgunBiome Service — What Clients Receive

A complete OgunBiome Insights report contains:

- Executive summary in plain scientific language
- Community composition visualisations
- Differential abundance analysis with volcano plot
- Expert biological interpretation by Dr. Ogun
- EFSA biomarker mapping with relevance tiers and opinion citations
- Conclusion connecting findings to health claim substantiation strategy

Delivered within 48 hours of data receipt. Priced to be accessible to mid-size food ingredient companies that cannot afford traditional consultancy rates.

---

## Development Status

This pipeline is being developed at CAU Kiel under the EXIST Grundungsstipendium programme. The MVP demonstrates the complete analytical workflow on a published public dataset. Commercial deployment is planned for Q3 2026.

---

## Contact

Dr. Oluwamayowa Ogun
Computational Biologist | OgunBiome Insights | CAU Kiel
GitHub: https://github.com/Mayorcool-lab

---

OgunBiome Insights — Kiel, Germany — April 2026
Demonstration analysis performed on publicly available data (Baxter et al. 2019, mBio).
This repository is part of an EXIST Grundungsstipendium application at CAU Kiel.
