"""Minimal ClinVar download and normalization helper.

This module downloads a small ClinVar TSV (provided URL) and extracts a few columns into
an in-repo SQLite variant table for demo purposes.
"""
import sqlite3
import pandas as pd
import requests
from pathlib import Path


CLINVAR_TSV_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt"


def download_clinvar(dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(CLINVAR_TSV_URL, stream=True)
    r.raise_for_status()
    dest.write_bytes(r.content)


def load_variants(tsv_path: Path, db_path: Path):
    df = pd.read_csv(tsv_path, sep='\t', low_memory=False)
    # keep a few illustrative columns
    keep = ['VariationID', 'GeneSymbol', 'ClinicalSignificance', 'Type', 'ReviewStatus']
    df2 = df[[c for c in keep if c in df.columns]].copy()
    conn = sqlite3.connect(str(db_path))
    df2.to_sql('variant', conn, if_exists='replace', index=False)
    conn.close()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--out-tsv', default='data/clinvar_variant_summary.txt')
    p.add_argument('--out-db', default='data/epic_synth.db')
    args = p.parse_args()
    download_clinvar(Path(args.out_tsv))
    load_variants(Path(args.out_tsv), Path(args.out_db))
