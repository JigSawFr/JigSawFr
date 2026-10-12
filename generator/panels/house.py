"""Panel 2 — the smart-home floorplan: 1 room = 1 month, 1 floor tile = 1 day of contributions."""

from __future__ import annotations

import datetime as dt
import math

from ..svg import AMBER, CYAN, DIM, EDGE, GREEN, HEAT, MAGENTA, PANEL, document, text

MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()

CSS = """
.tile { opacity: 0; animation: fade .4s ease-out forwards; }
.hot { animation: fade .4s ease-out forwards, flick 3.2s ease-in-out infinite; }
@keyframes flick { 0%,100% { opacity: 1; } 50% { opacity: .55; } }
.wave { animation: wave 2.6s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes wave { from { transform: scale(.2); opacity: .9; } to { transform: scale(1.6); opacity: 0; } }
.ring { animation: ring 1.8s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes ring { from { transform: scale(.4); opacity: 1; } to { transform: scale(2.4); opacity: 0; } }
.hotspot { animation: hs 1.6s ease-in-out infinite; }
@keyframes hs { 0%,100% { stroke-opacity: 1; } 50% { stroke-opacity: .25; } }
"""


def level(count: int, peak: int) -> int:
    if count <= 0:
        return 0
    return min(4, 1 + int(3 * math.log1p(count) / math.log1p(max(peak, 1))))


def device(kind: str, x: float, y: float, on: bool, power: float) -> str:
    """Tiny neon line-art devices. `power` (0..1) drives the glow."""
    c = CYAN if on else DIM
    op = 0.35 + 0.65 * power if on else 0.6
    g = f'<g transform="translate({x},{y})" stroke="{c}" fill="none" stroke-width="1.6" opacity="{op:.2f}"' + (
        ' filter="url(#glow)">' if on else ">")
    if kind == "bulb":
        s = (f'<circle cx="0" cy="-4" r="9" fill="{c}" fill-opacity="{0.35 * power if on else 0:.2f}"/>'
             '<path d="M-4 6h8M-3 10h6M-4 4v2M4 4v2"/>')
    elif kind == "thermo":
        s = ('<circle r="11"/><path d="M-7 5A8 8 0 1 1 7 5" stroke-width="2.4" stroke-dasharray="30 60"/>'
             f'<text x="0" y="3" font-size="8" text-anchor="middle" stroke="none" fill="{c}">{19 + round(4 * power)}°</text>')
    elif kind == "lock":
        s = '<rect x="-8" y="-2" width="16" height="12" rx="2"/><path d="M-5 -2v-4a5 5 0 0 1 10 0v4"/><circle cy="4" r="1.6"/>'
    elif kind == "camera":
        s = ('<rect x="-11" y="-6" width="15" height="11" rx="2"/><path d="M4 -2l7 -4v11l-7 -4z"/>'
             f'<circle cx="-7" cy="-2" r="1.6" fill="{AMBER if on else DIM}" stroke="none" class="{"blink" if on else ""}"/>')
    elif kind == "sensor":
        s = '<circle r="3"/><path d="M-7 -7a10 10 0 0 0 0 14M7 -7a10 10 0 0 1 0 14M-11 -11a16 16 0 0 0 0 22M11 -11a16 16 0 0 1 0 22"/>'
    else:  # server rack
        s = "".join(
            f'<rect x="-11" y="{-12 + i * 8}" width="22" height="6" rx="1"/>'
            f'<circle cx="7" cy="{-9 + i * 8}" r="1.3" fill="{GREEN if on else DIM}" stroke="none" '
            f'class="{"blink" if on else ""}" style="animation-delay:{i * 0.3:.1f}s"/>'
            for i in range(3)
        )
    return g + s + "</g>"


