"""Self-test for validate.py: good fixtures pass, each kind of bad record is caught."""
import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
T = [{"id": "ai-agents", "name": "AI Agents for Software Engineering", "description": "Agents that edit and test code.", "related_topics": ["ai-software-testing"]},
     {"id": "ai-software-testing", "name": "AI for Software Testing", "description": "Tests, oracles and fuzzing."}]
R = [{"id": "ada-lovelace", "name": "Ada Lovelace", "institution": "Analytical Engine University", "category": "academia",
      "topics": ["ai-agents"], "links": {"homepage": "https://ada.invalid/"}, "sources": ["https://ada.invalid/"], "last_verified": "2026-11-22"}]
P = [{"id": "p1", "title": "A Paper", "year": 2026, "authors": ["Ada Lovelace"], "topics": ["ai-agents"], "arxiv": "2601.00001",
      "links": {"paper": "https://arxiv.org/abs/2601.00001"}, "sources": ["https://arxiv.org/abs/2601.00001"]}]
J = [{"id": "j1", "name": "Tool", "description": "A research tool for tests.", "topics": ["ai-software-testing"],
      "repository": "https://github.com/x/tool", "related_papers": ["p1"], "sources": ["https://github.com/x/tool"]}]


class ValidateTests(unittest.TestCase):
    def run_with(self, **override):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d)
        files = {"topics.yaml": T, "researchers.yaml": R, "papers.yaml": P, "projects.yaml": J}
        for k, v in override.items():
            files[k.replace("_", ".")] = v
        for name, recs in files.items():
            (d / name).write_text(recs if isinstance(recs, str) else yaml.safe_dump(recs), encoding="utf-8")
        return validate.validate(d, ROOT / "schemas")

    def test_good(self):
        self.assertEqual(self.run_with(), [])

    def expect(self, needle, **override):
        errs = self.run_with(**override)
        self.assertTrue(any(needle in e for e in errs), f"expected '{needle}' in {errs}")

    def test_yaml_syntax(self):
        self.expect("YAML syntax error", topics_yaml="- id: [unclosed")

    def test_required_field(self):
        r = copy.deepcopy(R); del r[0]["institution"]
        self.expect("'institution' is a required property", researchers_yaml=r)

    def test_category(self):
        r = copy.deepcopy(R); r[0]["category"] = "government"
        self.expect("category", researchers_yaml=r)

    def test_bad_url(self):
        r = copy.deepcopy(R); r[0]["links"]["homepage"] = "javascript:alert(1)"
        self.expect("links.homepage", researchers_yaml=r)

    def test_missing_sources(self):
        r = copy.deepcopy(R); r[0]["sources"] = []
        self.expect("sources", researchers_yaml=r)

    def test_private_field_rejected(self):
        r = copy.deepcopy(R); r[0]["email"] = "ada@x.invalid"
        self.expect("Additional properties", researchers_yaml=r)

    def test_unknown_topic(self):
        p = copy.deepcopy(P); p[0]["topics"] = ["ai-quantum"]
        self.expect("unknown topic id 'ai-quantum'", papers_yaml=p)

    def test_unknown_related_paper(self):
        j = copy.deepcopy(J); j[0]["related_papers"] = ["nope"]
        self.expect("unknown related paper 'nope'", projects_yaml=j)

    def test_duplicate_id(self):
        self.expect("duplicate id", papers_yaml=P + [dict(P[0], arxiv="2601.00002", title="Other")])

    def test_duplicate_arxiv(self):
        self.expect("same arXiv id", papers_yaml=P + [dict(P[0], id="p2", title="Other")])

    def test_duplicate_repo(self):
        self.expect("same repository", projects_yaml=J + [dict(J[0], id="j2", repository="https://github.com/X/Tool/")])

    def test_html_in_text_rejected(self):
        r = copy.deepcopy(R); r[0]["institution"] = "SMU</script><img src=x onerror=alert(1)>"
        self.expect("institution", researchers_yaml=r)

    def test_email_rejected(self):
        r = copy.deepcopy(R); r[0]["aliases"] = ["ada@example.org"]
        self.expect("email", researchers_yaml=r)

    def test_phone_rejected(self):
        r = copy.deepcopy(R); r[0]["institution"] = "Call +1 (604) 555-0100"
        self.expect("phone", researchers_yaml=r)

    def test_placeholder(self):
        r = copy.deepcopy(R); r[0]["sources"] = ["https://example.com/profile"]
        self.expect("placeholder", researchers_yaml=r)


if __name__ == "__main__":
    unittest.main()
