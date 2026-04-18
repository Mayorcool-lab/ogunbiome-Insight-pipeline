# ============================================================
# OgunBiome MVP Pipeline — Snakefile
# Author: Dr. Oluwamayowa Ogun — OgunBiome Insights — CAU Kiel
# Dataset: Baxter et al. 2019 — mBio — SRP128128
# Run: snakemake --cores 1
# DAG: snakemake --dag | dot -Tpdf > pipeline_dag.pdf
# ============================================================

configfile: "config/config.yaml"

rule all:
    input:
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


rule quality_check:
    input:
        data = config["data"]["input_file"]
    output:
        summary = "results/quality_check/data_summary.csv",
        report  = "results/quality_check/quality_report.txt"
    message:
        "Step 1 — Running quality check on {input.data}"
    shell:
        "python workflow/scripts/01_quality_check.py"


rule diversity_analysis:
    input:
        summary = "results/quality_check/data_summary.csv"
    output:
        abundance_chart = "results/diversity/abundance_chart.png",
        top_taxa_plot   = "results/diversity/top_taxa_plot.png",
        genus_summary   = "results/diversity/genus_abundance_summary.csv"
    message:
        "Step 2 — Running diversity analysis"
    shell:
        "python workflow/scripts/02_diversity_analysis.py"


rule differential_abundance:
    input:
        genus_summary = "results/diversity/genus_abundance_summary.csv"
    output:
        volcano    = "results/differential_abundance/volcano_plot.png",
        significant = "results/differential_abundance/significant_results.csv"
    message:
        "Step 3 — Running differential abundance analysis"
    shell:
        "python workflow/scripts/03_deseq2_analysis.py"


rule efsa_mapping:
    input:
        significant  = "results/differential_abundance/significant_results.csv",
        efsa_database = config["data"]["efsa_database"]
    output:
        mapped = "results/efsa_mapping/efsa_mapped_results.csv"
    message:
        "Step 5 — Running EFSA biomarker mapping"
    shell:
        "python workflow/scripts/04_efsa_mapper.py"


rule generate_report:
    input:
        significant    = "results/differential_abundance/significant_results.csv",
        efsa_mapped    = "results/efsa_mapping/efsa_mapped_results.csv",
        abundance_chart = "results/diversity/abundance_chart.png",
        top_taxa_plot  = "results/diversity/top_taxa_plot.png",
        volcano        = "results/differential_abundance/volcano_plot.png"
    output:
        pdf = "results/report/OgunBiome_Inulin_Insight_Report.pdf"
    message:
        "Step 6 — Generating OgunBiome PDF report"
    shell:
        "python workflow/scripts/05_report_generator.py"
