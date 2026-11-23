# Changelog

All notable changes to the data model, taxonomy, data and website. The project follows [Semantic Versioning](https://semver.org/) for its data schema.

## [0.2.0] - 2026-11-22

### Added
- Explore page: interactive timeline of papers by topic (search, year range, code filter, table view, CSV/JSON/BibTeX downloads) and a topic-by-year coverage heatmap.
- A page per paper with Google Scholar `citation_*` meta tags, schema.org `ScholarlyArticle`, BibTeX and links to authors and projects in the atlas.
- `data/papers.csv`, `sitemap.xml`, `llms.txt`.

### Changed
- Editorial redesign: dark theme by default, large display type, monospace labels, timeline on the home page.

## [0.1.0] - 2026-11-22

### Added
- Data model and JSON Schemas for researchers, topics, papers and projects.
- Initial taxonomy of ten topics (v1).
- Seed data: 81 papers, 31 of them from 2026 (metadata from arXiv), 19 open-source projects (repositories checked), and verified researcher records.
- Website: home page with an animated topic map and search, researchers A–Z with filters and detail pages, topic pages, papers, projects, about and contribution pages; JSON and BibTeX downloads; schema.org metadata on the home, researcher and topic pages.
- `scripts/add_arxiv.py` to add papers from arXiv IDs.
- Validation script, issue and pull request templates, GitHub Actions for validation and GitHub Pages deployment.
