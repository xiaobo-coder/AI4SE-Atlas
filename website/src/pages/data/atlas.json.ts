import type { APIRoute } from 'astro';
import { topics, researchers, papers, projects } from '../../utils/data';
export const GET: APIRoute = () =>
  new Response(JSON.stringify({
    name: 'AI4SE Atlas', schema_version: 1, generated: new Date().toISOString().slice(0, 10),
    license_note: 'Bibliographic facts come from public sources cited in each record; see the repository README for data licensing.',
    topics, researchers, papers, projects,
  }, null, 2), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
