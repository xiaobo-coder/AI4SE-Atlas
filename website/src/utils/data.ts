// Loads the YAML files in ../data at build time. The website never hard-codes records.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { load } from 'js-yaml';

export type Category = 'academia' | 'industry' | 'independent';
export interface Topic { id: string; name: string; short_name?: string; description: string; related_topics?: string[] }
export interface Researcher {
  id: string; name: string; sort_name?: string; aliases?: string[]; institution: string; category: Category;
  topics: string[]; links?: Partial<Record<'homepage' | 'google_scholar' | 'dblp' | 'orcid' | 'github', string>>;
  sources: string[]; last_verified: string;
}
export interface Paper {
  id: string; title: string; year: number; authors: string[]; topics: string[]; arxiv?: string; doi?: string;
  links: { paper: string; code?: string }; sources: string[]; last_verified?: string;
}
export interface Project {
  id: string; name: string; description: string; topics: string[]; repository: string;
  related_papers?: string[]; sources: string[]; last_verified?: string;
}

// Build commands run from website/, so the data folder is ../data (override with ATLAS_DATA).
const dataDir = process.env.ATLAS_DATA || resolve(process.cwd(), '..', 'data');
function read<T>(name: string): T[] {
  const parsed = load(readFileSync(resolve(dataDir, name), 'utf8'));
  return (Array.isArray(parsed) ? parsed : []) as T[];
}

/** Sort key: explicit sort_name, else the last name token. Locale-aware, accent-insensitive. */
export function sortKey(r: Pick<Researcher, 'name' | 'sort_name'>): string {
  const base = r.sort_name?.trim() || r.name.trim().split(/\s+/).at(-1) || r.name;
  return base.normalize('NFD').replace(/\p{Diacritic}/gu, '');
}
export function initial(r: Pick<Researcher, 'name' | 'sort_name'>): string {
  const c = sortKey(r).charAt(0).toUpperCase();
  return /[A-Z]/.test(c) ? c : '#';
}
const collator = new Intl.Collator('en', { sensitivity: 'base' });
export const byResearcher = (a: Researcher, b: Researcher) =>
  collator.compare(sortKey(a), sortKey(b)) || collator.compare(a.name, b.name);

export const topics = read<Topic>('topics.yaml');
export const researchers = read<Researcher>('researchers.yaml').sort(byResearcher);
export const papers = read<Paper>('papers.yaml').sort((a, b) => b.year - a.year || collator.compare(a.title, b.title));
export const projects = read<Project>('projects.yaml').sort((a, b) => collator.compare(a.name, b.name));

export const topicById = new Map(topics.map((t) => [t.id, t]));
export const paperById = new Map(papers.map((p) => [p.id, p]));
export const topicName = (id: string) => topicById.get(id)?.name ?? id;

export const CATEGORY_LABEL: Record<Category, string> = { academia: 'Academia', industry: 'Industry', independent: 'Independent' };

export function authorLine(authors: string[], max = 6): string {
  return authors.length <= max ? authors.join(', ') : `${authors.slice(0, max).join(', ')}, et al. (${authors.length} authors)`;
}

/** Prefix a site-relative path with the configured base. */
export function url(path = ''): string {
  const b = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${b}/${path.replace(/^\//, '')}`;
}
