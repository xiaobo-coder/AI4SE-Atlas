#!/usr/bin/env python3
"""Generate assets/atlas-map.svg, the animated topic map shown in the README.

The geometry mirrors website/src/utils/map.ts. The SVG is self-contained
(CSS animation only, no scripts or external resources) so GitHub can render it,
and it stops moving for viewers who prefer reduced motion.

Usage: python scripts/make_map_svg.py [--check]
"""
from __future__ import annotations

import argparse
import html
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "atlas-map.svg"
W, H = 960, 600
CX, CY, RX, RY = W / 2, H / 2, 300, 205


def build(topics: list[dict]) -> str:
    n = len(topics)
    nodes = []
    for i, t in enumerate(topics):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        x, y = CX + RX * math.cos(ang), CY + RY * math.sin(ang)
        c = math.cos(ang)
        anchor = "middle" if abs(c) < 0.25 else ("start" if c > 0 else "end")
        lx = x + (0 if anchor == "middle" else (18 if c > 0 else -18))
        ly = y + ((-22 if math.sin(ang) < 0 else 34) if anchor == "middle" else 5)
        hue = round(360 * i / n + 230) % 360
        nodes.append(dict(id=t["id"], name=t.get("short_name") or t["name"], x=x, y=y, lx=lx, ly=ly, anchor=anchor, hue=hue))
    pos = {p["id"]: p for p in nodes}
    seen, edges = set(), []
    for t in topics:
        for r in t.get("related_topics") or []:
            key = tuple(sorted((t["id"], r)))
            if key in seen or r not in pos:
                continue
            seen.add(key)
            p, q = pos[t["id"]], pos[r]
            mx, my = (p["x"] + q["x"]) / 2, (p["y"] + q["y"]) / 2
            kx, ky = mx + (CX - mx) * 0.45, my + (CY - my) * 0.45
            edges.append(f"M{p['x']:.1f},{p['y']:.1f} Q{kx:.1f},{ky:.1f} {q['x']:.1f},{q['y']:.1f}")

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
           '<title id="t">AI4SE Atlas topic map</title>',
           f'<desc id="d">AI4SE research topics in a ring; curves connect related topics.</desc>',
           """<style>
.e{fill:none;stroke:url(#g);stroke-width:1.8;stroke-dasharray:4 6;animation:f 2.4s linear infinite}
.r{animation:p 3.2s ease-out infinite;transform-box:fill-box}
.dot{animation:m var(--d) linear infinite;offset-rotate:0deg}
.l{font:600 15px -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;fill:#e2e8f0}
@keyframes f{to{stroke-dashoffset:-40}}
@keyframes p{0%{r:9px;opacity:.6}80%,100%{r:24px;opacity:0}}
@keyframes m{from{offset-distance:0%}to{offset-distance:100%}}
@media (prefers-reduced-motion:reduce){.e,.r,.dot{animation:none}.dot{display:none}}
</style>""",
           '<defs><radialGradient id="glow"><stop offset="0" stop-color="#6366f1" stop-opacity=".45"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>'
           '<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#818cf8"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>'
           '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#111a33"/></linearGradient></defs>',
           f'<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>',
           f'<ellipse cx="{CX}" cy="{CY}" rx="380" ry="260" fill="url(#glow)"/>',
           f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="#fff" stroke-opacity=".08"/>']
    out.append('<g stroke="#fff" stroke-opacity=".06">' + "".join(f'<path d="M{CX},{CY} L{p["x"]:.1f},{p["y"]:.1f}"/>' for p in nodes) + "</g>")
    out.append("<g>" + "".join(f'<path class="e" d="{d}"/>' for d in edges) + "</g>")
    out.append("<g>" + "".join(
        f'<circle r="3.4" class="dot" fill="{"#22d3ee" if i % 2 else "#c7d2fe"}" style="offset-path:path(\'{d}\');--d:{4 + (i % 5) * 0.9:.1f}s;animation-delay:-{i * 0.7:.1f}s"/>'
        for i, d in enumerate(edges)) + "</g>")
    out.append(f'<circle cx="{CX}" cy="{CY}" r="50" fill="#6366f1" fill-opacity=".15" stroke="#818cf8" stroke-opacity=".6"/>'
               f'<text x="{CX}" y="{CY - 2}" text-anchor="middle" style="font:700 22px -apple-system,Segoe UI,Roboto,Arial,sans-serif;fill:#fff">AI4SE</text>'
               f'<text x="{CX}" y="{CY + 20}" text-anchor="middle" style="font:600 11px -apple-system,Segoe UI,Roboto,Arial,sans-serif;letter-spacing:3px;fill:#94a3b8">ATLAS</text>')
    for i, p in enumerate(nodes):
        col = f"hsl({p['hue']},80%,60%)"
        out.append(f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="9" fill="{col}" class="r" style="animation-delay:-{i * 0.32:.2f}s"/>'
                   f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="9" fill="{col}" stroke="#0b1020" stroke-width="3"/>'
                   f'<text class="l" x="{p["lx"]:.1f}" y="{p["ly"]:.1f}" text-anchor="{p["anchor"]}">{html.escape(p["name"])}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the committed SVG is out of date")
    args = ap.parse_args(argv)
    data = ROOT / "data"
    topics = yaml.safe_load((data / "topics.yaml").read_text(encoding="utf-8")) or []
    svg = build(topics)
    if args.check:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == svg
        print("atlas-map.svg is current" if ok else "atlas-map.svg is out of date: run python scripts/make_map_svg.py")
        return 0 if ok else 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
