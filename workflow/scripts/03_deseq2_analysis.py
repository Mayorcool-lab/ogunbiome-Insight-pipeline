"""
OgunBiome MVP Pipeline — Step 3: Differential Abundance Analysis
Dataset: Baxter et al. 2019 mBio — Inulin Arm
Author: Dr. Oluwamayowa Ogun — OgunBiome Insights — CAU Kiel
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yaml
from pathlib import Path


def load_config(config_path="config/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_data(config):
    path = "results/diversity/genus_abundance_summary.csv"
    df = pd.read_csv(path)
    print(f"Genera loaded: {df.shape[0]}")
    return df


def calculate_volcano_coordinates(df):
    df["log2_fc"] = np.log2(df["fold_change"])
    df["neg_log10_p"] = -np.log10(df["adjusted_pvalue"])
    print("Volcano coordinates calculated")
    return df


def plot_volcano(df, config):
    green = config["report"]["colors"]["green"]
    gold = config["report"]["colors"]["gold"]
    fdr_threshold = -np.log10(config["thresholds"]["fdr"])
    output_path = config["output"]["differential"]["volcano"]

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.scatter(df["log2_fc"], df["neg_log10_p"],
               color="lightgrey", s=80, zorder=2,
               edgecolors="grey", linewidths=0.5)

    significant = df[df["adjusted_pvalue"] < config["thresholds"]["fdr"]]
    ax.scatter(significant["log2_fc"], significant["neg_log10_p"],
               color=green, s=120, zorder=3,
               edgecolors="white", linewidths=0.8)

    for _, row in significant.iterrows():
        ax.annotate(
            row["Classification"],
            xy=(row["log2_fc"], row["neg_log10_p"]),
            xytext=(8, 4),
            textcoords="offset points",
            fontsize=10, fontstyle="italic",
            fontweight="bold", color=green
        )

    ax.axhline(y=fdr_threshold, color=gold, linestyle="--",
               linewidth=1.2, label="FDR = 0.05")
    ax.axvline(x=0, color="grey", linestyle="-",
               linewidth=0.8, alpha=0.5)

    ax.set_xlabel("log₂ Fold Change", fontsize=12)
    ax.set_ylabel("-log₁₀ Adjusted P-value", fontsize=12)
    ax.set_title(
        "Differential Abundance — Inulin Intervention\n"
        "Significant genera labelled (FDR < 0.05)",
        fontsize=13, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Volcano plot saved: {output_path}")


def save_significant_results(df, config):
    fdr = config["thresholds"]["fdr"]
    significant = df[df["adjusted_pvalue"] < fdr].copy()
    output_path = config["output"]["differential"]["significant"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    significant.to_csv(output_path, index=False)
    print(f"Significant results saved: {output_path}")
    print(f"Significant genera: {len(significant)}")
    return significant


def main():
    config = load_config()
    df = load_data(config)
    df = calculate_volcano_coordinates(df)
    plot_volcano(df, config)
    save_significant_results(df, config)
    print("\nStep 3 — Differential abundance analysis complete")


if __name__ == "__main__":
    main()
