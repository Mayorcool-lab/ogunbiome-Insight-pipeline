"""
OgunBiome MVP Pipeline — Step 5: EFSA Biomarker Mapping
Author: Dr. Oluwamayowa Ogun — OgunBiome Insights — CAU Kiel

A structured EFSA biomarker mapping layer developed by Dr. Ogun,
linking microbiome features to relevant EFSA opinions and guidance documents.
"""

import pandas as pd
import yaml
from pathlib import Path


def load_config(config_path="config/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_significant_results(config):
    path = config["output"]["differential"]["significant"]
    df = pd.read_csv(path)
    print(f"Significant genera loaded: {df.shape[0]}")
    return df


def load_efsa_database(config):
    path = config["data"]["efsa_database"]
    db = pd.read_csv(path)
    print(f"EFSA database loaded: {db.shape[0]} entries")
    return db


def map_to_efsa(significant, efsa_db):
    mapped = significant.merge(
        efsa_db,
        left_on="Classification",
        right_on="genus",
        how="left"
    )

    matched = mapped[mapped["relevance_tier"].notna()]
    unmatched = mapped[mapped["relevance_tier"].isna()]["Classification"].tolist()

    if unmatched:
        print(f"No EFSA mapping found for: {unmatched}")

    print(f"Mapped entries: {len(matched)}")
    return mapped


def write_output(mapped, config):
    output_path = config["output"]["efsa"]["mapped"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    mapped.to_csv(output_path, index=False)
    print(f"EFSA mapped results saved: {output_path}")


def print_summary(mapped):
    print("\n--- EFSA Mapping Summary ---")
    cols = ["Classification", "fold_change", "adjusted_pvalue",
            "relevance_tier", "efsa_opinion", "claim_context"]
    available = [c for c in cols if c in mapped.columns]
    print(mapped[available].to_string(index=False))


def main():
    config = load_config()
    significant = load_significant_results(config)
    efsa_db = load_efsa_database(config)
    mapped = map_to_efsa(significant, efsa_db)
    write_output(mapped, config)
    print_summary(mapped)
    print("\nStep 5 — EFSA mapping complete")


if __name__ == "__main__":
    main()
