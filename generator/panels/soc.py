"""Panel 3 — SOC console: radar of recently-pushed repos, KPIs, threat level, alert feed, 30-day sparkline."""

from __future__ import annotations

import datetime as dt
import math
import zlib

from ..svg import AMBER, CYAN, DIM, EDGE, GREEN, MAGENTA, PANEL, RED, clip, document, esc, text, titlebar

CSS = """
.sweep { animation: spin 4s linear infinite; transform-origin: 150px 182px; }
@keyframes spin { to { transform: rotate(360deg); } }
.blip { animation: blip 4s ease-out infinite; }
@keyframes blip { 0% { opacity: 1; } 70% { opacity: .15; } 100% { opacity: 1; } }
.draw { stroke-dasharray: 1400; stroke-dashoffset: 1400; animation: draw 2.4s ease-out .6s forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
.seg { opacity: 0; animation: fade .2s forwards; }
"""

LEVELS = [("LOW", GREEN), ("GUARDED", CYAN), ("ELEVATED", AMBER), ("HIGH", MAGENTA), ("CRITICAL", RED)]


def kpi(x, y, label, value, unit, color, delay):
    return (
        f'<g class="fade" style="animation-delay:{delay:.2f}s">'
        f'<rect x="{x}" y="{y}" width="124" height="60" rx="6" fill="{PANEL}" stroke="{EDGE}"/>'
        f'<rect x="{x}" y="{y}" width="3" height="60" rx="1.5" fill="{color}"/>'
        + text(x + 12, y + 18, label, "dim", 9.5)
        + f'<text x="{x + 12}" y="{y + 46}" font-size="24" font-weight="700" fill="{color}" filter="url(#glow)" '
        f'style="fill:{color}">{esc(value)}<tspan font-size="11" dx="4" style="fill:{DIM}">{esc(unit)}</tspan></text></g>'
    )


