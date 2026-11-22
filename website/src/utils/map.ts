// Geometry for the animated topic map (shared by the home page and topic pages).
import type { Topic } from './data';

export interface MapNode { id: string; name: string; full: string; x: number; y: number; lx: number; ly: number; anchor: 'start' | 'middle' | 'end'; hue: number }
export interface MapEdge { a: string; b: string; d: string }

export const W = 960, H = 600, CX = W / 2, CY = H / 2;

export function layout(topics: Topic[]): { nodes: MapNode[]; edges: MapEdge[]; spokes: MapEdge[] } {
  const n = topics.length;
  const rx = 300, ry = 205;
  const nodes = topics.map((t, i) => {
    const ang = -Math.PI / 2 + (2 * Math.PI * i) / n;
    const x = CX + rx * Math.cos(ang), y = CY + ry * Math.sin(ang);
    const c = Math.cos(ang);
    const anchor: MapNode['anchor'] = Math.abs(c) < 0.25 ? 'middle' : c > 0 ? 'start' : 'end';
    const lx = x + (anchor === 'middle' ? 0 : c > 0 ? 18 : -18);
    const ly = y + (anchor === 'middle' ? (Math.sin(ang) < 0 ? -22 : 32) : 5);
    return { id: t.id, name: t.short_name ?? t.name, full: t.name, x, y, lx, ly, anchor, hue: Math.round((360 * i) / n + 230) % 360 };
  });
  const pos = new Map(nodes.map((p) => [p.id, p]));
  const seen = new Set<string>();
  const edges: MapEdge[] = [];
  for (const t of topics) {
    for (const r of t.related_topics ?? []) {
      const key = [t.id, r].sort().join('|');
      if (seen.has(key) || !pos.has(r)) continue;
      seen.add(key);
      const p = pos.get(t.id)!, q = pos.get(r)!;
      // curve bends toward the centre so edges read as a network, not a polygon
      const mx = (p.x + q.x) / 2, my = (p.y + q.y) / 2;
      const kx = mx + (CX - mx) * 0.45, ky = my + (CY - my) * 0.45;
      edges.push({ a: t.id, b: r, d: `M${p.x.toFixed(1)},${p.y.toFixed(1)} Q${kx.toFixed(1)},${ky.toFixed(1)} ${q.x.toFixed(1)},${q.y.toFixed(1)}` });
    }
  }
  const spokes = nodes.map((p) => ({ a: 'core', b: p.id, d: `M${CX},${CY} L${p.x.toFixed(1)},${p.y.toFixed(1)}` }));
  return { nodes, edges, spokes };
}
