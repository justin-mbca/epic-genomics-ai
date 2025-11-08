# Epic-compatible synthetic EHR + Genomics Pipeline — Project Plan

This document captures the 3-month plan to build an Epic-compatible data engineering + AI demo using synthetic EHR and variant data. It maps the high-level plan to repository tasks, run instructions, acceptance criteria, and assumptions.

1) Goals
- Build a pipeline that uses open standards (FHIR, OMOP, GA4GH) with synthetic data.
- Produce a reproducible GitHub portfolio project demonstrating ETL, basic analytics, and a small ML demo for variant interpretation.

2) High-level 3-month roadmap
- Month 1 — Foundations
  - Learn FHIR, OMOP, GA4GH concepts and set up local tools (Synthea, HAPI FHIR if desired).
  - Deliverable: architecture summary document (this repo's docs).

- Month 2 — Data engineering
  - Generate synthetic data using Synthea (FHIR JSON). ETL pipeline to transform FHIR → SQLite/OMOP-like tables.
  - Deliverable: Jupyter notebooks and SQL schema demonstrating transformations and visualizations.

- Month 3 — AI & Genomics Integration
  - Normalize ClinVar / variant data to GA4GH VRS/VA formats, join to synthetic phenotypes, train a small classifier, and export predictions in GA4GH VA JSON.
  - Deliverable: notebooks, example outputs, README docs for demo and presentation.

3) Repo task mapping (what's implemented vs planned)
- Implemented / scaffolded
  - Project scaffold: `README.md`, `requirements.txt`, `.gitignore`.
  - ETL skeleton: `epic_etl/run_etl.py` (Patient, Observation, Condition → SQLite).
  - Synthea helper: `scripts/run_synthea.sh`.
  - Smoke test: `tests/smoke_test_run_etl.py`.
  - Continue runner and VS Code task: `scripts/continue_and_run.sh`, `.vscode/tasks.json`.

- Planned (todo)
  - Full OMOP CDM mapping (person, visit_occurrence, condition_occurrence, measurement)
  - Notebooks & visualizations in `notebooks/`
  - ClinVar normalization & GA4GH VRS integration
  - Small ML pipeline and GA4GH VA output
  - CI (GitHub Actions) to run smoke test on push

4) How to run locally (quick)
1. Ensure Python 3.10+ is available. Recommended: pyenv, conda, or system Python.
2. From repo root:

   chmod +x scripts/continue_and_run.sh
   bash ./scripts/continue_and_run.sh

This creates a `.venv`, installs dependencies, and runs a smoke test which verifies `person`, `observation`, and `condition` are loaded.

Alternative manual steps:

   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python tests/smoke_test_run_etl.py

5) Acceptance criteria / quality gates
- Build: `scripts/continue_and_run.sh` runs without error.
- Smoke test: `persons >= 1`, `observations >= 0`, `conditions >= 0` after run.
- Linting / types: minimal; avoid broad exception catches, ensure tests import local package correctly.

6) Assumptions and environment notes
- The project does not require access to an Epic instance. We use Synthea for synthetic EHR data.
- Java is required to run Synthea (download `synthea.jar` separately). Synthea is not included in this repo.
- For small demos SQLite is used; production pipelines would use PostgreSQL or cloud data warehouses.

7) Next implementation steps (recommended priorities)
1. Complete OMOP mapping for Person, Visit, Condition, Measurement (high priority).
2. Add notebooks demonstrating ETL + SQL analytics + plots (age distribution, condition counts).
3. Add ClinVar normalization (GA4GH VRS tool or light normalization path) and variant table.
4. Integrate phenotypes + variants and create ML dataset.
5. Train a small model and export GA4GH VariantAnnotation outputs.
6. Add CI workflow that runs smoke tests and lints.

8) Contact / contribution guidance
- Open issues for tasks you want help with. Each issue should map to one todo item in this plan (e.g., "Implement OMOP visit mapping").

Quality coverage
- This document is linked from `README.md`.
