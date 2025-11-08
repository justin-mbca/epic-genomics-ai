#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
source .venv/bin/activate || true
python -m epic_etl.clinvar --out-tsv data/clinvar_variant_summary.txt --out-db data/epic_synth.db
echo "ClinVar downloaded and loaded into data/epic_synth.db"
