"""
OgunBiome MVP Pipeline — Step 6: Report Generation
Author: Dr. Oluwamayowa Ogun — OgunBiome Insights — CAU Kiel
"""

import sys
import yaml
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

sys.path.insert(0, "workflow/scripts")
from interpretation_text import INTERPRETATIONS

GREEN = colors.HexColor("#1A6B3C")
GOLD = colors.HexColor("#C47F0A")
LIGHT_GREY = colors.HexColor("#F5F5F5")
DARK_GREY = colors.HexColor("#333333")


def load_config(config_path="config/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def define_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="OgunTitle", fontSize=24, textColor=GREEN,
        spaceAfter=12, alignment=TA_CENTER, fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="OgunSubtitle", fontSize=14, textColor=GOLD,
        spaceAfter=8, alignment=TA_CENTER, fontName="Helvetica"
    ))
    styles.add(ParagraphStyle(
        name="OgunHeading", fontSize=13, textColor=GREEN,
        spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="OgunBody", fontSize=10, textColor=DARK_GREY,
        spaceAfter=8, leading=16, alignment=TA_JUSTIFY,
        fontName="Helvetica"
    ))
    styles.add(ParagraphStyle(
        name="OgunCaption", fontSize=8, textColor=DARK_GREY,
        spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Oblique"
    ))
    return styles


def draw_title_page(config):
    def _draw(canvas, doc):
        canvas.saveState()
        w, h = A4

        canvas.setFont("Helvetica-Bold", 36)
        canvas.setFillColor(GREEN)
        canvas.drawCentredString(w/2, h - 5*cm, "OgunBiome")

        canvas.setFont("Helvetica", 16)
        canvas.setFillColor(GOLD)
        canvas.drawCentredString(w/2, h - 6.2*cm, "I N S I G H T S")

        canvas.setStrokeColor(GREEN)
        canvas.setLineWidth(1.5)
        canvas.line(3*cm, h - 7*cm, w - 3*cm, h - 7*cm)

        canvas.setFont("Helvetica-Bold", 18)
        canvas.setFillColor(GREEN)
        canvas.drawCentredString(w/2, h - 8.5*cm,
            "OgunBiome Inulin Intervention Insight Report")

        canvas.setFont("Helvetica", 11)
        canvas.setFillColor(DARK_GREY)
        canvas.drawCentredString(w/2, h - 9.5*cm,
            "Analysis of Baxter et al. 2019 — Inulin Arm — SRP128128")

        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.8)
        canvas.line(3*cm, h - 10.5*cm, w - 3*cm, h - 10.5*cm)

        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(GREEN)
        canvas.drawCentredString(w/2, h - 12*cm, "Dr. Oluwamayowa Ogun")

        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(DARK_GREY)
        canvas.drawCentredString(w/2, h - 13*cm,
            "Computational Biologist | CAU Kiel | Gut Microbiome Science & Analytics")

        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(GREEN)
        canvas.drawCentredString(w/2, h - 14.5*cm, "Oluwatimilehin Sarah Ogun")

        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(DARK_GREY)
        canvas.drawCentredString(w/2, h - 15.5*cm,
            "Co-Founder — Food Business & Industry Relations")

        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.8)
        canvas.line(3*cm, h - 16.5*cm, w - 3*cm, h - 16.5*cm)

        canvas.setFont("Helvetica", 11)
        canvas.setFillColor(GOLD)
        canvas.drawCentredString(w/2, h - 17.5*cm,
            "OgunBiome Insights — Kiel, Germany")

        canvas.setFont("Helvetica", 11)
        canvas.setFillColor(DARK_GREY)
        canvas.drawCentredString(w/2, h - 18.5*cm, "April 2026")

        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.5*cm, w - 2*cm, 1.5*cm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DARK_GREY)
        canvas.drawCentredString(w/2, 1.2*cm, config["report"]["footer"])

        canvas.restoreState()
    return _draw


