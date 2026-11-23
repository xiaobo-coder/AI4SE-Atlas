import type { APIRoute } from 'astro';
import { papers, researchers, topics, projects, topicName, CATEGORY_LABEL, paperById } from '../utils/data';
// Complete atlas as plain text, one record per block, for language-model ingestion.
export const GET: APIRoute = ({ site }) => {
  const base = new URL(import.meta.env.BASE_URL.replace(/\/?$/, '/'), site ?? 'https://example.org').href;
  const out: string[] = ['# AI4SE Atlas — full text', '', 'Unranked. People and projects are alphabetical; papers are newest first. Each record lists its public source.', ''];
  out.push(`## Topics (${topics.length})`, '');
  for (const t of topics) out.push(`### ${t.name}`, `id: ${t.id}`, `description: ${t.description}`, `related: ${(t.related_topics ?? []).join(', ')}`, `url: ${base}topics/${t.id}/`, '');
  out.push(`## Researchers (${researchers.length})`, '');
  for (const r of researchers) out.push(`### ${r.name}`, `id: ${r.id}`, `institution: ${r.institution}`, `sector: ${CATEGORY_LABEL[r.category]}`, `topics: ${r.topics.map(topicName).join('; ')}`,
    ...Object.entries(r.links ?? {}).filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`), `sources: ${r.sources.join(' ')}`, `last_verified: ${r.last_verified}`, `url: ${base}researchers/${r.id}/`, '');
  out.push(`## Papers (${papers.length})`, '');
  for (const p of papers) out.push(`### ${p.title}`, `id: ${p.id}`, `year: ${p.year}`, `authors: ${p.authors.join(', ')}`, `topics: ${p.topics.map(topicName).join('; ')}`,
    ...(p.arxiv ? [`arxiv: ${p.arxiv}`] : []), `paper: ${p.links.paper}`, ...(p.links.code ? [`code: ${p.links.code}`] : []), `url: ${base}papers/${p.id}/`, '');
  out.push(`## Projects (${projects.length})`, '');
  for (const j of projects) out.push(`### ${j.name}`, `id: ${j.id}`, `description: ${j.description}`, `repository: ${j.repository}`, `topics: ${j.topics.map(topicName).join('; ')}`,
    ...(j.related_papers?.length ? [`papers: ${j.related_papers.map((id) => paperById.get(id)?.title ?? id).join('; ')}`] : []), '');
  return new Response(out.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
