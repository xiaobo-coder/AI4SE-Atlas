import type { APIRoute } from 'astro';
import { papers } from '../../utils/data';
const cell = (v: unknown) => { const s = String(v ?? ''); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
export const GET: APIRoute = () => {
  const head = ['id', 'title', 'year', 'authors', 'topics', 'arxiv', 'paper_url', 'code_url'];
  const rows = papers.map((p) => [p.id, p.title, p.year, p.authors.join('; '), p.topics.join('; '), p.arxiv ?? '', p.links.paper, p.links.code ?? ''].map(cell).join(','));
  return new Response([head.join(','), ...rows].join('\n') + '\n', { headers: { 'Content-Type': 'text/csv; charset=utf-8' } });
};
