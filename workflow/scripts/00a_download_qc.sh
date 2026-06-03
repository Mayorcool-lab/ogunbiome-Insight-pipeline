#!/usr/bin/env bash
# =============================================================
# Step 0a — Raw Data Download and Quality Assessment
# Author: Dr. Oluwamayowa Ogun
# Dataset: Baxter et al. 2019 — SRP128128 — Inulin arm
# Framework: DRSWAE — S phase (Scripting)
# =============================================================
# Usage: bash workflow/scripts/00a_download_qc.sh
# Dependencies: sra-tools, fastqc, multiqc (ogunbiome environment)
# =============================================================

set -euo pipefail

RAW_DIR="data/raw"
FASTQC_DIR="results/fastqc"
MULTIQC_DIR="results/multiqc"
THREADS=4

ACCESSIONS=(
    "SRR6443837" "SRR6443965"
    "SRR6443940" "SRR6443840"
    "SRR6443863" "SRR6443902"
    "SRR6443869" "SRR6443945"
    "SRR6443914" "SRR6443899"
)

echo "=== Step 0a: Raw Data Download and Quality Assessment ==="

echo "[1/3] Downloading FASTQ files from NCBI SRA..."
for acc in "${ACCESSIONS[@]}"; do
    if [ -f "${RAW_DIR}/${acc}_1.fastq.gz" ]; then
        echo "  ${acc} already exists — skipping"
    else
        echo "  Downloading ${acc}..."
        fasterq-dump "${acc}" --outdir "${RAW_DIR}" --threads "${THREADS}" --progress
        gzip "${RAW_DIR}/${acc}_1.fastq" "${RAW_DIR}/${acc}_2.fastq"
    fi
done

echo "[2/3] Running FastQC..."
fastqc "${RAW_DIR}"/*.fastq.gz -o "${FASTQC_DIR}" --threads "${THREADS}"

echo "[3/3] Aggregating with MultiQC..."
multiqc "${FASTQC_DIR}" -o "${MULTIQC_DIR}" --filename ogunbiome_multiqc_report

echo "=== Step 0a Complete ==="
echo "Review MultiQC report to confirm DADA2 truncation lengths."
