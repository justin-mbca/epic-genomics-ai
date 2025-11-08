Epic Genomics AI — quick usage

This document reproduces the demo steps used in the repository to generate synthetic EHR data, run the ETL into a SQLite database, import ClinVar, and run a tiny ML demo.

Prerequisites
- Java 11+ (OpenJDK)
- Python 3.10 (recommended) and virtualenv
- Internet access to download ClinVar and Synthea (first run)

Quick steps

1) Create and activate virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Generate synthetic FHIR with Synthea

Place `synthea.jar` in the repo root or download it. Example:

```bash
# download if not present
curl -L -o synthea.jar https://github.com/synthetichealth/synthea/releases/latest/download/synthea-with-deps.jar
# generate 100 patients as FHIR JSON
java -jar synthea.jar -p 100 --exporter.fhir.export=true --exporter.baseDirectory=./data
```

3) Run the ETL

```bash
source .venv/bin/activate
python -m epic_etl.run_etl --fhir-dir data/fhir --out-db data/epic_synth.db
```

4) Download and load ClinVar

```bash
python -m epic_etl.clinvar --out-tsv data/clinvar_variant_summary.txt --out-db data/epic_synth.db
# or run the helper directly
python -c "from epic_etl.clinvar import download_clinvar; from pathlib import Path; download_clinvar(Path('data/clinvar_variant_summary.txt'))"
python -c "from epic_etl.clinvar import load_variants; load_variants(Path('data/clinvar_variant_summary.txt'), Path('data/epic_synth.db'))"
```

5) Create trimmed and normalized variant tables (demo)

```bash
python -c "from epic_etl.clinvar import create_trimmed_variant_table, normalize_trimmed_variants; from pathlib import Path; create_trimmed_variant_table(Path('data/clinvar_variant_summary.txt'), Path('data/epic_synth.db')); normalize_trimmed_variants(Path('data/epic_synth.db'))"
```

6) Run the notebook demo

Open `notebooks/etl_demo.ipynb` and run the cells; the notebook contains:
- counts and top genes
- `variant_pathogenic` and `variant_vrs` usage
- ML train/validate demo that saves `data/gene_level_model.joblib`
- compact `variant_index` and `patient_variant` demo join

Artifacts produced
- `data/epic_synth.db` — SQLite DB with demo tables
- `data/clinvar_variant_summary.txt.gz` and `.txt` — downloaded ClinVar TSV
- `data/gene_level_model.joblib` — saved toy model

Notes & next steps
- The VRS-like IDs are a sha256 of a canonical allele string; for production use, adopt GA4GH VRS libraries and canonicalization.
- The ML demo is intentionally minimal: add features and cross-validation for real experiments.

Contact
- Repo: https://github.com/justin-mbca/epic-genomics-ai
