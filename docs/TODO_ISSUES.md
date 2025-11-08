Small issues to create for contributors

1. Implement OMOP mapping for `visit_occurrence` (map FHIR Encounter → visit_occurrence)
2. Implement OMOP mapping for `condition_occurrence` (map FHIR Condition → condition_occurrence)
3. Implement OMOP mapping for `measurement` (map Observation.valueQuantity → measurement)
4. Add notebooks: ETL demo, analytics, ML demo
5. Add ClinVar normalization helper and variant table
6. Add GitHub Actions badge to README

Run `scripts/create_issues.sh` (requires `gh` CLI and authentication) to create these automatically.
