# ============================================================
# OgunBiome Insights Pipeline — Snakefile
# Author: Dr. Oluwamayowa Ogun
# Dataset: Baxter et al. 2019 — SRP128128 — Inulin arm
# Framework: DRSWAE — W phase (Workflow)
# ============================================================

configfile: "config/config.yaml"

# ============================================================
# rule all — final targets Snakemake works backward from
# ============================================================
rule all:
    input:
        # Step 0a outputs
        "results/multiqc/ogunbiome_multiqc_report.html",
        # Step 0b outputs
        "results/qiime2/exported/feature-table.tsv",
        "results/qiime2/exported/taxonomy.tsv",
        "results/qiime2/exported/stats.tsv",
        # Step 07 outputs — expanded analysis
        "results/qiime2/exported/alpha_diversity_shannon.png",
        "results/qiime2/exported/beta_diversity_pcoa.png",
        "results/qiime2/exported/volcano_plot_27participants.png",
        "results/qiime2/exported/baseline_responder_comparison.png",
        "results/qiime2/exported/differential_abundance_27participants.csv",
        "results/qiime2/exported/fold_changes_27participants.csv",
        # Step 1 outputs
        "results/quality_check/data_summary.csv",
        "results/quality_check/quality_report.txt",
        # Step 2 outputs
        "results/diversity/abundance_chart.png",
        "results/diversity/top_taxa_plot.png",
        "results/diversity/genus_abundance_summary.csv",
        # Step 3 outputs
        "results/differential_abundance/volcano_plot.png",
        "results/differential_abundance/significant_results.csv",
        # Step 5 outputs
        "results/efsa_mapping/efsa_mapped_results.csv",
        # Step 6 output
        "results/report/OgunBiome_Inulin_Insight_Report.pdf"

# ============================================================
# Step 1 — Quality Check
# ============================================================
rule quality_check:
    input:
        data = config["data"]["input_file"]
    output:
        summary = "results/quality_check/data_summary.csv",
        report  = "results/quality_check/quality_report.txt"
    message:
        "Step 1 — Quality check and data validation"
    shell:
        "python workflow/scripts/01_quality_check.py"

# ============================================================
# Step 2 — Diversity Analysis
# ============================================================
rule diversity_analysis:
    input:
        summary = "results/quality_check/data_summary.csv"
    output:
        chart   = "results/diversity/abundance_chart.png",
        top     = "results/diversity/top_taxa_plot.png",
        genus   = "results/diversity/genus_abundance_summary.csv"
    message:
        "Step 2 — Genus-level community composition analysis"
    shell:
        "python workflow/scripts/02_diversity_analysis.py"

# ============================================================
# Step 3 — Differential Abundance
# ============================================================
rule differential_abundance:
    input:
        summary = "results/quality_check/data_summary.csv"
    output:
        volcano     = "results/differential_abundance/volcano_plot.png",
        significant = "results/differential_abundance/significant_results.csv"
    message:
        "Step 3 — Differential abundance and volcano plot"
    shell:
        "python workflow/scripts/03_deseq2_analysis.py"

# ============================================================
# Step 5 — EFSA Regulatory Biomarker Mapping
# ============================================================
rule efsa_mapping:
    input:
        significant = "results/differential_abundance/significant_results.csv"
    output:
        mapped = "results/efsa_mapping/efsa_mapped_results.csv"
    message:
        "Step 5 — EFSA regulatory biomarker mapping"
    shell:
        "python workflow/scripts/04_efsa_mapper.py"

# ============================================================
# Step 6 — Report Generation
# ============================================================
rule generate_report:
    input:
        significant    = "results/differential_abundance/significant_results.csv",
        efsa_mapped    = "results/efsa_mapping/efsa_mapped_results.csv",
        abundance_chart = "results/diversity/abundance_chart.png",
        volcano        = "results/differential_abundance/volcano_plot.png"
    output:
        pdf = "results/report/OgunBiome_Inulin_Insight_Report.pdf"
    message:
        "Step 6 — Generating OgunBiome PDF report"
    shell:
        "python workflow/scripts/05_report_generator.py"

# ============================================================
# Step 0a — Raw Data Download and Quality Assessment
# ============================================================
rule download_and_qc:
    output:
        multiqc = "results/multiqc/ogunbiome_multiqc_report.html"
    message:
        "Step 0a — Downloading raw FASTQ files and running FastQC/MultiQC"
    shell:
        "bash workflow/scripts/00a_download_qc.sh"

# ============================================================
# Step 0b — DADA2 Amplicon Processing via QIIME2
# ============================================================
rule dada2_processing:
    input:
        multiqc    = "results/multiqc/ogunbiome_multiqc_report.html",
        manifest   = "data/manifest.tsv",
        classifier = "results/qiime2/silva-138-classifier.qza"
    output:
        table    = "results/qiime2/exported/feature-table.tsv",
        taxonomy = "results/qiime2/exported/taxonomy.tsv",
        stats    = "results/qiime2/exported/stats.tsv"
    message:
        "Step 0b — DADA2 denoising and taxonomy assignment via QIIME2"
    shell:
        "bash workflow/scripts/00b_dada2_pipeline.sh"

# ============================================================
# Step 07 — Expanded DADA2 Analysis
# ============================================================
rule expanded_analysis:
    input:
        table    = "results/qiime2/exported/feature-table.tsv",
        taxonomy = "results/qiime2/exported/taxonomy.tsv",
        stats    = "results/qiime2/exported/stats.tsv"
    output:
        alpha    = "results/qiime2/exported/alpha_diversity_shannon.png",
        beta     = "results/qiime2/exported/beta_diversity_pcoa.png",
        volcano  = "results/qiime2/exported/volcano_plot_27participants.png",
        baseline = "results/qiime2/exported/baseline_responder_comparison.png",
        diff_ab  = "results/qiime2/exported/differential_abundance_27participants.csv",
        fc       = "results/qiime2/exported/fold_changes_27participants.csv"
    message:
        "Step 07 — Expanded analysis: alpha/beta diversity, differential abundance, responder comparison"
    shell:
        "python workflow/scripts/07_expanded_analysis.py"