def render(cfg: dict, data: dict, st: dict) -> str:
    today = st["today"]
    body = [titlebar(f"SOC // threat intel on @{data['login']} — Security Operations Center", "● MONITORING")]

    # ---- radar
    cx, cy, R = 150, 182, 118
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{PANEL}" stroke="{GREEN}" stroke-opacity=".5"/>')
    for k in (0.33, 0.66):
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{R * k:.0f}" fill="none" stroke="{GREEN}" stroke-opacity=".22"/>')
    body.append(f'<path d="M{cx - R} {cy}H{cx + R}M{cx} {cy - R}V{cy + R}" stroke="{GREEN}" stroke-opacity=".22"/>')
    body.append(
        f'<defs><radialGradient id="sw" cx="0" cy="1" r="1"><stop offset="0" stop-color="{GREEN}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient></defs>'
        f'<g class="sweep"><path d="M{cx} {cy}L{cx} {cy - R}A{R} {R} 0 0 1 {cx + R * math.sin(math.radians(40)):.1f} '
        f'{cy - R * math.cos(math.radians(40)):.1f}Z" fill="url(#sw)" opacity=".7"/>'
        f'<path d="M{cx} {cy}V{cy - R}" stroke="{GREEN}" stroke-width="1.5"/></g>'
    )
    recent = [r for r in data["repos"] if not r.get("archived")][:6]
    for r in recent:
        age = (today - dt.date.fromisoformat(r["pushed_at"][:10])).days
        dist = min(R - 14, 20 + (R - 34) * math.log1p(age) / math.log1p(400))
        ang = math.radians(zlib.crc32(r["name"].encode()) % 360)
        bx, by = cx + dist * math.sin(ang), cy - dist * math.cos(ang)
        delay = (math.degrees(ang) % 360) / 360 * 4
        col = MAGENTA if age <= 7 else CYAN
        body.append(f'<g class="blip" style="animation-delay:{delay:.2f}s"><circle cx="{bx:.1f}" cy="{by:.1f}" r="3.5" '
                    f'fill="{col}" filter="url(#glow)"/>'
                    + text(round(bx + (6 if bx < cx else -6)), round(by - 5), clip(r["name"], 16), "", 8.5,
                           "start" if bx < cx else "end", f'style="fill:{col}"') + "</g>")
    body.append(text(cx, cy + R + 16, "radar: repos by last push (center = today)", "dim", 9, "middle"))

    # ---- KPIs
    kx, ky = 300, 50
    body.append(kpi(kx, ky, "EVENTS / 365D", f"{data['total']:,}".replace(",", " "), "evt", CYAN, 0.2))
    body.append(kpi(kx + 134, ky, "CURRENT STREAK", st["current_streak"], "days", GREEN, 0.35))
    body.append(kpi(kx, ky + 70, "LONGEST STREAK", st["longest_streak"], "days", MAGENTA, 0.5))
    body.append(kpi(kx + 134, ky + 70, "PEAK DAY", st["best_day"]["count"], "evt", AMBER, 0.65))

    # ---- threat level (= activity of the last 7 days)
    lvl = min(4, int(st["last7"] / 12)) if st["last7"] else 0
    name, col = LEVELS[lvl]
    ty = 202
    body.append(text(kx, ty, "THREAT LEVEL", "dim", 9.5))
    body.append(text(kx + 258, ty, f"{name} · {st['last7']} evt/7d", "b", 10, "end", f'style="fill:{col}"'))
    for i in range(20):
        on = i < (lvl + 1) * 4
        c = LEVELS[i // 4][1] if on else EDGE
        body.append(f'<rect class="seg" style="animation-delay:{0.9 + i * 0.05:.2f}s" x="{kx + i * 13}" y="{ty + 8}" '
                    f'width="10" height="12" rx="1.5" fill="{c}"/>')

    # ---- alert feed
    ax, ay = 584, 56
    body.append(f'<rect x="{ax - 12}" y="{ay - 14}" width="{840 - ax - 4}" height="176" rx="6" fill="{PANEL}" stroke="{EDGE}"/>')
    body.append(text(ax, ay, "ALERTS · journalctl -f", "dim", 9.5))
    last = data["repos"][0] if data["repos"] else {"name": "-", "pushed_at": today.isoformat()}
    top = max(data["repos"], key=lambda r: r["stars"]) if data["repos"] else {"name": "-", "stars": 0}
    streak = st["current_streak"]
    alerts = [
        ("INFO", CYAN, f"push on {last['name']}"),
        ("INFO", CYAN, f"{top['stars']}★ watching {top['name']}"),
        ("WARN", AMBER, f"streak {streak}d: no sleep detected") if streak >= 3
        else ("INFO", CYAN, "operator idle: tuning automations"),
        ("CRIT", RED, f"peak {st['best_day']['count']} evt on {st['best_day']['date'][5:]}"),
        ("INFO", CYAN, f"{data['prs']} PRs · {data['issues']} issues /365d"),
        ("OK", GREEN, "honeypots quiet · capteurs au vert"),
        ("WARN", AMBER, "café.service: niveau bas"),
    ]
    for i, (sev, c, msg) in enumerate(alerts):
        y = ay + 20 + i * 20
        stamp = (dt.datetime(2000, 1, 1, 8, 2) + dt.timedelta(minutes=37 * i + 3 * i * i)).strftime("%H:%M")
        body.append(
            f'<g class="fade" style="animation-delay:{1.0 + i * 0.35:.2f}s"><text x="{ax}" y="{y}" font-size="10" xml:space="preserve">'
            f'<tspan style="fill:{DIM}">{stamp}</tspan> <tspan font-weight="700" style="fill:{c}">{sev:<4}</tspan> '
            f'{esc(clip(msg, 27))}</text></g>'
        )

    # ---- sparkline (last 30 days)
    sx, sy, sw, sh = 300, 248, 524, 78
    pts = st["last30"] or [0]
    mx = max(pts) or 1
    step = sw / max(len(pts) - 1, 1)
    coords = [(sx + i * step, sy + sh - (v / mx) * (sh - 8)) for i, v in enumerate(pts)]
    line = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in coords)
    body.append(text(sx, sy - 6, "ACTIVITY · last 30 days", "dim", 9.5))
    body.append(text(sx + sw, sy - 6, f"Σ {sum(pts)} evt", "cyan", 9.5, "end"))
    body.append(f'<defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/>'
                f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient></defs>')
    body.append(f'<path class="fade" style="animation-delay:1.8s" d="{line}L{sx + sw} {sy + sh}L{sx} {sy + sh}Z" fill="url(#area)"/>')
    body.append(f'<path class="draw" d="{line}" fill="none" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>')
    body.append(f'<path d="M{sx} {sy + sh}H{sx + sw}" stroke="{EDGE}"/>')
    lx, ly = coords[-1]
    body.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{MAGENTA}" class="pulse" filter="url(#glow)"/>')
    return document(sy + sh + 20, "\n".join(body), "SOC dashboard built from GitHub activity", CSS)
