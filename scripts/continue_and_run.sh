#!/usr/bin/env bash
# Non-interactive script to prepare venv, install deps, and run smoke test.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR=".venv"
PYTHON=${PYTHON:-python3}

echo "Using python: $(which $PYTHON)"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR"
  $PYTHON -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Running smoke test..."
python tests/smoke_test_run_etl.py

echo "Done."
