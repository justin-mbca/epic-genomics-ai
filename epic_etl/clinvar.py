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


def create_trimmed_variant_table(tsv_path: Path, db_path: Path, clinical_filter: str = 'Pathogenic', chunksize: int = 200_000):
    """Create a smaller `variant_pathogenic` table from the full ClinVar TSV.

    This reads the TSV in chunks, filters rows where `ClinicalSignificance` contains
    `clinical_filter`, and writes a useful subset of columns to SQLite for fast analytics.
    """
    cols_of_interest = [
        'VariationID', 'GeneSymbol', 'ClinicalSignificance',
        'Chromosome', 'Start', 'ReferenceAllele', 'AlternateAllele',
        'PositionVCF', 'ReferenceAlleleVCF', 'AlternateAlleleVCF'
    ]
    conn = sqlite3.connect(str(db_path))
    first = True
    for chunk in pd.read_csv(tsv_path, sep='\t', low_memory=False, chunksize=chunksize):
        if 'ClinicalSignificance' not in chunk.columns:
            continue
        sel = chunk[chunk['ClinicalSignificance'].astype(str).str.contains(clinical_filter, na=False)]
        if sel.empty:
            continue
        # keep only columns that exist in this file
        keep = [c for c in cols_of_interest if c in sel.columns]
        out = sel[keep].copy()
        out.to_sql('variant_pathogenic', conn, if_exists='append' if not first else 'replace', index=False)
        first = False
    conn.close()


def normalize_trimmed_variants(db_path: Path, batch_size: int = 100_000):
    """Compute a stable, deterministic VRS-like id for rows in `variant_pathogenic`.

    This produces a `variant_vrs` table with columns: vrs_id, VariationID, gene, vrs_input.
    The vrs_id is a sha256 hex digest of a canonical allele string.
    """
    import hashlib
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    # create target table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS variant_vrs (
        vrs_id TEXT PRIMARY KEY,
        VariationID INTEGER,
        GeneSymbol TEXT,
        vrs_input TEXT
    )
    ''')
    conn.commit()
    # count rows
    try:
        # count rows (not used directly but keep for diagnostics if needed)
        _ = cur.execute('select count(*) from variant_pathogenic').fetchone()[0]
    except Exception:
        _ = 0
    offset = 0
    # discover which columns exist in variant_pathogenic and query only those
    cur2 = conn.cursor()
    cur2.execute("PRAGMA table_info(variant_pathogenic)")
    cols = [r[1] for r in cur2.fetchall()]
    desired = [
        'VariationID', 'GeneSymbol', 'Chromosome', 'Start', 'PositionVCF',
        'ReferenceAllele', 'AlternateAllele', 'ReferenceAlleleVCF', 'AlternateAlleleVCF'
    ]
    present = [c for c in desired if c in cols]
    if 'VariationID' not in present or 'Chromosome' not in present:
        # nothing sensible to do without at least VariationID and Chromosome
        conn.close()
        return

    select_clause = ",".join(present)
    while True:
        rows = cur.execute(f"select {select_clause} from variant_pathogenic limit {batch_size} offset {offset}").fetchall()
        if not rows:
            break
        inserts = []
        for r in rows:
            # row is a tuple aligned with `present`
            rec = dict(zip(present, r))
            VariationID = rec.get('VariationID')
            GeneSymbol = rec.get('GeneSymbol')
            Chromosome = rec.get('Chromosome')
            # prefer VCF position when available
            pos = rec.get('PositionVCF') if 'PositionVCF' in rec else rec.get('Start')
            # prefer VCF alleles when available
            ref = rec.get('ReferenceAlleleVCF') if 'ReferenceAlleleVCF' in rec and rec.get('ReferenceAlleleVCF') not in (None, '') else rec.get('ReferenceAllele')
            alt = rec.get('AlternateAlleleVCF') if 'AlternateAlleleVCF' in rec and rec.get('AlternateAlleleVCF') not in (None, '') else rec.get('AlternateAllele')
            if Chromosome in (None, '') or pos in (None, '') or ref in (None, '') or alt in (None, ''):
                # skip incomplete allele descriptions
                continue
            vrs_input = f"{Chromosome}:{pos}:{ref}:{alt}"
            vrs_id = hashlib.sha256(vrs_input.encode('utf-8')).hexdigest()
            inserts.append((vrs_id, VariationID, GeneSymbol, vrs_input))
        if inserts:
            cur.executemany('insert OR IGNORE into variant_vrs (vrs_id,VariationID,GeneSymbol,vrs_input) values (?,?,?,?)', inserts)
            conn.commit()
        offset += batch_size
    conn.close()




if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--out-tsv', default='data/clinvar_variant_summary.txt')
    p.add_argument('--out-db', default='data/epic_synth.db')
    args = p.parse_args()
    download_clinvar(Path(args.out_tsv))
    load_variants(Path(args.out_tsv), Path(args.out_db))
