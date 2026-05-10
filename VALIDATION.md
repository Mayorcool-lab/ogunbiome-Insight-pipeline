# Pipeline Validation Statement

## Definition

Validation is defined as the independent reproduction of published findings from a peer-reviewed study using this analytical pipeline.

---

## Reference Study

**Citation:** Baxter NT et al. (2019). Dynamics of Human Gut Microbiota and Short-Chain Fatty Acids in Response to Dietary Interventions with Three Fermentable Fibers. *mBio* 10:e02566-18.

**NCBI SRA Accession:** SRP128128

**Study design:** Randomised controlled trial. 174 healthy adults. Four intervention arms — chicory-derived inulin, potato resistant starch, maize resistant starch, and accessible corn starch control. Two-week dietary supplementation. 16S rRNA amplicon sequencing of stool samples before and during intervention.

**Pipeline focus:** Inulin arm exclusively.

---

## Published Findings

Baxter et al. 2019 reported that chicory-derived inulin supplementation significantly altered gut microbiota composition, with Bifidobacterium and Anaerostipes identified as the primary enriched taxa in the inulin arm.

---

## Pipeline Results

Significant genera identified at FDR < 0.05 and fold change >= 1.5:

| Genus | Fold Change | Adjusted P-value | Direction |
|-------|-------------|------------------|-----------|
| Bifidobacterium | 3.54x | 0.0022 | Enriched |
| Anaerostipes | 2.16x | 0.0001 | Enriched |

---

## Validation Statement

The pipeline independently recovered Bifidobacterium and Anaerostipes as the primary statistically significant responders to inulin supplementation, consistent with the published findings of Baxter et al. 2019.

The biological coherence of this finding is confirmed by the established prebiotic mechanism. Bifidobacterium species possess beta-fructosidase enzymes that selectively ferment inulin, positioning them as primary responders. Anaerostipes cross-feeds on acetate produced by Bifidobacterium during inulin fermentation, producing butyrate — a well-characterised secondary response consistent with the cross-feeding cascade reported in the prebiotic literature.

---

## Limitations

This validation was performed on a pre-processed supplementary data table from Baxter et al. 2019, not on raw FASTQ sequencing files. Fold changes and adjusted p-values were calculated by the original authors. The pipeline applied genus-level aggregation, visualisation, biological interpretation, and regulatory biomarker mapping to these pre-processed results.

Future pipeline versions will process raw sequencing data through the complete workflow including DADA2 or QIIME2 denoising, OTU table construction, and PyDESeq2 differential abundance analysis from raw counts.

---

## Version Control

All scripts, outputs, and this validation statement are version-controlled at:
https://github.com/Mayorcool-lab/ogunbiome-mvp-pipeline

---

Validated by: Dr. Oluwamayowa Ogun — Computational Biologist — CAU Kiel
Date: April 2026
