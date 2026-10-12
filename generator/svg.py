"""Shared palette and SVG helpers.

GitHub serves README images through a sandboxed <img>: no JS, no external fonts.
Everything is pure SVG + CSS keyframes + SMIL, which GitHub renders fine.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

W = 840
FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"

BG = "#070b12"
PANEL = "#0c1320"
EDGE = "#1c2a3d"
GRID = "#132033"
TEXT = "#c9d6e5"
DIM = "#5c6f88"
CYAN = "#00e5ff"
MAGENTA = "#ff2fd0"
GREEN = "#39ff88"
AMBER = "#ffb547"
RED = "#ff4d6d"

HEAT = ["#111a28", "#0a4452", "#087c8f", "#00b8d4", "#7af6ff"]

BASE_CSS = f"""
text {{ font-family: {FONT}; fill: {TEXT}; }}
.dim {{ fill: {DIM}; }}
.cyan {{ fill: {CYAN}; }} .mag {{ fill: {MAGENTA}; }} .green {{ fill: {GREEN}; }}
.amber {{ fill: {AMBER}; }} .red {{ fill: {RED}; }}
.b {{ font-weight: 700; }}
.fade {{ opacity: 0; animation: fade .35s ease-out forwards; }}
@keyframes fade {{ to {{ opacity: 1; }} }}
.blink {{ animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.pulse {{ animation: pulse 2.4s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
.scan {{ animation: scan 7s linear infinite; }}
@keyframes scan {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY(var(--h)); }} }}
"""

DEFS = f"""
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="2.2" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="5" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<linearGradient id="neon" x1="0" x2="1" y1="0" y2="0">
  <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{MAGENTA}"/>
</linearGradient>
<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
  <path d="M20 0H0V20" fill="none" stroke="{GRID}" stroke-width=".6"/>
</pattern>
<linearGradient id="scanline" x1="0" x2="0" y1="0" y2="1">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{CYAN}" stop-opacity=".07"/>
  <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
</linearGradient>
"""


def esc(s: object) -> str:
    return escape(str(s), {'"': "&quot;"})


def clip(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def text(x, y, s, cls="", size=12, anchor="start", extra="") -> str:
    c = f' class="{cls}"' if cls else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{x}" y="{y}" font-size="{size}"{c}{a} xml:space="preserve" {extra}>{esc(s)}</text>'


def document(h: int, body: str, title: str, css: str = "") -> str:
    """A full console 'screen': dark rounded frame, grid backdrop, sweeping scanline."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<defs>{DEFS}</defs>
<style>{BASE_CSS}{css}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{EDGE}"/>
<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="14" fill="url(#grid)" opacity=".55"/>
{body}
<rect class="scan" style="--h:{h}px" x="1" y="0" width="{W - 2}" height="40" fill="url(#scanline)"/>
</svg>
"""


def titlebar(label: str, right: str = "") -> str:
    dots = "".join(
        f'<circle cx="{22 + i * 16}" cy="18" r="5" fill="{c}"/>' for i, c in enumerate((RED, AMBER, GREEN))
    )
    out = [
        f'<path d="M1 34H{W - 1}" stroke="{EDGE}"/>',
        dots,
        text(W / 2, 22, label, "dim", 11, "middle"),
    ]
    if right:
        out.append(text(W - 18, 22, right, "green pulse", 10, "end"))
    return "\n".join(out)
