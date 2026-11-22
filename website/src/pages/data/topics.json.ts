import type { APIRoute } from 'astro';
import { topics } from '../../utils/data';
export const GET: APIRoute = () => new Response(JSON.stringify(topics, null, 2), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
