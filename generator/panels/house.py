"""Panel 2 — isometric smart home.

The garden in front of the house is the contribution calendar in 3D: 1 pillar = 1 day (height = events).
The 12 front windows are the last 12 months (top floor = older), brightness = activity.
Seasonal decorations / particles come from the active theme (seasons.py).
"""

from __future__ import annotations

import datetime as dt
import math
import random

from ..svg import DIM, EDGE, GREEN, RED, THEME, document, esc, shade, text

S = 12                      # iso unit (px)
CX, CY = 0.866 * S, 0.5 * S
OX, OY = 181, 112           # screen position of world origin
H = 512

HX0, HX1, HY0, HY1, WALL = 30, 44, -13, -3, 7.5   # house footprint & wall height
RIDGE_Y, RIDGE_Z, EAVE_Z = -8, 11.05, 7.15


def P(x, y, z=0.0):
    return OX + (x - y) * CX, OY + (x + y) * CY - z * S


def pts(points) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def poly(points, fill, extra="") -> str:
    return f'<polygon points="{pts(points)}" fill="{fill}" {extra}/>'


def box(x, y, z, dx, dy, dz, color, extra="", top_extra="") -> str:
    """Iso box; visible faces: top, +y (lower-left), +x (lower-right)."""
    top = [P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
    left = [P(x, y + dy, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
    right = [P(x + dx, y, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x + dx, y, z + dz)]
    return (poly(left, shade(color, 0.7), extra) + poly(right, shade(color, 0.48), extra)
            + poly(top, color, extra + " " + top_extra))


CSS = """
.rise { opacity: 0; animation: rise .7s cubic-bezier(.2,1.3,.4,1) forwards; }
@keyframes rise { from { opacity: 0; transform: translateY(22px); } to { opacity: 1; transform: none; } }
.sweep { opacity: 0; animation: sweep 7s ease-in-out infinite; }
@keyframes sweep { 0%, 10%, 100% { opacity: 0; } 5% { opacity: .55; } }
.flick { animation: flick 2.8s ease-in-out infinite; }
@keyframes flick { 0%,100% { opacity: 1; } 40% { opacity: .55; } 45% { opacity: .9; } 60% { opacity: .4; } }
.wave { animation: wave 2.6s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes wave { from { transform: scale(.2); opacity: .9; } to { transform: scale(1.6); opacity: 0; } }
.smoke { animation: smoke 4.5s ease-out infinite; opacity: 0; transform-box: fill-box; transform-origin: center; }
@keyframes smoke { 0% { opacity: .6; transform: translate(0,0) scale(.4); } 100% { opacity: 0; transform: translate(16px,-46px) scale(2); } }
.twinkle { animation: tw 3s ease-in-out infinite; }
@keyframes tw { 0%,100% { opacity: .9; } 50% { opacity: .15; } }
.bob { animation: bob 3.5s ease-in-out infinite; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.burst { animation: burst 2.6s ease-out infinite; opacity: 0; transform-box: fill-box; transform-origin: center; }
@keyframes burst { 0% { opacity: 1; transform: scale(.05); } 65% { opacity: 1; } 100% { opacity: 0; transform: scale(1); } }
.spin { animation: spin 30s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spin { to { transform: rotate(360deg); } }
.fly { animation: fly .9s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes fly { 50% { transform: scaleY(.35); } }
.beam { animation: beam 2s ease-in-out infinite; }
@keyframes beam { 0%,100% { opacity: .25; } 50% { opacity: 1; } }
.firefly { animation: ff 4s ease-in-out infinite; }
@keyframes ff { 0%,100% { opacity: 0; transform: translate(0,0); } 50% { opacity: 1; transform: translate(6px,-10px); } }
"""


def fall_css(h: int) -> str:
    return (f"@keyframes fallA {{ from {{ transform: translate(0,-20px) rotate(0); }} to {{ transform: translate(40px,{h}px) rotate(320deg); }} }}"
            f"@keyframes fallB {{ from {{ transform: translate(0,-20px) rotate(0); }} to {{ transform: translate(-50px,{h}px) rotate(-280deg); }} }}")


# ------------------------------------------------------------------ scenery

def sky(rng: random.Random) -> str:
    out = []
    for i in range(46):
        x, y = rng.uniform(20, 820), rng.uniform(30, 230)
        if x < 430 and y < 100:          # keep the title area clean
            continue
        out.append(f'<circle class="twinkle" style="animation-delay:{rng.uniform(0, 3):.2f}s" cx="{x:.0f}" cy="{y:.0f}" '
                   f'r="{rng.uniform(.5, 1.4):.1f}" fill="#dfe8ff"/>')
    mx, my = 788, 64
    if THEME["sky"] == "sun":
        rays = "".join(f'<path d="M{mx} {my - 30}V{my - 40}" stroke="#ffd166" stroke-width="2.5" stroke-linecap="round" '
                       f'transform="rotate({a} {mx} {my})"/>' for a in range(0, 360, 30))
        out.append(f'<g class="spin">{rays}</g><circle cx="{mx}" cy="{my}" r="22" fill="#ffd166" filter="url(#softglow)"/>')
    else:
        moon = "#ffb347" if THEME["key"] == "halloween" else "#f3f1d0"
        out.append(f'<circle cx="{mx}" cy="{my}" r="24" fill="{moon}" filter="url(#softglow)" opacity=".95"/>'
                   f'<circle cx="{mx - 7}" cy="{my - 5}" r="4" fill="{shade(moon, .85)}"/>'
                   f'<circle cx="{mx + 8}" cy="{my + 7}" r="3" fill="{shade(moon, .85)}"/>')
    return "".join(out)


def fireworks(colors) -> str:
    out = []
    for i, (bx, by) in enumerate([(470, 70), (600, 46), (360, 120), (720, 150)]):
        c = colors[i % len(colors)]
        rays = "".join(
            f'<path d="M0 0L{26 * math.cos(math.radians(a)):.1f} {26 * math.sin(math.radians(a)):.1f}" stroke="{c}" '
            f'stroke-width="2" stroke-linecap="round"/><circle cx="{30 * math.cos(math.radians(a)):.1f}" '
            f'cy="{30 * math.sin(math.radians(a)):.1f}" r="1.8" fill="{colors[(i + 1) % len(colors)]}"/>'
            for a in range(0, 360, 24))
        out.append(f'<g transform="translate({bx},{by})"><g class="burst" style="animation-delay:{i * 0.65:.2f}s" '
                   f'filter="url(#glow)">{rays}</g></g>')
    return "".join(out)


def bats() -> str:
    shape = ("M0 0C-3-5-9-5-12-2C-9-2-8 0-8 2C-6 0-3 1 0 3C3 1 6 0 8 2C8 0 9-2 12-2C9-5 3-5 0 0Z")
    paths = ["M-30 90 C 150 40, 300 140, 520 70 S 760 40, 880 110",
             "M880 60 C 700 120, 560 20, 380 90 S 120 60, -30 120",
             "M-30 170 C 200 120, 380 200, 560 140 S 800 100, 880 160"]
    out = []
    for i, p in enumerate(paths):
        out.append(f'<g><g class="fly" style="animation-delay:{i * .2}s"><path d="{shape}" fill="#07040c" '
                   f'stroke="{THEME["neon"][1]}" stroke-width=".8"/></g>'
                   f'<animateMotion dur="{14 + i * 4}s" repeatCount="indefinite" begin="{-i * 3}s" path="{p}"/></g>')
    return "".join(out)


def pumpkin(x, y, r=7.0) -> str:
    return (f'<g transform="translate({x:.1f},{y:.1f})">'
            f'<ellipse rx="{r}" ry="{r * .72:.1f}" fill="#ff7b00"/>'
            f'<ellipse rx="{r * .45:.1f}" ry="{r * .72:.1f}" fill="#e56a00"/>'
            f'<path d="M0 {-r * .7:.1f}v-3" stroke="#3c8d2f" stroke-width="2"/>'
            f'<g class="flick" fill="#ffe28a" filter="url(#glow)"><path d="M{-r * .5:.1f} -1l2 -3 2 3z"/>'
            f'<path d="M{r * .5 - 4:.1f} -1l2 -3 2 3z"/><path d="M-3 2h6l-3 2z"/></g></g>')


def tree(x, y, color) -> str:
    sx, sy = P(x, y)
    return (f'<path d="M{sx:.1f} {sy:.1f}v-16" stroke="#6b4a2b" stroke-width="3"/>'
            + "".join(f'<circle cx="{sx + dx:.1f}" cy="{sy + dy:.1f}" r="{r}" fill="{shade(color, k)}"/>'
                      for dx, dy, r, k in [(-7, -18, 8, .8), (7, -19, 8, .7), (0, -27, 10, 1), (0, -16, 7, .9)]))


def pine(x, y, snowy=False, xmas=False, rng=None) -> str:
    sx, sy = P(x, y)
    out = [f'<path d="M{sx:.1f} {sy:.1f}v-8" stroke="#6b4a2b" stroke-width="3"/>']
    for i, (w, top) in enumerate([(15, 30), (12, 42), (9, 52)]):
        base = sy - 6 - i * 12
        out.append(f'<path d="M{sx - w:.1f} {base:.1f}L{sx:.1f} {sy - top - 6:.1f}L{sx + w:.1f} {base:.1f}Z" fill="#1f6b3a"/>')
        if snowy:
            out.append(f'<path d="M{sx - w * .45:.1f} {sy - top + 4:.1f}L{sx:.1f} {sy - top - 6:.1f}L{sx + w * .45:.1f} '
                       f'{sy - top + 4:.1f}Z" fill="#e8f2ff"/>')
    if xmas and rng:
        cols = ["#ff4d6d", "#ffd166", "#00e5ff", "#ff2fd0"]
        for i in range(10):
            bx, by = sx + rng.uniform(-11, 11) * (1 - i / 14), sy - 10 - i * 4.5
            out.append(f'<circle class="blink" style="animation-delay:{i * .17:.2f}s" cx="{bx:.1f}" cy="{by:.1f}" r="1.8" '
                       f'fill="{cols[i % 4]}" filter="url(#glow)"/>')
        out.append(f'<path class="beam" d="M{sx} {sy - 66}l2 5 5 0-4 3 2 5-5-3-5 3 2-5-4-3 5 0z" fill="#ffd166" filter="url(#glow)"/>')
    return "".join(out)


def snowman(x, y) -> str:
    sx, sy = P(x, y)
    return (f'<circle cx="{sx}" cy="{sy - 8}" r="9" fill="#eef4ff"/><circle cx="{sx}" cy="{sy - 22}" r="6.5" fill="#eef4ff"/>'
            f'<path d="M{sx + 2} {sy - 22}l7 1.5-7 1z" fill="#ff7b00"/><rect x="{sx - 6}" y="{sy - 34}" width="12" height="7" fill="#111"/>'
            f'<rect x="{sx - 8}" y="{sy - 28}" width="16" height="2" fill="#111"/><path d="M{sx - 6} {sy - 16}h12" stroke="#ff4d6d" stroke-width="2.5"/>')


def dead_tree(x, y) -> str:
    sx, sy = P(x, y)
    c = THEME["neon"][1]
    return (f'<path d="M{sx} {sy}v-34m0 10l-12-12m12 4l10-14m-10 6l-4-12m-8-2l-6-4m24-2l7-3" fill="none" '
            f'stroke="#2a1838" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M{sx} {sy}v-34m0 10l-12-12m12 4l10-14m-10 6l-4-12" fill="none" stroke="{c}" stroke-width=".8" opacity=".7"/>')


def ghost(x, y) -> str:
    return (f'<g transform="translate({x},{y})"><g class="bob" opacity=".85">'
            f'<path d="M-9 8V-4a9 9 0 0 1 18 0V8l-3-3-3 3-3-3-3 3-3-3z" fill="#eef1ff" filter="url(#glow)"/>'
            f'<circle cx="-3" cy="-3" r="1.6" fill="#111"/><circle cx="3" cy="-3" r="1.6" fill="#111"/></g></g>')


def gifts(x, y) -> str:
    return (box(x, y, 0, .9, .9, .8, "#ff4d6d") + box(x + 1.1, y + .2, 0, .7, .7, .6, "#ffd166")
            + box(x + .3, y + 1.2, 0, .8, .7, .5, "#39ff88"))


def flowers(rng: random.Random) -> str:
    cols = ["#ff8fd8", "#ffd166", "#ff4d6d", "#b28dff", "#7af6ff"]
    out = []
    for i in range(30):
        sx, sy = P(rng.uniform(27.3, 46.7), rng.uniform(-1.6, -1.15))
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.7" fill="{cols[i % 5]}"/>')
    return "".join(out)


def particles(kind: str, rng: random.Random) -> str:
    out = []
    n = {"snow": 70, "leaves": 22, "petals": 26, "fireflies": 22}[kind]
    for i in range(n):
        x = rng.uniform(0, 840)
        dur = rng.uniform(9, 17) if kind == "snow" else rng.uniform(10, 16)
        anim = f"{'fallA' if i % 2 else 'fallB'} {dur:.1f}s linear {-rng.uniform(0, dur):.1f}s infinite"
        if kind == "snow":
            shape = f'<circle r="{rng.uniform(.8, 2.4):.1f}" fill="#f4f8ff" opacity="{rng.uniform(.45, .95):.2f}"/>'
        elif kind == "fireflies":
            fx, fy = rng.uniform(40, 800), rng.uniform(250, 490)
            out.append(f'<circle class="firefly" style="animation-delay:{rng.uniform(0, 4):.2f}s" cx="{fx:.0f}" cy="{fy:.0f}" '
                       f'r="1.8" fill="#fff07a" filter="url(#glow)"/>')
            continue
        else:
            cols = ["#e07b39", "#c0392b", "#ffb547", "#a0522d"] if kind == "leaves" else ["#ffb3d9", "#ff8fd8", "#fff0f7"]
            shape = f'<ellipse rx="4" ry="1.9" fill="{cols[i % len(cols)]}" opacity=".9"/>'
        out.append(f'<g transform="translate({x:.0f},0)"><g style="animation:{anim}">{shape}</g></g>')
    return "".join(out)


# ------------------------------------------------------------------ the house

def house(months_power: list[float], hot: int, live: int, rng: random.Random) -> str:
    neon_a, neon_b = THEME["neon"]
    edge = f'stroke="{neon_a}" stroke-opacity=".75" stroke-width="1.2" stroke-linejoin="round"'
    snow = "snow_roof" in THEME["deco"]
    out = []

    # lot
    lawn = "#1f2a38" if THEME["particles"] == "snow" else "#0f1f1b"
    out.append(box(27, -15.5, -.35, 20, 14.5, .35, lawn, f'stroke="{EDGE}" stroke-width=".6"'))

    # walls
    front = [P(HX0, HY1, 0), P(HX1, HY1, 0), P(HX1, HY1, WALL), P(HX0, HY1, WALL)]
    side = [P(HX1, HY0, 0), P(HX1, HY1, 0), P(HX1, HY1, WALL), P(HX1, HY0, WALL)]
    out.append(poly(front, "#111b2b", edge))
    out.append(poly(side, "#0b1320", edge))
    out.append(f'<path d="M{pts([P(HX0, HY1, 3.9), P(HX1, HY1, 3.9)])}" stroke="{neon_a}" stroke-opacity=".3" stroke-dasharray="3 3"/>')

    # 12 month windows on the front wall (top floor = older months)
    win = THEME["window"]
    for i, p in enumerate(months_power):
        row, col = divmod(i, 6)
        z0 = 4.9 if row == 0 else 1.2
        x0 = HX0 + .8 + col * 2.15
        quad = [P(x0, HY1, z0), P(x0 + 1.35, HY1, z0), P(x0 + 1.35, HY1, z0 + 1.6), P(x0, HY1, z0 + 1.6)]
        if p <= 0:
            out.append(poly(quad, "#0a111c", f'stroke="{EDGE}"'))
            continue
        cls = "flick" if i == hot else ("beam" if i == live else "")
        out.append(poly(quad, win, f'fill-opacity="{.25 + .75 * p:.2f}" class="{cls}" filter="url(#glow)"'))
        mid = [P(x0 + .675, HY1, z0), P(x0 + .675, HY1, z0 + 1.6)]
        out.append(f'<polyline points="{pts(mid)}" stroke="#111b2b" stroke-width="1"/>')

    # side: door, server-room window with blinking LEDs
    door = [P(HX1, -6.3, 0), P(HX1, -4.9, 0), P(HX1, -4.9, 2.7), P(HX1, -6.3, 2.7)]
    out.append(poly(door, "#1a2740", edge))
    kx, ky = P(HX1, -5.15, 1.3)
    out.append(f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="1.2" fill="{neon_b}"/>')
    rack = [P(HX1, -11.4, 4.8), P(HX1, -9.2, 4.8), P(HX1, -9.2, 6.6), P(HX1, -11.4, 6.6)]
    out.append(poly(rack, "#050a12", edge))
    for j in range(3):
        for k in range(3):
            lx, ly = P(HX1, -11.0 + k * .7, 5.2 + j * .55)
            c = GREEN if (j + k) % 3 else RED
            out.append(f'<circle class="blink" style="animation-delay:{(j * 3 + k) * .23:.2f}s" cx="{lx:.1f}" cy="{ly:.1f}" r="1.1" fill="{c}"/>')

    # gable + round attic window
    out.append(poly([P(HX1, HY0, WALL), P(HX1, HY1, WALL), P(HX1, RIDGE_Y, RIDGE_Z - .35)], "#0b1320", edge))
    attic = [P(HX1, RIDGE_Y + .8 * math.cos(t), 8.75 + .8 * math.sin(t)) for t in [k * math.pi / 8 for k in range(16)]]
    out.append(poly(attic, win, 'fill-opacity=".8" filter="url(#glow)" class="beam"'))

    # roof: back plane, chimney, front plane
    back = [P(HX0 - .5, HY0 - .5, EAVE_Z), P(HX1 + .5, HY0 - .5, EAVE_Z), P(HX1 + .5, RIDGE_Y, RIDGE_Z), P(HX0 - .5, RIDGE_Y, RIDGE_Z)]
    out.append(poly(back, "#e8f0fa" if snow else "#162034", edge))
    out.append(box(33, -11.2, 8.6, 1.4, 1.4, 4.0, "#3a2f3a", f'stroke="{neon_a}" stroke-opacity=".4" stroke-width=".6"'))
    smx, smy = P(33.7, -10.5, 12.6)
    for k in range(3):
        out.append(f'<circle class="smoke" style="animation-delay:{k * 1.5}s" cx="{smx:.1f}" cy="{smy - 3:.1f}" r="4" fill="{THEME["smoke"]}"/>')
    roof_pt = lambda x, t: P(x, RIDGE_Y + (HY1 + .5 - RIDGE_Y) * t, RIDGE_Z - (RIDGE_Z - EAVE_Z) * t)
    front_roof = [roof_pt(HX0 - .5, 0), roof_pt(HX1 + .5, 0), roof_pt(HX1 + .5, 1), roof_pt(HX0 - .5, 1)]
    out.append(poly(front_roof, "#1a2438", edge))

    # solar panels (energy = commits), shimmering
    for r in range(2):
        for c in range(5):
            x0, t0 = HX0 + 1 + c * 2.45, .14 + r * .4
            quad = [roof_pt(x0, t0), roof_pt(x0 + 2.2, t0), roof_pt(x0 + 2.2, t0 + .34), roof_pt(x0, t0 + .34)]
            out.append(poly(quad, "#0d2c52", f'stroke="{neon_a}" stroke-opacity=".55" stroke-width=".7"'))
            out.append(poly(quad, neon_a, f'class="sweep" style="animation-delay:{1 + c * .25 + r * .1:.2f}s"'))
    if snow:
        out.append(poly([roof_pt(HX0 - .5, 0), roof_pt(HX1 + .5, 0), roof_pt(HX1 + .5, .12), roof_pt(HX0 - .5, .12)], "#f4f8ff"))
        out.append(poly([roof_pt(HX0 - .5, .92), roof_pt(HX1 + .5, .92), roof_pt(HX1 + .5, 1), roof_pt(HX0 - .5, 1)], "#f4f8ff"))

    # antenna + zigbee/thread mesh waves
    ax, ay = P(41, RIDGE_Y, RIDGE_Z)
    tx, ty = P(41, RIDGE_Y, RIDGE_Z + 3.4)
    out.append(f'<path d="M{ax:.1f} {ay:.1f}L{tx:.1f} {ty:.1f}" stroke="{neon_a}" stroke-width="1.6"/>'
               f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="2.5" fill="{neon_b}" filter="url(#glow)"/>')
    for k in range(3):
        out.append(f'<circle class="wave" style="animation-delay:{k * .85:.2f}s" cx="{tx:.1f}" cy="{ty:.1f}" r="16" fill="none" '
                   f'stroke="{neon_a}" stroke-width="1"/>')
    if "flag" in THEME["deco"]:
        fx, fy = tx + 1, ty
        out.append(f'<g class="bob"><rect x="{fx}" y="{fy}" width="6" height="11" fill="#3b82f6"/>'
                   f'<rect x="{fx + 6}" y="{fy}" width="6" height="11" fill="#f5f5f5"/><rect x="{fx + 12}" y="{fy}" width="6" height="11" fill="#ef4444"/></g>')

    # christmas garland on the eaves
    if "garland" in THEME["deco"]:
        cols = ["#ff4d6d", "#39ff88", "#ffd166", "#00e5ff"]
        dots = [roof_pt(HX0 - .5 + i * .75, 1) for i in range(21)]
        dots += [P(HX1 + .5, RIDGE_Y + (HY1 + .5 - RIDGE_Y) * t, RIDGE_Z - (RIDGE_Z - EAVE_Z) * t) for t in (i / 8 for i in range(9))]
        for i, (gx, gy) in enumerate(dots):
            out.append(f'<circle class="blink" style="animation-delay:{(i % 4) * .25:.2f}s" cx="{gx:.1f}" cy="{gy + 2:.1f}" r="1.9" '
                       f'fill="{cols[i % 4]}" filter="url(#glow)"/>')
    return "".join(out)


def mailbox(prs: int) -> str:
    """Mailbox by the front-left corner of the lot; the red flag is up when PRs were opened this year."""
    out = [box(28.1, -2.2, 0, .18, .18, 1.6, "#5c6f88"), box(27.8, -2.45, 1.6, .8, .7, .55, "#2b3a52")]
    fx, fy = P(28.6, -2.45, 2.15)
    if prs:
        out.append(f'<path d="M{fx:.1f} {fy:.1f}v-9h6v4h-6" fill="{RED}" stroke="{RED}" stroke-width="1"/>')
    out.append(text(round(fx + 9), round(fy - 3), f"{prs} PRs", "dim", 9))
    return "".join(out)


def mower() -> str:
    # small iso robot drawn around (0,0), then driven along the front edge of the garden
    ox, oy = P(0, 0)
    body = f'<g transform="translate({-ox:.1f},{-oy:.1f})">{box(-.5, -.35, 0, 1.0, .7, .35, "#39ff88")}</g>'
    x1, y1 = P(.5, 7.55)
    x2, y2 = P(52.5, 7.55)
    return (f'<g>{body}<circle class="blink" cx="0" cy="-6" r="1.5" fill="{RED}"/>'
            f'<animateMotion dur="40s" repeatCount="indefinite" path="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}L{x1:.1f} {y1:.1f}"/></g>')


# ------------------------------------------------------------------ render

def render(cfg: dict, data: dict, st: dict) -> str:
    rng = random.Random(7)
    heat = THEME["heat"]
    peak = max(st["max_day"], 1)
    days = data["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7    # GitHub weeks start on Sunday

    totals = [sum(d["count"] for d in ds) for _, ds in st["months"]]
    top = max(totals or [1]) or 1
    power = [t / top for t in totals]
    hot = max(range(len(totals)), key=totals.__getitem__) if any(totals) else -1
    live = len(totals) - 1

    body = [sky(rng)]
    if THEME["fireworks"]:
        body.append(fireworks(THEME["fireworks"]))
    if "bats" in THEME["deco"]:
        body.append(bats())
    body.append(house(power, hot, live, rng))
    body.append(mailbox(data["prs"]))
    if "flowers" in THEME["deco"]:
        body.append(flowers(rng))
    if "pumpkins" in THEME["deco"]:
        for x, y, r in [(33, -1.5, 6), (36.5, -1.4, 7.5), (39.5, -1.6, 5.5)]:
            body.append(pumpkin(*P(x, y), r))
    if "ghost" in THEME["deco"]:
        body.append(ghost(*P(25.5, -9, 5)))

    # the garden: 1 pillar per day, back to front
    cells = []
    for i, d in enumerate(days):
        pos = offset + i
        cells.append((pos // 7, pos % 7, d))
    for w, dow, d in sorted(cells, key=lambda c: (c[0] + c[1], c[0])):
        n = d["count"]
        x, y = w + .1, dow + .1
        delay = .3 + w * .035
        if n == 0:
            body.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">'
                        + poly([P(x, y), P(x + .8, y), P(x + .8, y + .8), P(x, y + .8)], heat[0]) + "</g>")
            continue
        lvl = min(4, 1 + int(3 * math.log1p(n) / math.log1p(peak)))
        dz = .35 + 2.6 * math.sqrt(n / peak)
        col = heat[lvl]
        top_face = [P(x, y, dz), P(x + .8, y, dz), P(x + .8, y + .8, dz), P(x, y + .8, dz)]
        shine = poly(top_face, "#ffffff", f'class="sweep" style="animation-delay:{3 + w * .06:.2f}s"')
        body.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">{box(x, y, 0, .8, .8, dz, col)}{shine}'
                    f'<title>{esc(d["date"])}: {n}</title></g>')

    # beacon on today
    w, dow, d = cells[-1]
    bx, by = P(w + .5, dow + .5, .35 + 2.6 * math.sqrt(d["count"] / peak) if d["count"] else 0)
    body.append(f'<path class="beam" d="M{bx:.1f} {by:.1f}V{by - 46:.1f}" stroke="{THEME["neon"][1]}" stroke-width="2" filter="url(#glow)"/>'
                f'<circle class="wave" cx="{bx:.1f}" cy="{by:.1f}" r="7" fill="none" stroke="{THEME["neon"][1]}"/>')
    body.append(text(round(bx), round(by - 52), "today", "", 9, "middle", f'style="fill:{THEME["neon"][1]}"'))
    body.append(mower())

    # front-left yard
    deco = THEME["deco"]
    if "xmas_tree" in deco:
        body.append(pine(5, 13, snowy=True, xmas=True, rng=rng) + gifts(7.5, 13.5))
    elif "pine" in deco:
        body.append(pine(5, 13, snowy=True))
    elif "dead_tree" in deco:
        body.append(dead_tree(5, 13))
    elif THEME["foliage"]:
        body.append(tree(5, 13, THEME["foliage"]))
    if "snowman" in deco:
        body.append(snowman(10, 13.5))
    if "pumpkins" in deco:
        body.append(pumpkin(*P(9.5, 13.2), 8) + pumpkin(*P(11.5, 14.4), 5.5))

    # captions
    a, b = THEME["neon"]
    body.append(text(24, 40, "SMART-HOME // ISO VIEW", "b", 15, extra=f'style="fill:{a}" filter="url(#glow)"'))
    body.append(text(24, 58, "garden: 1 pillar = 1 day · windows: 1 = 1 month", "dim", 10.5))
    body.append(text(24, 72, "jardin : 1 pilier = 1 jour · fenêtres : 1 = 1 mois", "dim", 10.5))
    body.append(text(24, 94, f"{THEME['icon']} {THEME['label']} MODE", "b", 11, extra=f'style="fill:{b}"'))
    info = [f"{data['total']} events · 365 days",
            f"best day {st['best_day']['date']} → {st['best_day']['count']}",
            f"streak {st['current_streak']}d · record {st['longest_streak']}d",
            "robot mower: on duty 🤖"]
    for i, line in enumerate(info):
        body.append(text(24, 418 + i * 16, line, "" if i == 0 else "dim", 11 if i == 0 else 10.5,
                         extra=f'style="fill:{a}"' if i == 0 else ""))
    lx, ly = 690, 494
    body.append(text(lx - 6, ly, "less", "dim", 9.5, "end"))
    for i, c in enumerate(heat):
        body.append(f'<rect x="{lx + i * 15}" y="{ly - 9}" width="11" height="11" rx="2" fill="{c}"/>')
    body.append(text(lx + 5 * 15 + 3, ly, "more", "dim", 9.5))

    css = CSS
    if THEME["particles"]:
        body.append(particles(THEME["particles"], rng))
        css += fall_css(H + 20)
    return document(H, "\n".join(body), f"Isometric smart home built from GitHub contributions ({THEME['label']})", css)
