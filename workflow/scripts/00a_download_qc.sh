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
# June 2026 expansion: 10 accessions -> 54 accessions
# Complete wint17 inulin cohort — 27 participants x 2 timepoints
# Same semester = no batch correction required
# =============================================================

set -euo pipefail

RAW_DIR="data/raw"
FASTQC_DIR="results/fastqc"
MULTIQC_DIR="results/multiqc"
THREADS=4

ACCESSIONS=(
    # Original 5 participants
    "SRR6443837" "SRR6443965"   # U338 before/during
    "SRR6443940" "SRR6443840"   # U328 before/during
    "SRR6443863" "SRR6443902"   # U331 before/during
    "SRR6443869" "SRR6443945"   # U317 before/during
    "SRR6443914" "SRR6443899"   # U336 before/during
    # Expansion — 22 additional participants
    "SRR6443906" "SRR6444226"   # U307 before/during
    "SRR6443886" "SRR6444100"   # U310 before/during
    "SRR6444286" "SRR6444014"   # U311 before/during
    "SRR6443986" "SRR6444459"   # U312 before/during
    "SRR6444146" "SRR6444476"   # U313 before/during
    "SRR6443926" "SRR6444544"   # U315 before/during
    "SRR6444270" "SRR6444104"   # U316 before/during
    "SRR6444171" "SRR6444152"   # U318 before/during
    "SRR6444614" "SRR6444156"   # U322 before/during
    "SRR6444112" "SRR6444597"   # U323 before/during
    "SRR6444071" "SRR6444037"   # U325 before/during
    "SRR6443872" "SRR6444273"   # U326 before/during
    "SRR6443935" "SRR6444682"   # U327 before/during
    "SRR6443996" "SRR6444193"   # U329 before/during
    "SRR6444021" "SRR6443961"   # U332 before/during
    "SRR6444626" "SRR6443879"   # U333 before/during
    "SRR6443919" "SRR6444295"   # U334 before/during
    "SRR6443852" "SRR6444254"   # U335 before/during
    "SRR6443982" "SRR6443845"   # U339 before/during
    "SRR6443963" "SRR6444592"   # U341 before/during
    "SRR6443990" "SRR6444407"   # U343 before/during
    "SRR6444033" "SRR6443951"   # U344 before/during
)

echo "=== Step 0a: Raw Data Download and Quality Assessment ==="
echo "Dataset: Baxter et al. 2019 — SRP128128 — wint17 inulin arm"
echo "Samples: ${#ACCESSIONS[@]} SRA accessions — 27 participants x 2 timepoints"
echo ""

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

echo "[2/3] Running FastQC on all FASTQ files..."
fastqc "${RAW_DIR}"/*.fastq.gz -o "${FASTQC_DIR}" --threads "${THREADS}"

echo "[3/3] Aggregating FastQC reports with MultiQC..."
multiqc "${FASTQC_DIR}" -o "${MULTIQC_DIR}" --filename ogunbiome_multiqc_report

echo ""
echo "=== Step 0a Complete ==="
echo "Total accessions processed: ${#ACCESSIONS[@]}"
echo "Review MultiQC report to confirm truncation lengths consistent across all samples."
echo "Expected: trunc_len_f=230, trunc_len_r=200 based on original 10 samples."
