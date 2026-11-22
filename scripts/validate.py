#!/usr/bin/env python3
"""Validate the AI4SE Atlas data files.

Checks YAML syntax, JSON Schema compliance, duplicate IDs, topic and paper
references, and duplicate entities (same arXiv id, repository or person).
Exits with status 1 and prints file + record for every problem found.

Usage: python scripts/validate.py [--data DIR]
Requires: pyyaml, jsonschema (see scripts/requirements.txt)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
FILES = {  # data file -> schema name
    "topics.yaml": "topic",
    "researchers.yaml": "researcher",
    "papers.yaml": "paper",
    "projects.yaml": "project",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def add(self, file: str, record: str | None, msg: str) -> None:
        where = f"{file}" + (f" [{record}]" if record else "")
        self.errors.append(f"{where}: {msg}")


def label(rec, i: int) -> str:
    if isinstance(rec, dict) and isinstance(rec.get("id"), str):
        return f"#{i} id={rec['id']}"
    return f"#{i}"


def _strings(obj, path=""):
    """Yield (path, value) for every string inside a record."""
    if isinstance(obj, str):
        yield path or "(value)", obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for j, v in enumerate(obj):
            yield from _strings(v, f"{path}[{j}]")


def load_yaml(path: Path, rep: Report):
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        rep.add(path.name, None, "file is missing")
        return None
    except yaml.YAMLError as e:
        rep.add(path.name, None, f"YAML syntax error: {e}")
        return None
    if data is None:
        return []
    return data


def validate(data_dir: Path, schema_dir: Path) -> list[str]:
    rep = Report()
    data: dict[str, list] = {}
    for fname, sname in FILES.items():
        records = load_yaml(data_dir / fname, rep)
        if records is None:
            continue
        schema = json.loads((schema_dir / f"{sname}.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        for err in sorted(validator.iter_errors(records), key=lambda e: list(e.path)):
            path = list(err.path)
            rec = label(records[path[0]], path[0]) if path and isinstance(path[0], int) and isinstance(records, list) else None
            field = ".".join(str(p) for p in path[1:]) or "(record)"
            rep.add(fname, rec, f"{field}: {err.message}")
        data[fname] = records if isinstance(records, list) else []

    topics = {t.get("id") for t in data.get("topics.yaml", []) if isinstance(t, dict)}
    papers = {p.get("id") for p in data.get("papers.yaml", []) if isinstance(p, dict)}

    # duplicate ids within each file
    for fname, records in data.items():
        seen: dict[str, int] = {}
        for i, r in enumerate(records):
            if not isinstance(r, dict) or not isinstance(r.get("id"), str):
                continue
            if r["id"] in seen:
                rep.add(fname, label(r, i), f"duplicate id (also record #{seen[r['id']]})")
            seen.setdefault(r["id"], i)

    # references
    for fname in ("researchers.yaml", "papers.yaml", "projects.yaml"):
        for i, r in enumerate(data.get(fname, [])):
            if not isinstance(r, dict):
                continue
            for t in r.get("topics", []) or []:
                if t not in topics:
                    rep.add(fname, label(r, i), f"unknown topic id '{t}'")
    for i, t in enumerate(data.get("topics.yaml", [])):
        if isinstance(t, dict):
            for rt in t.get("related_topics", []) or []:
                if rt not in topics:
                    rep.add("topics.yaml", label(t, i), f"unknown related topic '{rt}'")
                if rt == t.get("id"):
                    rep.add("topics.yaml", label(t, i), "topic lists itself as related")
    for i, r in enumerate(data.get("projects.yaml", [])):
        if isinstance(r, dict):
            for pid in r.get("related_papers", []) or []:
                if pid not in papers:
                    rep.add("projects.yaml", label(r, i), f"unknown related paper '{pid}'")

    # duplicate entities that slipped in under different ids
    def dupes(fname: str, key, what: str) -> None:
        seen: dict[str, str] = {}
        for i, r in enumerate(data.get(fname, [])):
            if not isinstance(r, dict):
                continue
            k = key(r)
            if not k:
                continue
            if k in seen:
                rep.add(fname, label(r, i), f"same {what} as id={seen[k]}")
            seen.setdefault(k, r.get("id", "?"))

    norm = lambda s: " ".join(str(s).lower().split())
    dupes("papers.yaml", lambda r: r.get("arxiv"), "arXiv id")
    dupes("papers.yaml", lambda r: r.get("doi", "").lower() or None, "DOI")
    dupes("papers.yaml", lambda r: norm(r.get("title", "")), "title")
    dupes("projects.yaml", lambda r: str(r.get("repository", "")).lower().rstrip("/"), "repository")
    dupes("researchers.yaml", lambda r: (norm(r.get("name", "")) + "|" + norm(r.get("institution", ""))), "name and institution")
    dupes("researchers.yaml", lambda r: (r.get("links") or {}).get("dblp") or None, "DBLP profile")

    # no private contact data anywhere in the records
    email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phone = re.compile(r"\+?\d[\d\s().-]{8,}\d")
    for fname, records in data.items():
        for i, r in enumerate(records):
            for path, val in _strings(r):
                if "mailto:" in val.lower() or email.search(val.replace("https://", "").split("/")[0] if val.startswith("http") else val):
                    rep.add(fname, label(r, i), f"{path}: looks like an email address (private contact data is not allowed)")
                elif not val.startswith("http") and not re.fullmatch(r"\d{4}(-\d{2}-\d{2}|\.\d{4,5})", val) and phone.search(val):
                    rep.add(fname, label(r, i), f"{path}: looks like a phone number (private contact data is not allowed)")

    # placeholder records must never reach production data
    for fname, records in data.items():
        for i, r in enumerate(records):
            blob = json.dumps(r).lower()
            if "example.com" in blob or "illustrative" in blob or "example researcher" in blob:
                rep.add(fname, label(r, i), "looks like an illustrative placeholder record")
    return rep.errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, default=ROOT / "data")
    ap.add_argument("--schemas", type=Path, default=ROOT / "schemas")
    args = ap.parse_args(argv)
    errors = validate(args.data, args.schemas)
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\n{len(errors)} problem(s) found.")
        return 1
    counts = {f: len(yaml.safe_load((args.data / f).read_text(encoding="utf-8")) or []) for f in FILES}
    print("OK  " + ", ".join(f"{f.split('.')[0]}: {n}" for f, n in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
