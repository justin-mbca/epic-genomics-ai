"""Run a quick smoke test of the ETL using a tiny synthetic FHIR bundle."""

import json
import sys
from pathlib import Path

# ensure project root is importable when running inside the venv
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from epic_etl import run_etl
import sqlite3


def make_test_bundle(path: Path):
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "p1",
                    "name": [{"given": ["Alice"], "family": "Doe"}],
                    "gender": "female",
                    "birthDate": "1980-01-01",
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "o1",
                    "subject": {"reference": "Patient/p1"},
                    "code": {"coding": [{"code": "test-code"}]},
                    "valueQuantity": {"value": 7.5, "unit": "mg/dL"},
                    "effectiveDateTime": "2020-01-01",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "c1",
                    "subject": {"reference": "Patient/p1"},
                    "code": {"coding": [{"code": "cond-code"}]},
                    "onsetDateTime": "2019-05-01",
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "v1",
                    "subject": {"reference": "Patient/p1"},
                    "period": {"start": "2020-01-01"},
                    "class": {"code": "outpatient"},
                }
            },
        ],
    }
    path.write_text(json.dumps(bundle))


def run():
    tmp_dir = Path("data/tmp_test")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = tmp_dir / "bundle.json"
    make_test_bundle(bundle_path)
    out_db = tmp_dir / "test.db"
    run_etl.process_fhir_dir(str(tmp_dir), str(out_db))
    # quick check
    conn = sqlite3.connect(str(out_db))
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM person")
    persons = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM observation")
    obs = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM condition")
    cond = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM visit_occurrence")
    visits = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM condition_occurrence")
    cond_occ = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM measurement")
    meas = cur.fetchone()[0]
    print(
        f"persons={persons} obs={obs} cond={cond} visits={visits} cond_occ={cond_occ} meas={meas}"
    )


if __name__ == "__main__":
    run()
