import sys
import sqlite3
from pathlib import Path
import pandas as pd

# Ensure project root is on sys.path so tests can import epic_etl when run from CI or locally
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from epic_etl import clinvar


def make_tsv(path: Path):
    df = pd.DataFrame([
        {
            'VariationID': 1,
            'GeneSymbol': 'GENE1',
            'ClinicalSignificance': 'Pathogenic',
            'Chromosome': '1',
            'Start': 100,
            'ReferenceAllele': 'A',
            'AlternateAllele': 'T',
        },
        {
            'VariationID': 2,
            'GeneSymbol': 'GENE2',
            'ClinicalSignificance': 'Benign',
            'Chromosome': '2',
            'Start': 200,
            'ReferenceAllele': 'G',
            'AlternateAllele': 'C',
        }
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep='\t', index=False)


def test_clinvar_load_and_normalize(tmp_path: Path):
    tsv = tmp_path / 'variant_summary.txt'
    db = tmp_path / 'test.db'
    make_tsv(tsv)
    # load variants
    clinvar.load_variants(tsv, db)
    conn = sqlite3.connect(str(db))
    assert conn.execute('select count(*) from variant').fetchone()[0] == 2
    conn.close()

    # create trimmed pathogenic table
    clinvar.create_trimmed_variant_table(tsv, db, clinical_filter='Pathogenic', chunksize=10)
    conn = sqlite3.connect(str(db))
    assert conn.execute('select count(*) from variant_pathogenic').fetchone()[0] == 1
    conn.close()

    # normalize trimmed variants
    clinvar.normalize_trimmed_variants(db, batch_size=10)
    conn = sqlite3.connect(str(db))
    # ensure variant_vrs created and has 1 row
    assert conn.execute("select count(*) from variant_vrs").fetchone()[0] == 1
    # check vrs_input format
    row = conn.execute('select vrs_input from variant_vrs limit 1').fetchone()[0]
    assert row.count(':') == 3
    conn.close()