def make_footer(config):
    def _footer(canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.5*cm, w - 2*cm, 1.5*cm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DARK_GREY)
        canvas.drawCentredString(w/2, 1.2*cm, config["report"]["footer"])
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(w - 2*cm, 1.2*cm, f"Page {doc.page}")
        canvas.restoreState()
    return _footer


def build_report(config, styles):
    significant = pd.read_csv(config["output"]["differential"]["significant"])
    efsa_mapped = pd.read_csv(config["output"]["efsa"]["mapped"])
    output_path = config["output"]["report"]["pdf"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    efsa_cell_style = ParagraphStyle(
        name="EfsaCell", fontSize=8, leading=11,
        textColor=DARK_GREY, fontName="Helvetica"
    )
    efsa_header_style = ParagraphStyle(
        name="EfsaHeader", fontSize=9, leading=12,
        textColor=colors.white, fontName="Helvetica-Bold"
    )

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm
    )

    story = []
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles["OgunHeading"]))
    story.append(Paragraph(
        "Inulin supplementation resulted in a significant shift in gut "
        "microbiota composition, characterised by a marked enrichment of "
        "<i>Bifidobacterium</i> and <i>Anaerostipes</i> (FDR &lt; 0.05), "
        "indicating selective stimulation of saccharolytic and "
        "butyrate-producing taxa.",
        styles["OgunBody"]
    ))
    story.append(Paragraph(
        "Differential abundance analysis revealed two genera as primary "
        "responders to chicory-derived inulin supplementation. "
        "<i>Bifidobacterium</i> exhibited a 3.5-fold increase in relative "
        "abundance, consistent with its established role as a primary "
        "degrader of inulin-type fructans. <i>Anaerostipes</i> showed a "
        "2.2-fold enrichment, representing the most statistically significant "
        "finding (adj. p = 0.0001), reflecting cross-feeding interactions "
        "driven by Bifidobacterium-derived acetate.",
        styles["OgunBody"]
    ))
    story.append(PageBreak())

    # Community Composition
    story.append(Paragraph("Community Composition", styles["OgunHeading"]))
    story.append(Paragraph(
        "The following figures show gut microbiota abundance at baseline "
        "and during inulin supplementation across all detected genera, "
        "and the significant responders at FDR &lt; 0.05.",
        styles["OgunBody"]
    ))
    story.append(Image(
        config["output"]["diversity"]["abundance_chart"],
        width=16*cm, height=18*cm
    ))
    story.append(Paragraph(
        "Figure 1. Mean relative abundance of all detected genera at "
        "baseline and during inulin supplementation. Sorted by fold change.",
        styles["OgunCaption"]
    ))
    story.append(Spacer(1, 0.5*cm))
    story.append(Image(
        config["output"]["diversity"]["top_taxa_plot"],
        width=14*cm, height=10*cm
    ))
    story.append(Paragraph(
        "Figure 2. Significant genera — baseline vs during inulin "
        "supplementation. Fold change and adjusted p-value annotated.",
        styles["OgunCaption"]
    ))
    story.append(PageBreak())

    # Differential Abundance
    story.append(Paragraph(
        "Differential Abundance Analysis", styles["OgunHeading"]
    ))
    story.append(Paragraph(
        "Volcano plot showing log2 fold change against statistical "
        "significance for all 13 genera. Significant genera (FDR &lt; 0.05) "
        "highlighted in OgunBiome green and labelled explicitly.",
        styles["OgunBody"]
    ))
    story.append(Image(
        config["output"]["differential"]["volcano"],
        width=14*cm, height=10*cm
    ))
    story.append(Paragraph(
        "Figure 3. Volcano plot — differential abundance of gut microbiota "
        "genera in response to inulin supplementation.",
        styles["OgunCaption"]
    ))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Significant Findings", styles["OgunHeading"]))
    table_data = [["Genus", "Fold Change", "Adj. P-value", "Direction"]]
    for _, row in significant.iterrows():
        table_data.append([
            row["Classification"],
            f"{row['fold_change']:.2f}x",
            f"{row['adjusted_pvalue']:.4f}",
            "Enriched"
        ])
    sig_table = Table(table_data, colWidths=[5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    sig_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sig_table)
    story.append(PageBreak())

    # Biological Interpretation
    story.append(Paragraph(
        "Biological Interpretation", styles["OgunHeading"]
    ))
    story.append(Paragraph(
        "The following interpretations are provided by Dr. Oluwamayowa Ogun "
        "based on domain expertise in gut microbiology, glyco-enzyme biology, "
        "and dietary intervention science.",
        styles["OgunBody"]
    ))
    for genus, interp in INTERPRETATIONS.items():
        story.append(Paragraph(genus, styles["OgunHeading"]))
        for key, label in [
            ("what_it_is", "What it is"),
            ("what_changed", "What changed"),
            ("mechanism", "Mechanism"),
            ("health_relevance", "Health relevance"),
            ("efsa_relevance", "EFSA relevance")
        ]:
            story.append(Paragraph(
                f"<b>{label}:</b> {interp[key]}",
                styles["OgunBody"]
            ))
        story.append(Spacer(1, 0.3*cm))
    story.append(PageBreak())

    # EFSA Mapping
    story.append(Paragraph(
        "EFSA Biomarker Mapping", styles["OgunHeading"]
    ))
    story.append(Paragraph(
        "A structured EFSA biomarker mapping layer developed by Dr. Ogun, "
        "linking microbiome features to relevant EFSA opinions and guidance "
        "documents. Relevance tiers: HIGH — directly cited in positive EFSA "
        "opinion; MODERATE — supported by studies cited in EFSA opinions; "
        "SUPPORTING — biologically consistent but more distal.",
        styles["OgunBody"]
    ))

    col_widths = [3*cm, 1.8*cm, 6*cm, 4.7*cm]
    efsa_table_data = [[
        Paragraph("Genus", efsa_header_style),
        Paragraph("Tier", efsa_header_style),
        Paragraph("EFSA Opinion", efsa_header_style),
        Paragraph("Claim Context", efsa_header_style)
    ]]
    for _, row in efsa_mapped.iterrows():
        efsa_table_data.append([
            Paragraph(str(row.get("Classification", "")), efsa_cell_style),
            Paragraph(str(row.get("relevance_tier", "")), efsa_cell_style),
            Paragraph(str(row.get("efsa_opinion", "")), efsa_cell_style),
            Paragraph(str(row.get("claim_context", "")), efsa_cell_style)
        ])

    efsa_tbl = Table(efsa_table_data, colWidths=col_widths)
    efsa_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(efsa_tbl)
    story.append(PageBreak())

    # Conclusion
    story.append(Paragraph("Conclusion", styles["OgunHeading"]))
    story.append(Paragraph(
        "This analysis demonstrates that chicory-derived inulin "
        "supplementation produces a targeted and biologically coherent "
        "restructuring of the gut microbiota, characterised by the selective "
        "enrichment of <i>Bifidobacterium</i> and <i>Anaerostipes</i>. "
        "These findings are consistent with the established prebiotic "
        "mechanism of inulin-type fructans and are directly relevant to "
        "EFSA health claim substantiation under Regulation EC 1924/2006.",
        styles["OgunBody"]
    ))
    story.append(Paragraph(
        "The co-enrichment of a primary inulin fermenter and a cross-feeding "
        "butyrate producer provides mechanistic evidence of the complete "
        "prebiotic metabolic cascade operating in vivo. Butyrate production "
        "supports colonic epithelial health, gut barrier integrity, and "
        "mucosal immune regulation — outcomes recognised by EFSA as "
        "biologically plausible indicators of gut health benefit.",
        styles["OgunBody"]
    ))
    story.append(Paragraph(
        "OgunBiome Insights translates microbiome data into actionable gut "
        "health intelligence for the food and ingredient industry.",
        styles["OgunBody"]
    ))

    doc.build(
        story,
        onFirstPage=draw_title_page(config),
        onLaterPages=make_footer(config)
    )
    print(f"Report generated: {output_path}")


def main():
    config = load_config()
    styles = define_styles()
    build_report(config, styles)
    print("\nStep 6 — Report generation complete")


if __name__ == "__main__":
    main()
