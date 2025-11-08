#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found; install from https://cli.github.com/ to create issues automatically."
  exit 1
fi

OWNER="justin-mbca"
REPO="epic-genomics-ai"

declare -a issues=(
  "Implement OMOP mapping for visit_occurrence|Map FHIR Encounter -> OMOP visit_occurrence"
  "Implement OMOP mapping for condition_occurrence|Map FHIR Condition -> OMOP condition_occurrence"
  "Implement OMOP mapping for measurement|Map FHIR Observation -> OMOP measurement"
  "Add notebooks for ETL and visualizations|Create Jupyter notebooks demonstrating ETL and plots"
  "Add ClinVar normalization helper|Download ClinVar TSV and normalize to GA4GH VRS/VA"
)

for i in "${issues[@]}"; do
  title="${i%%|*}"
  body="${i##*|}"
  gh issue create --repo "$OWNER/$REPO" --title "$title" --body "$body" --label "help wanted"
done

echo "Created issues."
