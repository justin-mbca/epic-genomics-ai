"""Simple FHIR to SQLite ETL skeleton.

Usage:
    python -m epic_etl.run_etl --fhir-dir data/fhir --out-db data/epic_synth.db
"""
import argparse
import json
import os
import sqlite3
from pathlib import Path


def create_tables(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS person (
            person_id TEXT PRIMARY KEY,
            given_name TEXT,
            family_name TEXT,
            gender TEXT,
            birth_date TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS observation (
            obs_id TEXT PRIMARY KEY,
            person_id TEXT,
            code TEXT,
            value TEXT,
            unit TEXT,
            effective_date TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS condition (
            cond_id TEXT PRIMARY KEY,
            person_id TEXT,
            code TEXT,
            onset_date TEXT
        )
        """
    )
    conn.commit()


def load_patient(resource: dict, conn: sqlite3.Connection):
    # Minimal mapping from FHIR Patient to person table
    pid = resource.get("id")
    name = resource.get("name", [{}])[0]
    given = " ".join(name.get("given", [])) if name else None
    family = name.get("family") if name else None
    gender = resource.get("gender")
    birth = resource.get("birthDate")
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO person (person_id, given_name, family_name, gender, birth_date) VALUES (?,?,?,?,?)",
        (pid, given, family, gender, birth),
    )


def load_observation(resource: dict, conn: sqlite3.Connection):
    oid = resource.get("id")
    subject = resource.get("subject", {}).get("reference")
    person_id = None
    if subject and subject.startswith("Patient/"):
        person_id = subject.split("/", 1)[1]
    code = None
    value = None
    unit = None
    if resource.get("code"):
        coding = resource["code"].get("coding", [{}])[0]
        code = coding.get("code")
    if resource.get("valueQuantity"):
        vq = resource["valueQuantity"]
        value = str(vq.get("value"))
        unit = vq.get("unit")
    effective = resource.get("effectiveDateTime")
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO observation (obs_id, person_id, code, value, unit, effective_date) VALUES (?,?,?,?,?,?)",
        (oid, person_id, code, value, unit, effective),
    )


def load_condition(resource: dict, conn: sqlite3.Connection):
    cid = resource.get("id")
    subject = resource.get("subject", {}).get("reference")
    person_id = None
    if subject and subject.startswith("Patient/"):
        person_id = subject.split("/", 1)[1]
    code = None
    if resource.get("code"):
        coding = resource["code"].get("coding", [{}])[0]
        code = coding.get("code")
    onset = resource.get("onsetDateTime")
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO condition (cond_id, person_id, code, onset_date) VALUES (?,?,?,?)",
        (cid, person_id, code, onset),
    )


def process_fhir_dir(fhir_dir: str, out_db: str):
    conn = sqlite3.connect(out_db)
    create_tables(conn)
    p = Path(fhir_dir)
    for fp in p.rglob("*.json"):
        try:
            text = fp.read_text()
            data = json.loads(text)
        except (OSError, json.JSONDecodeError):
            # skip unreadable or invalid JSON files
            continue
        # FHIR bundle with entries
        if isinstance(data, dict) and data.get("resourceType") == "Bundle":
            for entry in data.get("entry", []):
                res = entry.get("resource")
                if not res:
                    continue
                if res.get("resourceType") == "Patient":
                    load_patient(res, conn)
                elif res.get("resourceType") == "Observation":
                    load_observation(res, conn)
                elif res.get("resourceType") == "Condition":
                    load_condition(res, conn)
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fhir-dir", required=True)
    parser.add_argument("--out-db", required=True)
    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.out_db), exist_ok=True)
    process_fhir_dir(args.fhir_dir, args.out_db)


if __name__ == "__main__":
    main()
