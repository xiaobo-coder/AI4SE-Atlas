import type { APIRoute } from 'astro';
import { papers } from '../../utils/data';
// Escape LaTeX specials so one odd title cannot break the whole file.
const esc = (s: string) => s
  .replace(/\\/g, '\\textbackslash{}')
  .replace(/([{}&%$#_])/g, '\\$1')
  .replace(/~/g, '\\textasciitilde{}')
  .replace(/\^/g, '\\textasciicircum{}')
  .replace(/\\textbackslash\\\{\\\}/g, '\\textbackslash{}');
export const GET: APIRoute = () => {
  const body = papers.map((p) => {
    const f: [string, string][] = [['title', `{${esc(p.title)}}`], ['author', p.authors.map(esc).join(' and ')], ['year', String(p.year)]];
    if (p.arxiv) f.push(['eprint', p.arxiv], ['archivePrefix', 'arXiv']);
    if (p.doi) f.push(['doi', p.doi]);
    f.push(['url', p.links.paper]);
    return `@misc{${p.id},\n${f.map(([k, v]) => `  ${k.padEnd(13)} = {${v}}`).join(',\n')}\n}`;
  }).join('\n\n');
  return new Response(body + '\n', { headers: { 'Content-Type': 'application/x-bibtex; charset=utf-8' } });
};
