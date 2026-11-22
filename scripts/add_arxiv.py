#!/usr/bin/env python3
"""Add papers to data/papers.yaml from their arXiv IDs.

Fetches title, authors and date from the official arXiv API, so nothing is typed by hand.
You choose the topics; the script never guesses them.

Examples:
  python scripts/add_arxiv.py 2611.03523 --topics ai-agents ai-software-maintenance
  python scripts/add_arxiv.py 2611.03523 2610.29185 --topics ai-devops --code https://github.com/org/repo
  python scripts/add_arxiv.py 2611.03523 --topics ai-agents --dry-run   # print YAML only

Then run: python scripts/validate.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "data" / "papers.yaml"
TOPICS = ROOT / "data" / "topics.yaml"
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
API = "https://export.arxiv.org/api/query?"


def fetch(ids: list[str]) -> list[dict]:
    q = urllib.parse.urlencode({"id_list": ",".join(ids), "max_results": len(ids)})
    req = urllib.request.Request(API + q, headers={"User-Agent": "ai4se-atlas/0.1 (add_arxiv.py)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    out = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.rsplit("/abs/", 1)[-1]
        aid = re.sub(r"v\d+$", "", aid)
        title = " ".join(e.find("a:title", NS).text.split())
        if title.lower() == "error":
            raise SystemExit(f"arXiv returned an error for {aid}")
        abstract = " ".join(e.find("a:summary", NS).text.split())
        code = re.search(r"https?://github\.com/[\w.-]+/[\w.-]+", abstract)
        out.append({
            "arxiv": aid, "title": title,
            "authors": [a.find("a:name", NS).text.strip() for a in e.findall("a:author", NS)],
            "year": int(e.find("a:published", NS).text[:4]),
            "code": code.group(0).rstrip(".") if code else "",
        })
    return out


def slug(title: str, taken: set[str]) -> str:
    head = title.split(":")[0] if ":" in title and len(title.split(":")[0]) < 40 else " ".join(title.split()[:5])
    s = re.sub(r"[^a-z0-9]+", "-", head.lower()).strip("-")[:50].strip("-") or "paper"
    base, n = s, 2
    while s in taken:
        s, n = f"{base}-{n}", n + 1
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+", help="arXiv IDs such as 2611.03523")
    ap.add_argument("--topics", nargs="+", required=True, help="topic IDs from data/topics.yaml")
    ap.add_argument("--code", default=None, help="code URL (default: first GitHub link in the abstract, if any)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    bad = [i for i in a.ids if not re.fullmatch(r"\d{4}\.\d{4,5}", i)]
    if bad:
        raise SystemExit(f"not an arXiv ID: {', '.join(bad)}")
    valid_topics = {t["id"] for t in yaml.safe_load(TOPICS.read_text(encoding="utf-8"))}
    unknown = [t for t in a.topics if t not in valid_topics]
    if unknown:
        raise SystemExit(f"unknown topic(s): {', '.join(unknown)}. Choose from: {', '.join(sorted(valid_topics))}")

    text = PAPERS.read_text(encoding="utf-8")
    papers = yaml.safe_load(text) or []
    have = {p.get("arxiv") for p in papers}
    taken = {p["id"] for p in papers}
    todo = [i for i in a.ids if i not in have]
    for i in sorted(set(a.ids) - set(todo)):
        print(f"skip {i}: already in papers.yaml")
    if not todo:
        return 0

    today = dt.date.today().isoformat()
    new = []
    for m in fetch(todo):
        pid = slug(m["title"], taken)
        taken.add(pid)
        new.append({"id": pid, "title": m["title"], "year": m["year"], "authors": m["authors"], "topics": a.topics,
                    "arxiv": m["arxiv"], "links": {"paper": f"https://arxiv.org/abs/{m['arxiv']}", "code": a.code if a.code is not None else m["code"]},
                    "sources": [f"https://arxiv.org/abs/{m['arxiv']}"], "last_verified": today})
        time.sleep(0.5)
    missing = set(todo) - {n["arxiv"] for n in new}
    if missing:
        print(f"warning: arXiv returned nothing for {', '.join(sorted(missing))}", file=sys.stderr)

    block = yaml.safe_dump(new, sort_keys=False, allow_unicode=True, width=100)
    if a.dry_run:
        print(block)
        return 0
    with PAPERS.open("a", encoding="utf-8") as f:
        f.write(("" if text.endswith("\n") else "\n") + block)
    for n in new:
        print(f"added {n['id']}: {n['title']} ({n['year']})" + (f"  code: {n['links']['code']}" if n["links"]["code"] else ""))
    print("Check the code link, then run: python scripts/validate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
