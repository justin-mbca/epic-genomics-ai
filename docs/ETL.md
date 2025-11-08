# ETL details

This page shows a more detailed view of the FHIR → OMOP-like ETL steps used in this repo.

```mermaid
flowchart LR
  subgraph FHIR_DIR [data/fhir]
    B1(Patient JSON)
    B2(Observation JSON)
    B3(Condition JSON)
    B4(Encounter JSON)
  end
  B1 --> ETL_STEP[parse & map]
  B2 --> ETL_STEP
  B3 --> ETL_STEP
  B4 --> ETL_STEP
  ETL_STEP -->|write| PERSON[person table]
  ETL_STEP -->|write| OBS[observation/measurement]
  ETL_STEP -->|write| COND[condition_occurrence]
  ETL_STEP -->|write| VISIT[visit_occurrence]
  ClinVar -->|trim & normalize| VRS[variant_vrs]
  VRS -->|join| PAT_VAR[patient_variant demo]
  PERSON & VRS --> Analytics[notebooks / ML]
```

Notes
- The ETL is implemented in `epic_etl/run_etl.py` and writes to `data/epic_synth.db`.
- The ClinVar normalization is a prototype in `epic_etl/clinvar.py` (sha256-based VRS id). If you need GA4GH-compliant canonicalization, consider integrating `ga4gh-vrs` libraries.
