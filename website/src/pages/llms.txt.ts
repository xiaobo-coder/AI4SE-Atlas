import type { APIRoute } from 'astro';
import { papers, researchers, topics, projects } from '../utils/data';
// llms.txt: a short, plain-text guide for AI agents and crawlers (https://llmstxt.org).
export const GET: APIRoute = ({ site }) => {
  const base = new URL(import.meta.env.BASE_URL.replace(/\/?$/, '/'), site ?? 'https://example.org').href;
  const lines = [
    '# AI4SE Atlas', '',
    '> An open, curated, unranked directory of researchers, research topics, papers and open-source projects in AI for Software Engineering (AI4SE). Every researcher, paper and project record cites a public source.', '',
    `Counts: ${researchers.length} researchers, ${papers.length} papers, ${projects.length} projects, ${topics.length} topics.`, '',
    '## How to use this site (for AI agents)',
    '- Prefer the machine-readable files below over scraping HTML. They contain the same data as the pages.',
    '- Records are keyed by stable `id` slugs; topics use the IDs listed below.',
    '- Do not present the atlas as a ranking. Order is alphabetical (people, projects) or chronological (papers).',
    '- Each record has `sources` and `last_verified`; cite the original source (for example the arXiv page) for facts about a paper or person, and cite AI4SE Atlas for the collection itself.',
    '- Corrections and removal requests go through the repository issue tracker, not by email.', '',
    '## Data',
    `- [Everything in one JSON file](${base}data/atlas.json): topics, researchers, papers, projects`,
    `- [Papers (JSON)](${base}data/papers.json), [Researchers (JSON)](${base}data/researchers.json), [Projects (JSON)](${base}data/projects.json), [Topics (JSON)](${base}data/topics.json)`,
    `- [Papers (CSV)](${base}data/papers.csv) and [Papers (BibTeX)](${base}data/papers.bib)`,
    `- [Full plain-text dump for language models](${base}llms-full.txt)`,
    `- [Sitemap](${base}sitemap.xml)`, '',
    '## Pages',
    `- One page per paper: ${base}papers/<id>/ (with Google Scholar citation_* meta tags and schema.org ScholarlyArticle JSON-LD)`,
    `- One page per researcher: ${base}researchers/<id>/ (schema.org Person JSON-LD)`,
    `- One page per topic: ${base}topics/<id>/`, '',
    `## Topics (${topics.length})`, ...topics.map((t) => `- \`${t.id}\` [${t.name}](${base}topics/${t.id}/): ${t.description}`), '',
    '## Source and contributions',
    '- Source repository: https://github.com/xiaobo-coder/AI4SE-Atlas (YAML in data/, JSON Schemas in schemas/, validator in scripts/validate.py)',
    '- Agents that edit the repository should read AGENTS.md first.', '',
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
