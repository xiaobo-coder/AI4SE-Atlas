# Contributing to AI4SE Atlas

Thank you for helping. The atlas is only as good as its sources, so every record must be checkable.

## Ways to contribute

| You want to… | Do this |
|---|---|
| Suggest a researcher, paper or project | Open an issue with the matching template (no Git needed). |
| Add records yourself | Edit the YAML file in `data/` and open a pull request. |
| Fix or remove a record | Open a **Report a correction** issue, or a pull request. |
| Discuss the taxonomy | Open a **Propose a taxonomy change** issue. |

## Inclusion criteria

1. The record is clearly related to AI for Software Engineering.
2. Each fact (name, affiliation, title, authors, year, URL) is supported by a public source listed in `sources`.
3. No promotional wording. Descriptions are short and factual.
4. Only professional, public information: no private email addresses, phone numbers or other personal data.
5. No rankings or popularity data: no citation counts, h-index, stars or "top" labels.

Self-nominations are fine and follow the same rules.

## Record format

Data files: `data/researchers.yaml`, `data/papers.yaml`, `data/projects.yaml`, `data/topics.yaml`. Contracts: `schemas/*.schema.json`.

- `id`: lowercase words separated by hyphens (`given-family`, `short-paper-name`). IDs never change once merged.
- `topics`: one or more IDs from `data/topics.yaml`.
- `sources`: at least one public `https://` (or `http://`) URL. For researchers, a page that shows the current affiliation (for example a faculty or company page).
- `last_verified`: the date you checked the sources (`YYYY-MM-DD`).
- `sort_name` (researchers, optional): the family name to sort by when it is not the last word, for example `Le Goues` or a family name written first.
- Papers: copy the title and author list exactly from the source (arXiv or the publisher).

## Adding papers quickly

Let the script copy the metadata from arXiv instead of typing it:

```sh
python scripts/add_arxiv.py 2611.03523 2610.29185 --topics ai-agents ai-devops
python scripts/validate.py
```

It fetches the exact title, authors and year from the arXiv API, takes the first GitHub link in the abstract as the code link (check it), and refuses unknown topic IDs or papers that are already listed.

## Check your change locally

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/validate.py          # schemas, references, duplicates
python scripts/make_map_svg.py      # only if you changed data/topics.yaml
cd website && npm ci && npm run build
```

## Review

The maintainer reviews contributions every Saturday. A pull request is merged when the validation passes and the sources support the record. The maintainer may ask for changes or decline a record that does not meet the criteria. See `GOVERNANCE.md`.

By contributing, you agree that your original contributions (descriptions, taxonomy edits) are licensed under CC BY 4.0 and code under MIT (see `DATA_LICENSE.md`).
