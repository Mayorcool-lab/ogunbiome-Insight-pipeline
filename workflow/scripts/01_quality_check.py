"""
OgunBiome MVP Pipeline — Step 1: Quality Check
Dataset: Baxter et al. 2019 mBio — Inulin Arm
Author: Dr. Oluwamayowa Ogun — OgunBiome Insights — CAU Kiel
"""

import pandas as pd
import yaml
import sys
from pathlib import Path


def load_config(config_path="config/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_data(config):
    path = config["data"]["input_file"]
    sheet = config["data"]["sheet_name"]
    print(f"Loading: {path} — sheet: {sheet}")
    df = pd.read_excel(path, sheet_name=sheet)
    print(f"Loaded: {df.shape[0]} taxa, {df.shape[1]} columns")
    return df


def verify_columns(df, config):
    expected = list(config["columns"].values())
    missing = [col for col in expected if col not in df.columns]
    if missing:
        print(f"ERROR — Missing columns: {missing}")
        sys.exit(1)
    print(f"Column verification passed — all {len(expected)} columns present")


def check_missing_values(df):
    missing = df.isnull().sum()
    total_missing = missing.sum()
    if total_missing > 0:
        print(f"WARNING — Missing values detected:\n{missing[missing > 0]}")
    else:
        print("Missing value check passed — no missing values")
    return missing


def identify_significant_taxa(df, config):
    fdr = config["thresholds"]["fdr"]
    fc_min = config["thresholds"]["fold_change_min"]
    adj_p_col = config["columns"]["adjusted_pvalue"]
    fc_col = config["columns"]["fold_change"]

    significant = df[
        (df[adj_p_col] < fdr) &
        (df[fc_col] >= fc_min)
    ].copy()

    print(f"\nSignificant taxa (FDR < {fdr}, FC >= {fc_min}): {len(significant)}")
    print(significant[[
        config["columns"]["classification"],
        fc_col,
        adj_p_col
    ]].to_string(index=False))

    return significant


def write_outputs(df, significant, config):
    summary_path = config["output"]["quality_check"]["summary"]
    report_path = config["output"]["quality_check"]["report"]

    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(summary_path, index=False)
    print(f"\nData summary written: {summary_path}")

    with open(report_path, "w") as f:
        f.write("OgunBiome MVP Pipeline — Quality Check Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Dataset: Baxter et al. 2019 — Inulin Arm\n")
        f.write(f"Total taxa analysed: {len(df)}\n")
        f.write(f"Significant taxa (FDR < {config['thresholds']['fdr']}): "
                f"{len(significant)}\n\n")
        f.write("Significant Taxa:\n")
        f.write("-" * 30 + "\n")
        for _, row in significant.iterrows():
            f.write(
                f"{row[config['columns']['classification']]} — "
                f"FC: {row[config['columns']['fold_change']]:.2f} — "
                f"adj.p: {row[config['columns']['adjusted_pvalue']]:.4f}\n"
            )

    print(f"Quality report written: {report_path}")


def main():
    config = load_config()
    df = load_data(config)
    verify_columns(df, config)
    check_missing_values(df)
    significant = identify_significant_taxa(df, config)
    write_outputs(df, significant, config)
    print("\nStep 1 — Quality check complete")


if __name__ == "__main__":
    main()
