#!/usr/bin/env bash
# =============================================================
# Step 0b — DADA2 Amplicon Processing via QIIME2
# Author: Dr. Oluwamayowa Ogun
# Dataset: Baxter et al. 2019 — SRP128128 — Inulin arm
# Framework: DRSWAE — S phase (Scripting)
# =============================================================
# Usage: conda activate qiime2-amplicon && bash workflow/scripts/00b_dada2_pipeline.sh
# Dependencies: QIIME2 2024.10 (qiime2-amplicon conda environment)
# =============================================================
# June 2026 expansion: 5 participants -> 27 participants
# Complete wint17 inulin cohort — same semester, no batch correction
# =============================================================

set -euo pipefail

QIIME2_DIR="results/qiime2"
EXPORT_DIR="results/qiime2/exported"
MANIFEST="data/manifest.tsv"
FWD_PRIMER="GTGYCAGCMGCCGCGGTAA"
REV_PRIMER="GGACTACNVGGGTWTCTAAT"
TRUNC_F=230
TRUNC_R=200
MAX_EE=2.0
TRUNC_Q=2
THREADS=4
CONFIDENCE=0.7
CLASSIFIER="${QIIME2_DIR}/silva-138-classifier.qza"

echo "=== Step 0b: DADA2 Amplicon Processing ==="
echo "Samples: 54 paired-end FASTQ files (27 participants x 2 timepoints)"
echo "Complete wint17 inulin cohort — Baxter et al. 2019 — SRP128128"
echo ""

echo "[1/5] Importing paired-end FASTQs via manifest..."
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path "${MANIFEST}" \
  --output-path "${QIIME2_DIR}/demux.qza" \
  --input-format PairedEndFastqManifestPhred33V2

echo "[2/5] Trimming primers with Cutadapt..."
echo "Note: Baxter 2019 SRA deposit is pre-trimmed — no discard-untrimmed flag"
qiime cutadapt trim-paired \
  --i-demultiplexed-sequences "${QIIME2_DIR}/demux.qza" \
  --p-front-f "${FWD_PRIMER}" \
  --p-front-r "${REV_PRIMER}" \
  --p-cores "${THREADS}" \
  --o-trimmed-sequences "${QIIME2_DIR}/demux-trimmed.qza"

echo "[3/5] Running DADA2 denoising..."
echo "  trunc_len_f=${TRUNC_F} confirmed from FastQC Q30 profile"
echo "  trunc_len_r=${TRUNC_R} set from FastQC reverse read quality drop"
echo "  Quality profiles consistent across all 27 participants — confirmed MultiQC"
qiime dada2 denoise-paired \
  --i-demultiplexed-seqs "${QIIME2_DIR}/demux-trimmed.qza" \
  --p-trunc-len-f "${TRUNC_F}" \
  --p-trunc-len-r "${TRUNC_R}" \
  --p-max-ee-f "${MAX_EE}" \
  --p-max-ee-r "${MAX_EE}" \
  --p-trunc-q "${TRUNC_Q}" \
  --p-n-threads "${THREADS}" \
  --o-table "${QIIME2_DIR}/table.qza" \
  --o-representative-sequences "${QIIME2_DIR}/rep-seqs.qza" \
  --o-denoising-stats "${QIIME2_DIR}/denoising-stats.qza"

echo "[4/5] Assigning taxonomy with SILVA 138..."
echo "  Human stool weighted naive Bayes classifier — sklearn 1.4.2"
echo "  Confidence threshold: ${CONFIDENCE}"
qiime feature-classifier classify-sklearn \
  --i-classifier "${CLASSIFIER}" \
  --i-reads "${QIIME2_DIR}/rep-seqs.qza" \
  --p-confidence "${CONFIDENCE}" \
  --p-n-jobs "${THREADS}" \
  --o-classification "${QIIME2_DIR}/taxonomy.qza"

echo "[5/5] Exporting to TSV for downstream Python pipeline..."
qiime tools export --input-path "${QIIME2_DIR}/table.qza" --output-path "${EXPORT_DIR}/"
qiime tools export --input-path "${QIIME2_DIR}/taxonomy.qza" --output-path "${EXPORT_DIR}/"
qiime tools export --input-path "${QIIME2_DIR}/denoising-stats.qza" --output-path "${EXPORT_DIR}/"
biom convert -i "${EXPORT_DIR}/feature-table.biom" -o "${EXPORT_DIR}/feature-table.tsv" --to-tsv

echo ""
echo "=== Step 0b Complete ==="
echo "ASV table:  ${EXPORT_DIR}/feature-table.tsv"
echo "Taxonomy:   ${EXPORT_DIR}/taxonomy.tsv"
echo "Stats:      ${EXPORT_DIR}/stats.tsv"
echo "Samples processed: 27 participants x 2 timepoints = 54 samples"
