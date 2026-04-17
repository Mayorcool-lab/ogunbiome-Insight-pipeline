"""
OgunBiome MVP Pipeline — Step 2: Diversity Analysis
Dataset: Baxter et al. 2019 mBio — Inulin Arm
Author: Dr. Oluwamayowa Ogun — OgunBiome Insights — CAU Kiel
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import yaml
from pathlib import Path


def load_config(config_path="config/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_data(config):
    path = config["output"]["quality_check"]["summary"]
    df = pd.read_csv(path)
    print(f"Loaded: {df.shape[0]} taxa")
    return df


def aggregate_by_genus(df, config):
    col_class = config["columns"]["classification"]
    col_before = config["columns"]["abund_before"]
    col_during = config["columns"]["abund_during"]
    col_fc = config["columns"]["fold_change"]
    col_adjp = config["columns"]["adjusted_pvalue"]

    df_genus = df.groupby(col_class).agg(
        abund_before=(col_before, "sum"),
        abund_during=(col_during, "sum"),
        fold_change=(col_fc, "mean"),
        adjusted_pvalue=(col_adjp, "min")
    ).reset_index()

    print(f"Genera after aggregation: {df_genus.shape[0]}")
    return df_genus


def plot_abundance_chart(df_genus, config):
    green = config["report"]["colors"]["green"]
    gold = config["report"]["colors"]["gold"]
    output_path = config["output"]["diversity"]["abundance_chart"]

    df_sorted = df_genus.sort_values("fold_change", ascending=True).copy()

    labels = df_sorted["Classification"].tolist()
    before = df_sorted["abund_before"].tolist()
    during = df_sorted["abund_during"].tolist()

    y = np.arange(len(labels))
    height = 0.35

    fig, ax = plt.subplots(figsize=(10, 12))

    ax.barh(y + height/2, during, height, color=green,
            label="During inulin", alpha=0.85)
    ax.barh(y - height/2, before, height, color=gold,
            label="Baseline", alpha=0.85)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Mean Relative Abundance (%)", fontsize=11)
    ax.set_title(
        "Gut Microbiota Abundance — Baseline vs Inulin Supplementation\n"
        "Baxter et al. 2019 — Inulin Arm",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Abundance chart saved: {output_path}")


def plot_top_responders(df_genus, config):
    green = config["report"]["colors"]["green"]
    gold = config["report"]["colors"]["gold"]
    output_path = config["output"]["diversity"]["top_taxa_plot"]
    fdr = config["thresholds"]["fdr"]

    significant = df_genus[
        df_genus["adjusted_pvalue"] < fdr
    ].sort_values("fold_change", ascending=False).copy()

    print(f"Significant genera: {len(significant)}")

    genera = significant["Classification"].tolist()
    before = significant["abund_before"].tolist()
    during = significant["abund_during"].tolist()
    fold_changes = significant["fold_change"].tolist()
    pvalues = significant["adjusted_pvalue"].tolist()

    x = np.arange(len(genera))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 7))

    ax.bar(x - width/2, before, width, color=gold,
           label="Baseline", alpha=0.85)
    bars_during = ax.bar(x + width/2, during, width,
                         color=green, label="During inulin", alpha=0.85)

    for bar, fc, p in zip(bars_during, fold_changes, pvalues):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{fc:.1f}x\np={p:.4f}",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold", color=green
        )

    ax.set_xticks(x)
    ax.set_xticklabels(genera, fontsize=11, fontstyle="italic")
    ax.set_ylabel("Mean Relative Abundance (%)", fontsize=11)
    ax.set_title(
        "Significant Microbiome Responders to Inulin Supplementation\n"
        "Baxter et al. 2019 — FDR < 0.05",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Top responders chart saved: {output_path}")


def write_genus_summary(df_genus, config):
    output_path = "results/diversity/genus_abundance_summary.csv"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df_genus.to_csv(output_path, index=False)
    print(f"Genus summary saved: {output_path}")


def main():
    config = load_config()
    df = load_data(config)
    df_genus = aggregate_by_genus(df, config)
    plot_abundance_chart(df_genus, config)
    plot_top_responders(df_genus, config)
    write_genus_summary(df_genus, config)
    print("\nStep 2 — Diversity analysis complete")


if __name__ == "__main__":
    main()
