import type { APIRoute } from 'astro';
import { papers, researchers, topics, projects } from '../utils/data';
// Plain-text overview for language-model crawlers and agents (llms.txt convention).
export const GET: APIRoute = ({ site }) => {
  const base = new URL(import.meta.env.BASE_URL.replace(/\/?$/, '/'), site ?? 'https://example.org').href;
  const lines = [
    '# AI4SE Atlas', '',
    '> An open, curated, unranked directory of researchers, research topics, papers and open-source projects in AI for Software Engineering. Every researcher, paper and project cites a public source.', '',
    '## Data', `- [All data (JSON)](${base}data/atlas.json)`, `- [Papers (CSV)](${base}data/papers.csv)`, `- [Papers (BibTeX)](${base}data/papers.bib)`, `- [Sitemap](${base}sitemap.xml)`, '',
    `## Topics (${topics.length})`, ...topics.map((t) => `- [${t.name}](${base}topics/${t.id}/): ${t.description}`), '',
    `## Counts`, `- ${researchers.length} researchers, ${papers.length} papers, ${projects.length} projects`, '',
    '## Policy', '- No rankings: researchers are alphabetical by family name, papers chronological, projects alphabetical.', '- Corrections and removal on request: see the About page.', '',
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
