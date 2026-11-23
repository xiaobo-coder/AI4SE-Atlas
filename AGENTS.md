# AGENTS.md — instructions for AI coding agents (Codex, Claude Code, Copilot, Cursor, …)

AI4SE Atlas is an open, **unranked** directory of AI for Software Engineering researchers, topics, papers and open-source projects. Data lives in YAML; the website only renders it.

## If you only need the data (read-only)
Do not scrape the HTML. Use the published files (same content as the pages):

| What | URL |
|---|---|
| Guide for agents | https://xiaobo-coder.github.io/AI4SE-Atlas/llms.txt |
| Everything, plain text | https://xiaobo-coder.github.io/AI4SE-Atlas/llms-full.txt |
| Everything, JSON | https://xiaobo-coder.github.io/AI4SE-Atlas/data/atlas.json |
| Papers | `data/papers.json`, `data/papers.csv`, `data/papers.bib` (same base URL) |
| Researchers / projects / topics | `data/researchers.json`, `data/projects.json`, `data/topics.json` |
| Sitemap | https://xiaobo-coder.github.io/AI4SE-Atlas/sitemap.xml |

Or read `data/*.yaml` directly from a clone. Records are keyed by stable `id` slugs.

When you use the data:
- Never describe the atlas as a ranking or "top" list. Order is alphabetical (people, projects) or chronological (papers).
- Cite the original source (each record's `sources`, e.g. the arXiv page) for facts; cite AI4SE Atlas (`CITATION.cff`) for the collection.

## If you are changing the repository
1. **Edit only `data/*.yaml`** for content. Never hard-code records in `website/`.
2. **Every fact needs a public source** in `sources` and a `last_verified` date (YYYY-MM-DD). Do not invent names, affiliations, titles, author lists, URLs or DOIs. If you cannot verify a fact from a primary page, leave the record out.
3. **Papers:** add them with the script, which copies title/authors/year from the arXiv API:
   ```sh
   python scripts/add_arxiv.py <arXiv id> [<arXiv id> …] --topics <topic id> [<topic id> …]
   ```
   Then check the detected `code` link.
4. **Researchers:** cite a page that shows the current affiliation. Use `sort_name` when the family name is not the last word (e.g. `Le Goues`) and `aliases` for other spellings used in author lists.
5. **Never store** private email addresses, phone numbers, citation counts, h-index, star counts or rankings. The validator rejects emails, phone numbers and `<`/`>` in text.
6. **Topic IDs** are fixed (see `data/topics.yaml`). Propose new topics in an issue; do not add them silently.
7. **Validate before committing:**
   ```sh
   python -m pip install -r scripts/requirements.txt
   python scripts/validate.py
   python -m unittest discover -s scripts -p "test_*.py"
   python scripts/make_map_svg.py --check     # only if topics.yaml changed
   cd website && npm ci && npm run build
   ```
8. Keep changes small and in one pull request per topic of change. The maintainer reviews every Saturday; do not push to `main` directly.

## Layout
```
data/      YAML records (researchers, topics, papers, projects)  ← edit here
schemas/   JSON Schemas (contracts for the YAML)
scripts/   validate.py, add_arxiv.py, make_map_svg.py, tests
website/   Astro + Tailwind static site; reads ../data at build time
```
