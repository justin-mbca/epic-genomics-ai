#!/usr/bin/env bash
# Helper script to run Synthea and export FHIR JSON
# Requires Java and the Synthea jar available locally.

set -euo pipefail

SYNTHEA_JAR=${SYNTHEA_JAR:-"./synthea.jar"}
OUT_DIR=${OUT_DIR:-"../data/fhir"}
PATIENTS=${PATIENTS:-1000}

if [ ! -f "$SYNTHEA_JAR" ]; then
  echo "Synthea jar not found at $SYNTHEA_JAR"
  echo "Download from https://github.com/synthetichealth/synthea/releases and place as synthea.jar"
  exit 1
fi

mkdir -p "$OUT_DIR"

java -jar "$SYNTHEA_JAR" -p "$PATIENTS" -f json -o "$OUT_DIR"

echo "Synthea run complete. FHIR JSON in $OUT_DIR"