def render(cfg: dict, data: dict, st: dict) -> str:
    months = st["months"]
    peak = st["max_day"]
    totals = [sum(d["count"] for d in days) for _, days in months]
    hot_idx = max(range(len(totals)), key=totals.__getitem__) if totals else -1
    month_peak = max(totals or [1]) or 1
    rooms = cfg["rooms"]

    X0, ROOF_BASE, COLS = 30, 128, 4
    HX, HW, RH, GAP = X0 - 8, 840 - 2 * (X0 - 8), 142, 10
    w = (HW - (COLS + 1) * GAP) / COLS
    TILE, STEP = 12, 16
    body = []

    # roof + antenna mesh
    apex = (420, 52)
    body.append(f'<path d="M{X0 - 8} {ROOF_BASE} L{apex[0]} {apex[1]} L{840 - X0 + 8} {ROOF_BASE}" fill="none" '
                f'stroke="url(#neon)" stroke-width="2.5" filter="url(#glow)"/>')
    body.append(f'<path d="M{apex[0]} {apex[1]}V24" stroke="{CYAN}" stroke-width="2"/><circle cx="{apex[0]}" cy="22" r="3" fill="{MAGENTA}"/>')
    for i in range(3):
        body.append(f'<circle class="wave" style="animation-delay:{i * 0.85:.2f}s" cx="{apex[0]}" cy="22" r="18" '
                    f'fill="none" stroke="{CYAN}" stroke-width="1.2"/>')
    body.append(text(apex[0], 92, "SMART-HOME // CONTRIBUTION FLOORPLAN", "b cyan", 14, "middle"))
    body.append(text(apex[0], 110, "1 room = 1 month · 1 tile = 1 day · 1 pièce = 1 mois", "dim", 10.5, "middle"))
    body.append(text(X0 + 4, 30, f"zigbee/mqtt mesh · {len([t for t in totals if t])}/{len(totals)} rooms online", "dim", 10))
    body.append(text(840 - X0 - 4, 30, f"{data['total']} events · 365d", "green", 10, "end"))

    rows = math.ceil(len(months) / COLS)
    house_h = rows * (RH + GAP) + GAP
    body.append(f'<rect x="{HX}" y="{ROOF_BASE}" width="{HW}" height="{house_h}" rx="4" '
                f'fill="{PANEL}" fill-opacity=".6" stroke="{CYAN}" stroke-opacity=".6" stroke-width="2"/>')

    today = st["today"]
    for idx, (ym, days) in enumerate(months):
        r, c = divmod(idx, COLS)
        x = HX + GAP + c * (w + GAP)
        y = ROOF_BASE + GAP + r * (RH + GAP)
        room = rooms[idx % len(rooms)]
        total = totals[idx]
        power = total / month_peak
        is_hot = idx == hot_idx and total > 0
        is_live = ym == today.isoformat()[:7]
        stroke = MAGENTA if is_hot else (CYAN if total else EDGE)
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{RH}" rx="3" fill="{CYAN}" fill-opacity="{0.06 * power:.3f}" '
                    f'stroke="{stroke}" stroke-opacity="{1 if is_hot else 0.45}" class="{"hotspot" if is_hot else ""}"/>')
        # door gap, purely decorative
        body.append(f'<path d="M{x + w - 30} {y + RH}h18" stroke="{PANEL}" stroke-width="3"/>')
        mon = MONTHS[int(ym[5:]) - 1]
        body.append(text(x + 8, y + 16, f"{mon} · {room['name']}", "b", 10.5))
        if is_hot:
            body.append(text(x + w - 8, y + 16, "HOTSPOT", "mag b", 9, "end"))
        elif is_live:
            body.append(text(x + w - 8, y + 16, "● LIVE", "green b pulse", 9, "end"))

        # floor tiles (weekday columns, week rows)
        first = dt.date.fromisoformat(f"{ym}-01")
        offset = first.weekday()
        for d in days:
            day = dt.date.fromisoformat(d["date"])
            pos = day.day - 1 + offset
            tx = x + 8 + (pos % 7) * STEP
            ty = y + 26 + (pos // 7) * STEP
            lv = level(d["count"], peak)
            cls = "tile hot" if lv == 4 else "tile"
            delay = 0.15 + idx * 0.12 + (pos % 7) * 0.02
            body.append(f'<rect class="{cls}" style="animation-delay:{delay:.2f}s" x="{tx}" y="{ty}" width="{TILE}" '
                        f'height="{TILE}" rx="2.5" fill="{HEAT[lv]}"><title>{d["date"]}: {d["count"]}</title></rect>')

        # device + readout
        dx = x + w - 30
        body.append(device(room["device"], dx, y + 62, total > 0, power))
        body.append(text(dx, y + 100, str(total), "b cyan" if total else "dim", 16, "middle"))
        body.append(text(dx, y + 114, "events", "dim", 9, "middle"))
        state = "ON" if total else "OFF"
        body.append(text(dx, y + 130, state, "green" if total else "dim", 9, "middle"))
        if is_live:
            body.append(f'<circle class="ring" cx="{x + w - 12}" cy="{y + RH - 10}" r="4" fill="none" stroke="{GREEN}"/>')

    # legend
    ly = ROOF_BASE + house_h + 26
    body.append(text(X0, ly, f"best day {st['best_day']['date']} → {st['best_day']['count']} events", "dim", 10.5))
    lx = 840 - X0 - 5 * 16 - 40
    body.append(text(lx - 8, ly, "less", "dim", 10, "end"))
    for i, col in enumerate(HEAT):
        body.append(f'<rect x="{lx + i * 16}" y="{ly - 10}" width="12" height="12" rx="2.5" fill="{col}"/>')
    body.append(text(lx + 5 * 16 + 4, ly, "more", "dim", 10))
    return document(ly + 18, "\n".join(body), "Smart-home floorplan built from GitHub contributions", CSS)
