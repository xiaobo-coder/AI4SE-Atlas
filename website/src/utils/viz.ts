// Build-time geometry for the Explore charts. Marks are uniform in size (no ranking).
import { papers, topics, type Paper } from './data';

/** Fractional year from the arXiv ID (YYMM), falling back to mid-year. */
export function when(p: Paper): number {
  const m = p.arxiv?.match(/^(\d{2})(\d{2})\./);
  return m ? 2000 + Number(m[1]) + (Number(m[2]) - 0.5) / 12 : p.year + 0.5;
}
export function monthLabel(p: Paper): string {
  const m = p.arxiv?.match(/^(\d{2})(\d{2})\./);
  if (!m) return String(p.year);
  return new Date(Date.UTC(2000 + Number(m[1]), Number(m[2]) - 1, 1)).toLocaleString('en', { month: 'short', year: 'numeric', timeZone: 'UTC' });
}
/** Deterministic jitter in [-1, 1] so dots in a lane do not sit on one line. */
function jitter(s: string): number {
  let h = 2166136261;
  for (const c of s) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return ((h >>> 0) % 1000) / 500 - 1;
}

export interface TimelineGeom {
  W: number; H: number; left: number; right: number; top: number; bottom: number; laneH: number;
  x0: number; x1: number; years: number[];
  lanes: { id: string; label: string; y: number }[];
  dots: { pid: string; topic: string; cx: number; cy: number }[];
}

export function timeline(opts: { W?: number; laneH?: number; left?: number } = {}): TimelineGeom {
  const W = opts.W ?? 1100, laneH = opts.laneH ?? 44, left = opts.left ?? 170, right = 24, top = 16, bottom = 34;
  const H = top + laneH * topics.length + bottom;
  const ts = papers.map(when);
  const x0 = Math.floor(Math.min(...ts)), x1 = Math.ceil(Math.max(...ts) + 1e-9);
  const sx = (t: number) => left + ((t - x0) / (x1 - x0)) * (W - left - right);
  const lanes = topics.map((t, i) => ({ id: t.id, label: t.short_name ?? t.name, y: top + laneH * i + laneH / 2 }));
  const laneY = new Map(lanes.map((l) => [l.id, l.y]));
  const dots = papers.flatMap((p) => p.topics.filter((t) => laneY.has(t)).map((t) => ({
    pid: p.id, topic: t, cx: +sx(when(p)).toFixed(1), cy: +(laneY.get(t)! + jitter(p.id + t) * laneH * 0.3).toFixed(1),
  })));
  const years: number[] = [];
  for (let y = x0; y <= x1; y++) years.push(y);
  return { W, H, left, right, top, bottom, laneH, x0, x1, years, lanes, dots };
}

/** Records per topic and year (papers only), for the heatmap. */
export function topicYearCounts() {
  const years = [...new Set(papers.map((p) => p.year))].sort((a, b) => a - b);
  const rows = topics.map((t) => ({ id: t.id, label: t.short_name ?? t.name,
    cells: years.map((y) => papers.filter((p) => p.year === y && p.topics.includes(t.id)).length) }));
  const max = Math.max(1, ...rows.flatMap((r) => r.cells));
  return { years, rows, max };
}
