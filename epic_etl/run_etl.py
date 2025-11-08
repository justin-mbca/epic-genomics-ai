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
    # OMOP-like tables
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS visit_occurrence (
            visit_id TEXT PRIMARY KEY,
            person_id TEXT,
            visit_start_date TEXT,
            visit_concept TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS condition_occurrence (
            condition_occurrence_id TEXT PRIMARY KEY,
            person_id TEXT,
            condition_concept TEXT,
            condition_start_date TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS measurement (
            measurement_id TEXT PRIMARY KEY,
            person_id TEXT,
            measurement_concept TEXT,
            value_as_number REAL,
            unit_concept TEXT,
            measurement_date TEXT
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
    # also write to OMOP-like measurement when value is numeric
    try:
        val_num = float(value) if value is not None else None
    except (TypeError, ValueError):
        val_num = None
    if val_num is not None:
        cur.execute(
            "INSERT OR REPLACE INTO measurement (measurement_id, person_id, measurement_concept, value_as_number, unit_concept, measurement_date) VALUES (?,?,?,?,?,?)",
            (oid, person_id, code, val_num, unit, effective),
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
    # mirror into OMOP-like condition_occurrence
    cur.execute(
        "INSERT OR REPLACE INTO condition_occurrence (condition_occurrence_id, person_id, condition_concept, condition_start_date) VALUES (?,?,?,?)",
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
                elif res.get("resourceType") == "Encounter":
                    # simple mapping: Encounter.id -> visit_occurrence
                    vid = res.get("id")
                    subject = res.get("subject", {}).get("reference")
                    person_id = None
                    if subject and subject.startswith("Patient/"):
                        person_id = subject.split("/", 1)[1]
                    start = (
                        res.get("period", {}).get("start")
                        if res.get("period")
                        else None
                    )
                    visit_type = (
                        res.get("class", {}).get("code") if res.get("class") else None
                    )
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT OR REPLACE INTO visit_occurrence (visit_id, person_id, visit_start_date, visit_concept) VALUES (?,?,?,?)",
                        (vid, person_id, start, visit_type),
                    )
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
