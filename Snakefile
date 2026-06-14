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
        # Step 08 outputs — PICRUSt2 functional profiling and extended diversity
        "results/qiime2/exported/rarefaction_curve.png",
        "results/qiime2/exported/alpha_diversity_all_metrics.png",
        "results/qiime2/exported/beta_diversity_weighted_unifrac.png",
        "results/qiime2/exported/butyrate_trajectory.png",
        "results/qiime2/exported/spearman_correlation.png",
        "results/qiime2/exported/picrust2_pathway_analysis.png",
        "results/qiime2/exported/random_forest_importance.png",
        # Step 1 outputs
        "results/quality_check/data_summary.csv",
        "results/quality_check/quality_report.txt",
        # Step 2 outputs
        "results/diversity/abundance_chart.png",
        "results/diversity/top_taxa_plot.png",
        # Step 3 outputs
        "results/differential_abundance/significant_results.csv",
        "results/differential_abundance/all_results.csv",
        "results/differential_abundance/volcano_plot.png",
        # Step 5 outputs
        "results/efsa_mapping/efsa_mapped_results.csv",
        # Step 6 outputs
        "results/report/OgunBiome_Inulin_Insight_Report.pdf"
# ============================================================
# Step 1 — Quality Check
# ============================================================
rule quality_check:
    input:
        data = config["data"]["input_file"]
    output:
        summary = config["output"]["quality_check"]["summary"],
        report  = config["output"]["quality_check"]["report"]
    message:
        "Step 1 — Quality check and data validation"
    shell:
        "python workflow/scripts/01_quality_check.py"
# ============================================================
# Step 2 — Diversity Analysis
# ============================================================
rule diversity_analysis:
    input:
        summary = config["output"]["quality_check"]["summary"]
    output:
        abundance = config["output"]["diversity"]["abundance_chart"],
        top_taxa  = config["output"]["diversity"]["top_taxa_plot"]
    message:
        "Step 2 — Diversity analysis and community composition"
    shell:
        "python workflow/scripts/02_diversity_analysis.py"
# ============================================================
# Step 3 — Differential Abundance
# ============================================================
rule differential_abundance:
    input:
        abundance = config["output"]["diversity"]["abundance_chart"]
    output:
        significant = config["output"]["differential"]["significant"],
        all_results = config["output"]["differential"]["all_results"],
        volcano     = config["output"]["differential"]["volcano"]
    message:
        "Step 3 — Differential abundance analysis"
    shell:
        "python workflow/scripts/03_deseq2_analysis.py"
# ============================================================
# Step 5 — EFSA Regulatory Biomarker Mapping
# ============================================================
rule efsa_mapping:
    input:
        significant = config["output"]["differential"]["significant"]
    output:
        mapped = config["output"]["efsa"]["mapped"]
    message:
        "Step 5 — EFSA regulatory biomarker mapping"
    shell:
        "python workflow/scripts/04_efsa_mapper.py"
# ============================================================
# Step 6 — Report Generation
# ============================================================
rule report_generation:
    input:
        mapped = config["output"]["efsa"]["mapped"]
    output:
        pdf = config["output"]["report"]["pdf"]
    message:
        "Step 6 — Automated PDF report generation"
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
# ============================================================
# Step 08 — PICRUSt2 Functional Profiling and Extended Diversity
# ============================================================
rule picrust2_analysis:
    input:
        table    = "results/qiime2/exported/feature-table.tsv",
        taxonomy = "results/qiime2/exported/taxonomy.tsv",
        pathways = "results/picrust2/path_abun_unstrat.tsv.gz",
        tree     = "results/picrust2/bac_reduced.tre"
    output:
        rarefaction = "results/qiime2/exported/rarefaction_curve.png",
        alpha_all   = "results/qiime2/exported/alpha_diversity_all_metrics.png",
        unifrac     = "results/qiime2/exported/beta_diversity_weighted_unifrac.png",
        trajectory  = "results/qiime2/exported/butyrate_trajectory.png",
        spearman    = "results/qiime2/exported/spearman_correlation.png",
        pathways    = "results/qiime2/exported/picrust2_pathway_analysis.png",
        rf          = "results/qiime2/exported/random_forest_importance.png"
    message:
        "Step 08 — PICRUSt2 functional profiling, Faith PD, Weighted UniFrac, Spearman, Random Forest"
    shell:
        "python workflow/scripts/08_picrust2_analysis.py"
