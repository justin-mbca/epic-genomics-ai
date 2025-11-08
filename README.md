# Epic-compatible synthetic EHR + Genomics Pipeline

This repository scaffolds a 3-month project to build an Epic-compatible data engineering + AI demo using open standards (FHIR, OMOP, GA4GH). It uses Synthea to generate synthetic EHR data and provides ETL, notebooks, and ML demo stubs.

Overview:
- Generate synthetic patients with Synthea (FHIR JSON export).
- ETL FHIR resources into a SQLite database with an OMOP-like person table.
- Integrate ClinVar variant data and normalize to GA4GH VRS/VA formats.
- Train a simple ML model to demonstrate variant interpretation.

See the `notebooks/` folder for guided examples.

Project plan and docs
---------------------
See `docs/PROJECT_PLAN.md` for the full 3-month step-by-step plan, task mapping, run instructions, and acceptance criteria.

Quick start
1. Install Python 3.10+ and Java (for Synthea).
2. Create a virtual environment and install dependencies:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

3. Use `scripts/run_synthea.sh` to generate FHIR data (requires Java and Synthea jar).
4. Run the ETL to load FHIR JSON into SQLite:

   python -m epic_etl.run_etl --fhir-dir data/fhir --out-db data/epic_synth.db

Project structure
- `epic_etl/` - Python package with ETL and utilities
- `notebooks/` - Jupyter notebooks for ETL demo and visualizations
- `scripts/` - helper scripts for Synthea and dataset download
- `data/` - generated data (gitignored)

License: MIT
