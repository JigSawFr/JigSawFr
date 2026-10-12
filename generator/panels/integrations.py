"""Panel 4 — Home Assistant style 'Devices & services' grid + language power meters."""

from __future__ import annotations

from ..svg import CYAN, DIM, EDGE, GREEN, MAGENTA, PANEL, AMBER, clip, document, text

CSS = """
.card { opacity: 0; animation: pop .45s cubic-bezier(.2,1.4,.4,1) forwards; transform-box: fill-box; transform-origin: center; }
@keyframes pop { from { opacity: 0; transform: scale(.85); } to { opacity: 1; transform: scale(1); } }
.bar { transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: grow 1.2s ease-out forwards; }
@keyframes grow { to { transform: scaleX(1); } }
"""

LANG_COLORS = [CYAN, MAGENTA, GREEN, AMBER, "#7aa2ff", "#ff7a59"]


def render(cfg: dict, data: dict, st: dict) -> str:
    items = cfg["integrations"]
    body = [text(24, 34, "INTEGRATIONS", "b cyan", 14),
            text(150, 34, "Settings › Devices & services · Paramètres › Appareils et services", "dim", 10.5),
            text(816, 34, f"{len(items)}/{len(items)} online", "green", 10.5, "end")]

    cols, gap, x0, y0 = 4, 12, 24, 50
    cw, ch = (840 - 2 * x0 - (cols - 1) * gap) / cols, 62
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        x, y = x0 + c * (cw + gap), y0 + r * (ch + gap)
        col = it.get("color", CYAN)
        delay = 0.15 + i * 0.12
        body.append(
            f'<g class="card" style="animation-delay:{delay:.2f}s">'
            f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="10" fill="{PANEL}" stroke="{EDGE}"/>'
            f'<circle cx="{x + 30:.1f}" cy="{y + ch / 2}" r="18" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-width="1.5" filter="url(#glow)"/>'
            + text(round(x + 30, 1), y + ch / 2 + 4, it["short"], "b", 10 if len(it["short"]) > 2 else 11.5, "middle", f'style="fill:{col}"')
            + text(round(x + 58, 1), y + 27, clip(it["name"], 16), "b", 12)
            + text(round(x + 58, 1), y + 44, clip(it["kind"], 20), "dim", 10)
            + f'<circle cx="{x + cw - 14:.1f}" cy="{y + 14}" r="3.5" fill="{GREEN}" class="pulse" '
            f'style="animation-delay:{i * 0.3:.1f}s" filter="url(#glow)"/></g>'
        )

    rows = -(-len(items) // cols)
    ly = y0 + rows * (ch + gap) + 22
    body.append(text(24, ly, "POWER USAGE BY LANGUAGE", "b cyan", 12))
    body.append(text(816, ly, "public repos · bytes of code", "dim", 10, "end"))
    langs = data["languages"][:6]
    total = sum(v for _, v in langs) or 1
    bw = (840 - 2 * x0 - 20) / 2
    for i, (name, v) in enumerate(langs):
        r, c = divmod(i, 2)
        x, y = x0 + c * (bw + 20), ly + 18 + r * 26
        pct = v / total
        col = LANG_COLORS[i % len(LANG_COLORS)]
        body.append(text(x, y + 10, clip(name, 12), "", 11))
        body.append(f'<rect x="{x + 104}" y="{y + 1}" width="{bw - 160:.1f}" height="10" rx="5" fill="{EDGE}"/>')
        body.append(f'<rect class="bar" style="animation-delay:{0.8 + i * 0.15:.2f}s" x="{x + 104}" y="{y + 1}" '
                    f'width="{max(4, (bw - 160) * pct / langs[0][1] * total):.1f}" height="10" rx="5" fill="{col}" filter="url(#glow)"/>')
        body.append(text(round(x + bw - 4, 1), y + 10, f"{pct * 100:.1f}%", "", 11, "end", f'style="fill:{col}"'))
    h = ly + 18 + (-(-len(langs) // 2)) * 26 + 8
    return document(h, "\n".join(body), "Home-lab integrations and languages", CSS)
