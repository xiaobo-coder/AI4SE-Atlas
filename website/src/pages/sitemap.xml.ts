import type { APIRoute } from 'astro';
import { papers, researchers, topics } from '../utils/data';
export const GET: APIRoute = ({ site }) => {
  const base = new URL(import.meta.env.BASE_URL.replace(/\/?$/, '/'), site ?? 'https://example.org');
  const paths = ['', 'explore/', 'researchers/', 'topics/', 'papers/', 'projects/', 'about/', 'contribute/',
    ...researchers.map((r) => `researchers/${r.id}/`), ...topics.map((t) => `topics/${t.id}/`), ...papers.map((p) => `papers/${p.id}/`)];
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${paths.map((p) => `  <url><loc>${new URL(p, base).href}</loc></url>`).join('\n')}\n</urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
