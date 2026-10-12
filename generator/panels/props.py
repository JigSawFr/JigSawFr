"""Scenery props for the isometric house: lights, garden, garage & car, seasonal decorations, sky objects.

Every function returns an SVG fragment. `L` is the light level (1 = night, ~0.1 = broad daylight).
"""

from __future__ import annotations

import math
import random

from ..svg import GREEN, RED, THEME, esc, shade, text
from .iso import P, box, glow, line, poly, quad_y

WARM = "#ffd27a"
COLD = "#e8f2ff"


# ------------------------------------------------------------------ lights & equipment

def lamp_post(x, y, L) -> str:
    base, head = P(x, y), P(x, y, 2.5)
    out = [f'<ellipse cx="{base[0]:.1f}" cy="{base[1]:.1f}" rx="18" ry="9" fill="{WARM}" opacity="{.22 * L:.2f}"/>',
           line(base, head, "#3a4a63", 2),
           box(x - .2, y - .2, 2.45, .4, .4, .35, "#2b3a52")]
    out.append(f'<circle cx="{head[0]:.1f}" cy="{head[1] + 1:.1f}" r="2.4" fill="{WARM if L > .3 else "#6b6450"}"/>')
    if L > .3:
        out.append(glow(head[0], head[1] + 1, 22, WARM, L))
    return "".join(out)


def lantern(pt, L) -> str:
    x, y = pt
    out = f'<rect x="{x - 2:.1f}" y="{y - 3:.1f}" width="4" height="6" rx="1" fill="{WARM if L > .3 else "#6b6450"}"/>'
    return out + (glow(x, y, 14, WARM, L) if L > .3 else "")


def camera(x, y, z, flip=False) -> str:
    sx, sy = P(x, y, z)
    d = -1 if flip else 1
    return (f'<rect x="{sx - 4:.1f}" y="{sy - 2:.1f}" width="8" height="4" rx="1" fill="#d9e2ef" '
            f'transform="rotate({-28 * d} {sx:.1f} {sy:.1f})"/>'
            f'<circle class="blink" cx="{sx + 3 * d:.1f}" cy="{sy - 1:.1f}" r="1.2" fill="{RED}"/>')


def unifi_ap(x, y, z) -> str:
    sx, sy = P(x, y, z)
    return (f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="5" ry="2.6" fill="#f4f7fb"/>'
            f'<ellipse class="pulse" cx="{sx:.1f}" cy="{sy:.1f}" rx="5" ry="2.6" fill="none" stroke="#3b82f6" '
            f'stroke-width="1.4" filter="url(#glow)"/>')


def weather_station(x, y, env) -> str:
    base, top = P(x, y), P(x, y, 4.2)
    cups = "".join(f'<path d="M0 0L{9 * math.cos(math.radians(a)):.1f} {4.5 * math.sin(math.radians(a)):.1f}" '
                   f'stroke="#c9d6e5" stroke-width="1.2"/><circle cx="{9 * math.cos(math.radians(a)):.1f}" '
                   f'cy="{4.5 * math.sin(math.radians(a)):.1f}" r="1.8" fill="#c9d6e5"/>' for a in (0, 120, 240))
    speed = "1.2s" if env.get("weather") == "storm" else "3s"
    out = [line(base, top, "#5c6f88", 1.6),
           f'<g transform="translate({top[0]:.1f},{top[1]:.1f})"><g style="animation:spin {speed} linear infinite;'
           f'transform-box:fill-box;transform-origin:center">{cups}</g></g>',
           box(x - .25, y - .25, 2.4, .5, .5, .4, "#d9e2ef")]
    if env.get("temp") is not None:
        out.append(text(round(top[0] - 14), round(top[1] - 2), f"{env['temp']:.0f}°C", "", 9.5, "end",
                        f'style="fill:{THEME["neon"][0]}"'))
    return "".join(out)


# ------------------------------------------------------------------ garden

def fence(x0, x1, y0, y1) -> str:
    """Picket fence along the back (y = y0) and left (x = x0) edges of the lot."""
    col, stroke = "#2b3a52", THEME["neon"][0]
    out = []
    for z in (.35, .8):
        out.append(line(P(x0, y0, z), P(x1, y0, z), col, 1.6))
        out.append(line(P(x0, y0, z), P(x0, y1, z), col, 1.6))
    k = x0
    while k <= x1:
        out.append(line(P(k, y0, 0), P(k, y0, 1.05), col, 2))
        k += .8
    k = y0
    while k <= y1:
        out.append(line(P(x0, k, 0), P(x0, k, 1.05), col, 2))
        k += .8
    out.append(line(P(x0, y0, 1.05), P(x1, y0, 1.05), stroke, .6, 'stroke-opacity=".35"'))
    return "".join(out)


def bush(x, y, rng: random.Random, lights=False, snowy=False, r=7) -> str:
    sx, sy = P(x, y)
    g = "#1f5a36"
    out = [f'<circle cx="{sx + dx:.1f}" cy="{sy + dy:.1f}" r="{rr}" fill="{shade(g, k)}"/>'
           for dx, dy, rr, k in [(-r * .7, -r * .6, r * .8, .8), (r * .7, -r * .6, r * .8, .65), (0, -r * 1.1, r, 1)]]
    if snowy:
        out.append(f'<ellipse cx="{sx:.1f}" cy="{sy - r * 1.8:.1f}" rx="{r * .8:.1f}" ry="{r * .35:.1f}" fill="#eef4ff"/>')
    if lights:
        cols = THEME["garland"] or ["#ffd166"]
        for i in range(9):
            a = rng.uniform(0, math.tau)
            out.append(f'<circle class="blink" style="animation-delay:{i * .21:.2f}s" cx="{sx + r * math.cos(a):.1f}" '
                       f'cy="{sy - r + r * .8 * math.sin(a):.1f}" r="1.4" fill="{cols[i % len(cols)]}" filter="url(#glow)"/>')
    return "".join(out)


def stepping_stones(points) -> str:
    return "".join(f'<ellipse cx="{P(x, y)[0]:.1f}" cy="{P(x, y)[1]:.1f}" rx="5" ry="2.6" fill="#3a4658"/>' for x, y in points)


def flowers(rng: random.Random, x0, x1, y0, y1, n=30) -> str:
    cols = ["#ff8fd8", "#ffd166", "#ff4d6d", "#b28dff", "#7af6ff"]
    return "".join(f'<circle cx="{P(rng.uniform(x0, x1), rng.uniform(y0, y1))[0]:.1f}" '
                   f'cy="{P(rng.uniform(x0, x1), rng.uniform(y0, y1))[1]:.1f}" r="1.7" fill="{cols[i % 5]}"/>'
                   for i in range(n))


def leaf_pile(x, y, rng: random.Random) -> str:
    sx, sy = P(x, y)
    cols = ["#e07b39", "#c0392b", "#ffb547", "#a0522d"]
    out = [f'<ellipse cx="{sx:.1f}" cy="{sy - 3:.1f}" rx="13" ry="6" fill="#8a4a20"/>']
    for i in range(14):
        out.append(f'<ellipse cx="{sx + rng.uniform(-11, 11):.1f}" cy="{sy - 3 + rng.uniform(-5, 3):.1f}" rx="2.6" ry="1.3" '
                   f'fill="{cols[i % 4]}" transform="rotate({rng.randint(0, 180)} {sx:.1f} {sy:.1f})"/>')
    return "".join(out)


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
        # a light string spiralling down the tree
        path = " ".join(f"{sx + (4 + i * .9) * math.sin(i * .9):.1f},{sy - 58 + i * 2.6:.1f}" for i in range(20))
        out.append(f'<polyline points="{path}" fill="none" stroke="#ffd166" stroke-width=".6" opacity=".6"/>')
        for i in range(16):
            bx, by = sx + (4 + i * 1.1) * math.sin(i * 1.1), sy - 56 + i * 3.1
            out.append(f'<circle class="blink" style="animation-delay:{i * .17:.2f}s" cx="{bx:.1f}" cy="{by:.1f}" r="1.7" '
                       f'fill="{cols[i % 4]}" filter="url(#glow)"/>')
        out.append(f'<path class="beam" d="M{sx} {sy - 70}l2 5 5 0-4 3 2 5-5-3-5 3 2-5-4-3 5 0z" fill="#ffd166" filter="url(#glow)"/>')
    return "".join(out)


def snowman(x, y) -> str:
    sx, sy = P(x, y)
    return (f'<circle cx="{sx}" cy="{sy - 8}" r="9" fill="#eef4ff"/><circle cx="{sx}" cy="{sy - 22}" r="6.5" fill="#eef4ff"/>'
            f'<path d="M{sx + 2} {sy - 22}l7 1.5-7 1z" fill="#ff7b00"/><rect x="{sx - 6}" y="{sy - 34}" width="12" height="7" fill="#111"/>'
            f'<rect x="{sx - 8}" y="{sy - 28}" width="16" height="2" fill="#111"/><path d="M{sx - 6} {sy - 16}h12" stroke="#ff4d6d" stroke-width="2.5"/>'
            f'<path d="M{sx - 8} {sy - 12}l-9-6M{sx + 8} {sy - 12}l9-6" stroke="#6b4a2b" stroke-width="1.5"/>')


def gifts(x, y) -> str:
    out = box(x, y, 0, .9, .9, .8, "#ff4d6d") + box(x + 1.1, y + .2, 0, .7, .7, .6, "#ffd166") + box(x + .3, y + 1.2, 0, .8, .7, .5, "#39ff88")
    a, b = P(x + .45, y, .8), P(x + .45, y + .9, .8)
    return out + line(a, b, "#ffd166", 1.5)


def reindeer(x, y, L) -> str:
    """Wire-frame light sculpture."""
    sx, sy = P(x, y)
    d = (f"M{sx - 12} {sy}l2-12h16l2 12M{sx - 10} {sy - 12}q-2-6 4-8h14q6-2 6-8m0 0l3-6m-3 6l-6-4"
         f"m6 4q6 2 4 8M{sx + 16} {sy - 22}l4-2")
    return (f'<path class="twinkle" d="{d}" fill="none" stroke="{COLD}" stroke-width="1.6" stroke-linejoin="round" '
            f'stroke-dasharray="1 3" filter="url(#glow)" opacity="{.4 + .6 * L:.2f}"/>'
            f'<circle cx="{sx + 20}" cy="{sy - 24}" r="2" fill="#ff4d6d" filter="url(#glow)"/>')


def sleigh() -> str:
    shape = ("<path d='M0 0h18q4 0 4-5M2 0v-6h12v6' fill='none' stroke='#ffd166' stroke-width='1.4'/>"
             "<rect x='3' y='-10' width='9' height='5' fill='#ff4d6d'/>"
             + "".join(f"<path d='M{-12 - 12 * i} -3l3-4h7l2-4m-2 4l2 5m-9-1l-1 4' stroke='#c9a27a' stroke-width='1.4' fill='none'/>"
                       for i in range(2))
             + "<path d='M-4 -4H-30' stroke='#c9d6e5' stroke-width='.6'/>"
             + "<circle cx='-34' cy='-11' r='1.8' fill='#ff4d6d' filter='url(#glow)'/>")
    return (f'<g>{shape}<animateMotion dur="26s" repeatCount="indefinite" '
            f'path="M-60 16 C 220 2, 440 30, 900 22"/></g>')


def tombstone(x, y, lean=0) -> str:
    sx, sy = P(x, y)
    return (f'<g transform="rotate({lean} {sx:.1f} {sy:.1f})"><path d="M{sx - 6:.1f} {sy:.1f}v-11a6 6 0 0 1 12 0v11z" '
            f'fill="#4a4f5c" stroke="#2a2d36"/><text x="{sx:.1f}" y="{sy - 6:.1f}" font-size="4.5" text-anchor="middle" '
            f'style="fill:#1a1c22">RIP</text></g>')


def web(sx, sy) -> str:
    out = []
    for a in range(0, 91, 22):
        r = math.radians(a)
        out.append(f'<path d="M{sx:.1f} {sy:.1f}l{24 * math.cos(r):.1f} {24 * math.sin(r):.1f}" stroke="#cfd3e6" stroke-width=".5"/>')
    for k in (8, 15, 22):
        p = " ".join(f"{sx + k * math.cos(math.radians(a)):.1f},{sy + k * math.sin(math.radians(a)):.1f}" for a in range(0, 91, 22))
        out.append(f'<polyline points="{p}" fill="none" stroke="#cfd3e6" stroke-width=".5"/>')
    out.append(f'<path class="bob" d="M{sx + 14:.1f} {sy + 14:.1f}v8" stroke="#cfd3e6" stroke-width=".4"/>'
               f'<circle class="bob" cx="{sx + 14:.1f}" cy="{sy + 23:.1f}" r="2" fill="#111"/>')
    return f'<g opacity=".7">{"".join(out)}</g>'


def pumpkin(x, y, r=7.0) -> str:
    return (f'<g transform="translate({x:.1f},{y:.1f})">'
            f'<ellipse rx="{r}" ry="{r * .72:.1f}" fill="#ff7b00"/>'
            f'<ellipse rx="{r * .45:.1f}" ry="{r * .72:.1f}" fill="#e56a00"/>'
            f'<path d="M0 {-r * .7:.1f}v-3" stroke="#3c8d2f" stroke-width="2"/>'
            f'<g class="flick" fill="#ffe28a" filter="url(#glow)"><path d="M{-r * .5:.1f} -1l2 -3 2 3z"/>'
            f'<path d="M{r * .5 - 4:.1f} -1l2 -3 2 3z"/><path d="M-3 2h6l-3 2z"/></g></g>')


def dead_tree(x, y) -> str:
    sx, sy = P(x, y)
    c = THEME["neon"][1]
    return (f'<path d="M{sx} {sy}v-34m0 10l-12-12m12 4l10-14m-10 6l-4-12m-8-2l-6-4m24-2l7-3" fill="none" '
            f'stroke="#2a1838" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M{sx} {sy}v-34m0 10l-12-12m12 4l10-14m-10 6l-4-12" fill="none" stroke="{c}" stroke-width=".8" opacity=".7"/>')


def ghost(x, y) -> str:
    return (f'<g transform="translate({x:.1f},{y:.1f})"><g class="bob" opacity=".85">'
            f'<path d="M-9 8V-4a9 9 0 0 1 18 0V8l-3-3-3 3-3-3-3 3-3-3z" fill="#eef1ff" filter="url(#glow)"/>'
            f'<circle cx="-3" cy="-3" r="1.6" fill="#111"/><circle cx="3" cy="-3" r="1.6" fill="#111"/></g></g>')


def parasol(x, y) -> str:
    sx, sy = P(x, y)
    stripes = "".join(f'<path d="M{sx:.1f} {sy - 30:.1f}L{sx - 18 + i * 6:.1f} {sy - 20:.1f}L{sx - 12 + i * 6:.1f} {sy - 20:.1f}Z" '
                      f'fill="{"#ff4d6d" if i % 2 else "#f5f5f5"}"/>' for i in range(6))
    return (box(x - .5, y - .5, 0, 1, 1, .9, "#c9a27a") + line((sx, sy), (sx, sy - 30), "#c9d6e5", 1.5) + stripes)


def birdhouse(x, y) -> str:
    sx, sy = P(x, y)
    return (line((sx, sy), (sx, sy - 24), "#6b4a2b", 2) + f'<rect x="{sx - 6}" y="{sy - 34}" width="12" height="11" fill="#c9a27a"/>'
            f'<path d="M{sx - 8} {sy - 33}L{sx} {sy - 40}L{sx + 8} {sy - 33}Z" fill="#ff4d6d"/>'
            f'<circle cx="{sx}" cy="{sy - 29}" r="2" fill="#111"/>')


def string_lights(a, b, colors, L, sag=7.0, n=10) -> str:
    """A sagging string of bulbs between two screen points (guinguette / garland)."""
    (ax, ay), (bx, by) = a, b
    mx, my = (ax + bx) / 2, (ay + by) / 2 + sag * 2
    out = [f'<path d="M{ax:.1f} {ay:.1f}Q{mx:.1f} {my:.1f} {bx:.1f} {by:.1f}" fill="none" stroke="#2b3a52" stroke-width=".8"/>']
    for i in range(1, n):
        t = i / n
        x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * mx + t * t * bx
        y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * my + t * t * by
        out.append(f'<circle class="twinkle" style="animation-delay:{i * .3:.1f}s" cx="{x:.1f}" cy="{y + 2:.1f}" r="1.8" '
                   f'fill="{colors[i % len(colors)]}" opacity="{.5 + .5 * L:.2f}" filter="url(#glow)"/>')
    return "".join(out)


# ------------------------------------------------------------------ garage & car

GARAGE = (15, 21, -12, -6, 3.6)   # detached garage: x0, x1, y0, y1 (front wall), height


def garage(open_prs: int, has_car: bool, L, edge) -> str:
    x0, x1, y0, y1, h = GARAGE
    out = [box(x0, y0, 0, x1 - x0, y1 - y0, h, "#111b2b", edge),
           box(x0 - .1, y0 - .1, h, x1 - x0 + .2, y1 - y0 + .2, .25, "#1a2438", edge)]
    dx0, dx1, dz = x0 + 1, x1 - .7, 2.8
    if open_prs:
        out.append(quad_y(dx0, dx1, y1, 0, dz, "#05080e"))
        # warm interior light, shelves and a workbench silhouette
        out.append(quad_y(dx0, dx1, y1, 0, dz, WARM, f'opacity="{.18 + .25 * L:.2f}"'))
        out.append(quad_y(dx0 + .3, dx1 - .3, y1, 1.6, 1.7, "#3a4a63"))
        out.append(quad_y(dx1 - 1.4, dx1 - .3, y1, .0, .9, "#2b3a52"))
        out.append(quad_y(dx0, dx1, y1, dz - .35, dz, "#2b3a52", edge))   # rolled-up door
    else:
        out.append(quad_y(dx0, dx1, y1, 0, dz, "#1a2740", edge))
        for k in range(1, 5):
            out.append(line(P(dx0, y1, k * dz / 5), P(dx1, y1, k * dz / 5), "#0b1320", 1))
    # EV charger left of the door, lantern on the right
    out.append(box(x0 + .25, y1, 1.1, .4, .14, .75, "#d9e2ef"))
    cx, cy = P(x0 + .45, y1 + .14, 1.65)
    out.append(f'<circle class="pulse" cx="{cx:.1f}" cy="{cy:.1f}" r="1.3" fill="{GREEN if has_car else "#3b82f6"}"/>')
    out.append(lantern(P(x1 - .35, y1, 2.4), L))
    out.append(poly([P(x0 + .3, y0 + .3, h + .26), P(x1 - .3, y0 + .3, h + .26), P(x1 - .3, y0 + 2.3, h + .26),
                     P(x0 + .3, y0 + 2.3, h + .26)], "#0d2c52", f'stroke="{THEME["neon"][0]}" stroke-opacity=".5" stroke-width=".6"'))
    return "".join(out)


def car(release: dict, L) -> str:
    x0, _, _, y1, _ = GARAGE
    cx0, cy0 = x0 + 1.6, y1 + .4            # parked on the driveway, nose towards the garden
    col = THEME["neon"][1]
    out = [box(cx0, cy0, .3, 2.0, 2.9, .7, shade(col, .75)),
           box(cx0 + .25, cy0 + .6, 1.0, 1.5, 1.6, .55, "#1a2438", f'stroke="{col}" stroke-width=".6"')]
    for wy in (cy0 + .5, cy0 + 2.4):
        wx, wyy = P(cx0 + 2.0, wy, .3)
        out.append(f'<ellipse cx="{wx:.1f}" cy="{wyy:.1f}" rx="2.6" ry="3.6" fill="#0a0d12" stroke="#5c6f88" stroke-width=".8"/>')
    for hx in (cx0 + .3, cx0 + 1.7):
        sx, sy = P(hx, cy0 + 2.9, .75)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.5" fill="{COLD}"/>' + glow(sx, sy, 12, COLD, .4 + .6 * L))
    a, b = P(x0 + .45, y1 + .14, 1.3), P(cx0, cy0 + 1.2, .8)
    out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}Q{a[0] - 4:.1f} {b[1] + 8:.1f} {b[0]:.1f} {b[1]:.1f}" fill="none" stroke="#111" stroke-width="1.4"/>')
    tx, ty = P(cx0 + 1, cy0 + 1.5, 2.4)
    out.append(text(round(tx), round(ty - 4), release["tag"], "b", 9, "middle", f'style="fill:{col}" filter="url(#glow)"'))
    return "".join(out)


def mailbox(x, y, has_mail: bool) -> str:
    out = [box(x, y, 0, .18, .18, 1.6, "#5c6f88"), box(x - .3, y - .25, 1.6, .8, .7, .55, "#2b3a52")]
    fx, fy = P(x + .5, y - .25, 2.15)
    if has_mail:
        out.append(f'<path d="M{fx:.1f} {fy:.1f}v-9h6v4h-6" fill="{RED}" stroke="{RED}" stroke-width="1"/>')
    return "".join(out)


# ------------------------------------------------------------------ sky objects

def bats() -> str:
    shape = "M0 0C-3-5-9-5-12-2C-9-2-8 0-8 2C-6 0-3 1 0 3C3 1 6 0 8 2C8 0 9-2 12-2C9-5 3-5 0 0Z"
    paths = ["M-30 90 C 150 40, 300 140, 520 70 S 760 40, 880 110",
             "M880 60 C 700 120, 560 20, 380 90 S 120 60, -30 120",
             "M-30 170 C 200 120, 380 200, 560 140 S 800 100, 880 160"]
    return "".join(
        f'<g><g class="fly" style="animation-delay:{i * .2}s"><path d="{shape}" fill="#07040c" '
        f'stroke="{THEME["neon"][1]}" stroke-width=".8"/></g>'
        f'<animateMotion dur="{14 + i * 4}s" repeatCount="indefinite" begin="{-i * 3}s" path="{p}"/></g>'
        for i, p in enumerate(paths))


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


def beacon(sx, sy) -> str:
    """Rotating red alarm light (intrusion mode)."""
    beams = (f'<path d="M0 0L90 -10L90 10Z" fill="{RED}" opacity=".35"/>'
             f'<path d="M0 0L-90 -10L-90 10Z" fill="{RED}" opacity=".35"/>')
    return (f'<g transform="translate({sx:.1f},{sy:.1f})"><g>{beams}<animateTransform attributeName="transform" '
            f'type="rotate" from="0" to="360" dur="1.2s" repeatCount="indefinite"/></g></g>'
            f'<path d="M{sx - 5:.1f} {sy + 2:.1f}a5 5 0 0 1 10 0z" fill="{RED}" filter="url(#glow)"/>'
            + glow(sx, sy, 26, RED, 1, "pulse"))




# ------------------------------------------------------------------ more seasonal props

def drone() -> str:
    """Security drone patrolling around the house (all seasons)."""
    body = ('<rect x="-5" y="-2" width="10" height="4" rx="1.5" fill="#d9e2ef"/>'
            '<path d="M-5 0h-5M5 0h5" stroke="#5c6f88" stroke-width="1"/>'
            '<ellipse class="blink" cx="-10" cy="-1.5" rx="4" ry="1" fill="#c9d6e5" opacity=".6"/>'
            '<ellipse class="blink" cx="10" cy="-1.5" rx="4" ry="1" fill="#c9d6e5" opacity=".6" style="animation-delay:.5s"/>'
            f'<circle class="blink" cx="-3" cy="2.5" r="1" fill="{RED}"/><circle class="blink" cx="3" cy="2.5" r="1" fill="{GREEN}" '
            'style="animation-delay:.5s"/>')
    return (f'<g><g class="bob">{body}</g><animateMotion dur="22s" repeatCount="indefinite" '
            f'path="M470 150 C 520 70, 760 70, 815 160 S 640 260, 470 150"/></g>')


def hologram(x, y, z) -> str:
    sx, sy = P(x, y, z)
    c = THEME["neon"][0]
    house = f"M-14 8V-4L0-15L14-4V8ZM-5 8V0h10v8"
    return (f'<ellipse cx="{sx:.1f}" cy="{P(x, y)[1]:.1f}" rx="14" ry="6" fill="{c}" opacity=".25" filter="url(#glow)"/>'
            f'<path d="M{sx - 12:.1f} {P(x, y)[1]:.1f}L{sx - 14:.1f} {sy + 8:.1f}M{sx + 12:.1f} {P(x, y)[1]:.1f}L{sx + 14:.1f} {sy + 8:.1f}" '
            f'stroke="{c}" stroke-opacity=".25"/>'
            f'<g transform="translate({sx:.1f},{sy:.1f})"><g class="holo"><path d="{house}" fill="{c}" fill-opacity=".12" '
            f'stroke="{c}" stroke-width="1.4" filter="url(#glow)"/></g></g>')


def neon_sign(label: str, color: str) -> str:
    """Neon letters standing on the garage roof, drawn in the y = -7.5 plane."""
    x0, x1, y0, y1, h = GARAGE
    sx, sy = P(x0 + .3, (y0 + y1) / 2 + 1.2, h + .6)
    return (f'<g transform="matrix(.866 .5 0 1 {sx:.1f} {sy:.1f})"><text class="flick" x="0" y="0" font-size="8.5" '
            f'font-weight="700" style="fill:{color}" filter="url(#glow)" textLength="{min(len(label) * 5.6, 52):.0f}" '
            f'lengthAdjust="spacingAndGlyphs">{label}</text></g>')


def butterflies() -> str:
    cols = ["#ff8fd8", "#ffd166", "#7af6ff"]
    paths = ["M60 260 C 120 200, 200 300, 260 230 S 360 260, 300 300 S 120 320, 60 260",
             "M140 300 C 220 240, 300 300, 230 330 S 100 330, 140 300",
             "M520 330 C 600 300, 640 380, 560 390 S 480 360, 520 330"]
    return "".join(
        f'<g><g class="fly" style="animation-duration:.35s"><path d="M0 0c-4-6-9-4-7 0c-2 4 3 6 7 0c4-6 9-4 7 0c2 4-3 6-7 0" '
        f'fill="{cols[i]}"/></g><animateMotion dur="{11 + i * 3}s" repeatCount="indefinite" path="{p}"/></g>'
        for i, p in enumerate(paths))


def pool(x0, x1, y0, y1) -> str:
    rim = box(x0 - .3, y0 - .3, 0, x1 - x0 + .6, y1 - y0 + .6, .25, "#d9e2ef")
    water = poly([P(x0, y0, .26), P(x1, y0, .26), P(x1, y1, .26), P(x0, y1, .26)], "#1fb6ff", 'opacity=".85"')
    waves = "".join(line(P(x0 + .5, y0 + k, .27), P(x1 - .5, y0 + k, .27), "#bff0ff", .8,
                         f'class="twinkle" style="animation-delay:{k * .4:.1f}s"') for k in (.6, 1.3, 2.0))
    rx, ry = P((x0 + x1) / 2, (y0 + y1) / 2, .3)
    ring = (f'<g class="bob"><ellipse cx="{rx:.1f}" cy="{ry:.1f}" rx="6" ry="3.2" fill="none" stroke="#ff8fd8" stroke-width="2.6"/>'
            f'</g>')
    return rim + water + waves + ring


def deckchair(x, y) -> str:
    return box(x, y, .2, .8, 1.8, .15, "#ffb547") + box(x, y, .35, .8, .4, .9, "#ff4d6d")


def sled(x, y) -> str:
    sx, sy = P(x, y)
    prints = "".join(f'<ellipse cx="{sx + 12 + i * 7:.1f}" cy="{sy - 2 + i * 4:.1f}" rx="2" ry="1" fill="#c9d6e5" opacity=".6"/>'
                     for i in range(5))
    return (box(x, y, .15, 1.0, 2.0, .2, "#c0392b") + line(P(x, y + 2.3, 0), P(x, y - .1, 0), "#d9e2ef", 1.4)
            + line(P(x + 1, y + 2.3, 0), P(x + 1, y - .1, 0), "#d9e2ef", 1.4) + prints)


def scarecrow(x, y) -> str:
    sx, sy = P(x, y)
    return (f'<path d="M{sx} {sy}v-36M{sx - 13} {sy - 26}h26" stroke="#8a5a2b" stroke-width="2.4"/>'
            f'<path d="M{sx - 8} {sy - 27}h16l-3 14h-10z" fill="#3b6ea5"/>'
            f'<circle cx="{sx}" cy="{sy - 33}" r="5" fill="#e9c46a"/>'
            f'<path d="M{sx - 9} {sy - 36}h18M{sx - 5} {sy - 36}l2-6h6l2 6" fill="#6b4a2b" stroke="#6b4a2b" stroke-width="1.6"/>'
            f'<path class="bob" d="M{sx + 14} {sy - 30}l4-2 4 2" fill="none" stroke="#111" stroke-width="1.2"/>')


def mushrooms(x, y) -> str:
    sx, sy = P(x, y)
    return "".join(f'<path d="M{sx + dx - 1} {sy + dy}v-4h2v4z" fill="#f5f0e6"/>'
                   f'<path d="M{sx + dx - 4} {sy + dy - 4}a4 3 0 0 1 8 0z" fill="#ff4d6d"/>'
                   for dx, dy in [(0, 0), (8, 3), (-7, 4)])


def bunting(a, b, colors, sag=6.0, n=12) -> str:
    (ax, ay), (bx, by) = a, b
    mx, my = (ax + bx) / 2, (ay + by) / 2 + sag * 2
    out = [f'<path d="M{ax:.1f} {ay:.1f}Q{mx:.1f} {my:.1f} {bx:.1f} {by:.1f}" fill="none" stroke="#c9d6e5" stroke-width=".6"/>']
    for i in range(1, n):
        t = i / n
        x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * mx + t * t * bx
        y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * my + t * t * by
        out.append(f'<path class="bob" style="animation-duration:{2 + i % 3}s" d="M{x - 3:.1f} {y:.1f}h6l-3 6z" fill="{colors[i % len(colors)]}"/>')
    return "".join(out)


# ------------------------------------------------------------------ live-data props

def ticker(x0, x1, y, z_top, height, message: str, color: str) -> str:
    """Scrolling LED band mounted on a y = const wall (last commit message)."""
    sx, sy = P(x0, y, z_top)
    w, h = (x1 - x0) * 12, height * 12
    tw = len(message) * 5.7
    dur = (w + tw) / 28
    return (f'<g transform="matrix(.866 .5 0 1 {sx:.1f} {sy:.1f})">'
            f'<defs><clipPath id="tick"><rect width="{w:.0f}" height="{h:.0f}"/></clipPath></defs>'
            f'<rect width="{w:.0f}" height="{h:.0f}" rx="2" fill="#03060b" stroke="{THEME["neon"][0]}" stroke-opacity=".6"/>'
            f'<g clip-path="url(#tick)"><text x="0" y="{h * .72:.1f}" font-size="9.5" style="fill:{color};'
            f'animation:ticker {dur:.1f}s linear infinite" filter="url(#glow)">{esc(message)}</text></g>'
            f'<style>@keyframes ticker {{ from {{ transform: translateX({w:.0f}px); }} to {{ transform: translateX(-{tw:.0f}px); }} }}</style>'
            f"</g>")


def inverter(x, y_left, y_right, z_top, height, line1: str, line2: str, color: str) -> str:
    """Small screen on an x = const wall (solar inverter / UPS)."""
    sx, sy = P(x, y_left, z_top)
    w, h = (y_left - y_right) * 12, height * 12
    return (f'<g transform="matrix(.866 -.5 0 1 {sx:.1f} {sy:.1f})">'
            f'<rect width="{w:.0f}" height="{h:.0f}" rx="2" fill="#03060b" stroke="{color}" stroke-opacity=".7"/>'
            f'<text x="{w / 2:.0f}" y="{h * .5:.1f}" font-size="7.5" font-weight="700" text-anchor="middle" '
            f'style="fill:{color}" filter="url(#glow)">{esc(line1)}</text>'
            f'<text x="{w / 2:.0f}" y="{h * .86:.1f}" font-size="5" text-anchor="middle" style="fill:#8aa0b8">{esc(line2)}</text></g>')


def bird(sx, sy, color, delay) -> str:
    return (f'<g transform="translate({sx:.1f},{sy:.1f})"><g class="peck" style="animation-delay:{delay:.1f}s">'
            f'<path d="M-1 0v3M1 0v3" stroke="#ffb547" stroke-width=".7"/>'
            f'<ellipse cx="0" cy="-2.5" rx="4" ry="2.8" fill="{color}"/>'
            f'<circle cx="3.2" cy="-5" r="2" fill="{color}"/><path d="M5 -5.2l2.4 .6-2.4 .6z" fill="#ffb547"/>'
            f'<circle cx="3.6" cy="-5.4" r=".5" fill="#111"/><path d="M-4 -3l-3 -1.5" stroke="{color}" stroke-width="1.6"/></g></g>')


def balloons(x, y, z) -> str:
    sx, sy = P(x, y, z)
    cols = ["#ff4d6d", "#ffd166", "#00e5ff", "#ff2fd0", "#39ff88"]
    out = []
    for i, (dx, dy) in enumerate([(-12, -34), (-4, -42), (6, -38), (14, -30), (0, -28)]):
        out.append(f'<g class="bob" style="animation-delay:{i * .4:.1f}s">'
                   f'<path d="M{sx:.1f} {sy:.1f}Q{sx + dx / 2:.1f} {sy + dy / 2 + 6:.1f} {sx + dx:.1f} {sy + dy + 6:.1f}" '
                   f'fill="none" stroke="#c9d6e5" stroke-width=".5"/>'
                   f'<ellipse cx="{sx + dx:.1f}" cy="{sy + dy:.1f}" rx="5" ry="6.2" fill="{cols[i]}"/>'
                   f'<ellipse cx="{sx + dx - 1.6:.1f}" cy="{sy + dy - 2:.1f}" rx="1.2" ry="1.8" fill="#fff" opacity=".5"/></g>')
    return "".join(out)


def cake(x, y) -> str:
    sx, sy = P(x, y, .9)
    out = [box(x - .6, y - .6, 0, 1.2, 1.2, .9, "#c9a27a"),
           f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="9" ry="4.5" fill="#ff8fd8"/>',
           f'<rect x="{sx - 9:.1f}" y="{sy - 8:.1f}" width="18" height="8" fill="#ff8fd8"/>',
           f'<ellipse cx="{sx:.1f}" cy="{sy - 8:.1f}" rx="9" ry="4.5" fill="#ffd1ec"/>']
    for k in range(4):
        cx = sx - 5 + k * 3.4
        out.append(f'<rect x="{cx - .6:.1f}" y="{sy - 14:.1f}" width="1.2" height="5" fill="#7af6ff"/>'
                   f'<ellipse class="flick" style="animation-delay:{k * .3:.1f}s" cx="{cx:.1f}" cy="{sy - 15.5:.1f}" '
                   f'rx="1" ry="1.8" fill="#ffd166" filter="url(#glow)"/>')
    return "".join(out)


def road(x0, x1, y0, y1) -> str:
    out = [poly([P(x0, y0, .01), P(x1, y0, .01), P(x1, y1, .01), P(x0, y1, .01)], "#141a24"),
           line(P(x0, y0, .02), P(x1, y0, .02), "#2b3a52", 1), line(P(x0, y1, .02), P(x1, y1, .02), "#2b3a52", 1)]
    k, ym = x0 + .5, (y0 + y1) / 2
    while k < x1 - 1:
        out.append(line(P(k, ym, .02), P(k + 1, ym, .02), "#ffd166", 1, 'stroke-opacity=".5"'))
        k += 2
    return "".join(out)


NEIGHBOUR_W, NEIGHBOUR_D = 2.6, 1.8


def neighbour(x, y, total: int, login: str, L, rng: random.Random) -> str:
    """A small follower house: its windows glow with that person's yearly activity."""
    w, d, h = NEIGHBOUR_W, NEIGHBOUR_D, 1.5
    wall = rng.choice(["#18233a", "#1d2a2a", "#2a1f33", "#2b2620"])
    roof = rng.choice(["#3a7bd5", "#ff4d6d", "#39b54a", "#a64dff", "#e07b39"])
    power = min(1.0, total / 1500)
    out = [box(x, y, 0, w, d, h, wall, f'stroke="{shade(roof, .8)}" stroke-opacity=".5" stroke-width=".5"')]
    ry, rz = y + d / 2, h + 1.0
    out.append(poly([P(x - .1, y - .1, h), P(x + w + .1, y - .1, h), P(x + w + .1, ry, rz), P(x - .1, ry, rz)], shade(roof, .55)))
    out.append(poly([P(x + w, y, h), P(x + w, y + d, h), P(x + w, ry, rz - .05)], shade(wall, .6)))
    out.append(poly([P(x - .1, ry, rz), P(x + w + .1, ry, rz), P(x + w + .1, y + d + .1, h), P(x - .1, y + d + .1, h)], roof))
    win = THEME["window"]
    for k in range(2):
        wx = x + .35 + k * 1.5
        op = (.15 + .85 * power) * (.35 + .65 * L) if total else .05
        out.append(quad_y(wx, wx + .7, y + d, .7, 1.3, win if total else "#0a111c",
                          f'fill-opacity="{op:.2f}"' + (' filter="url(#glow)"' if total and L > .3 else "")))
    out.append(quad_y(x + 1.15, x + 1.6, y + d, 0, .9, "#0b1320"))
    lx, ly = P(x + w / 2, y + d, 0)
    label = "@" + login[:14]
    out.append(f'<rect x="{lx - len(label) * 2.3 - 3:.1f}" y="{ly + 5:.1f}" width="{len(label) * 4.6 + 6:.1f}" height="10" '
               f'rx="3" fill="#070b12" opacity=".8"/>')
    out.append(text(round(lx), round(ly + 12.5), label, "", 7.5, "middle", 'style="fill:#c9d6e5"'))
    return "".join(out)


# ------------------------------------------------------------------ street life

SKIN = ["#f1c27d", "#e0ac69", "#c68642", "#8d5524", "#ffdbac"]
LANE_FWD, LANE_BACK = 8.75, 9.5          # road lanes (+x / -x)
WALK_FWD, WALK_BACK = 7.9, 8.12          # sidewalk lines


def _at_origin(fragment_world: str) -> str:
    """Re-anchor a fragment drawn in world coords around (0,0) so animateMotion can drive it."""
    ox, oy = P(0, 0)
    return f'<g transform="translate({-ox:.1f},{-oy:.1f})">{fragment_world}</g>'


def _lightbar(x, z, colors, L) -> str:
    sx, sy = P(x, 0, z)
    ox, oy = P(0, 0)
    sx, sy = sx - ox, sy - oy
    out = []
    for i, c in enumerate(colors):
        dx = (i - (len(colors) - 1) / 2) * 3.4
        out.append(f'<rect class="blink" style="animation-delay:{i * .5:.1f}s;animation-duration:.6s" x="{sx + dx - 1.6:.1f}" '
                   f'y="{sy - 1.6:.1f}" width="3.2" height="2.2" rx=".6" fill="{c}" filter="url(#glow)"/>')
        if L > .3:
            out.append(glow(sx + dx, sy, 14, c if c in (RED, COLD) else RED, .7, "blink"))
    return "".join(out)


def _headlights(front_x, z, L) -> str:
    ox, oy = P(0, 0)
    out = []
    for y in (-.25, .25):
        sx, sy = P(front_x, y, z)
        sx, sy = sx - ox, sy - oy
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.1" fill="{COLD}"/>')
        if L > .3:
            out.append(glow(sx, sy, 9, COLD, .6 * L))
    return "".join(out)


def _side_text(x, z, label, color) -> str:
    """Text painted on the +y flank of a vehicle (local coords)."""
    ox, oy = P(0, 0)
    sx, sy = P(x, .45, z)
    return (f'<g transform="matrix(.866 .5 0 1 {sx - ox:.1f} {sy - oy:.1f})"><text font-size="5" font-weight="700" '
            f'style="fill:{color}">{label}</text></g>')


def vehicle(kind: str, forward: bool, L: float) -> str:
    """Iso vehicle centred on the origin, length along x."""
    out = []
    if kind in ("bus", "school"):
        col = "#2f6db5" if kind == "bus" else "#ffc21a"
        out.append(_at_origin(box(-2.2, -.45, .15, 4.4, .9, 1.15, col)))
        out.append(_at_origin(quad_y(-1.9, 1.9, .45, .75, 1.1, "#bfe3ff", 'opacity=".85"')))
        if kind == "school":
            out.append(_at_origin(quad_y(-2.2, 2.2, .45, .5, .6, "#111")))
            out.append(_side_text(-1.2, .25, "ÉCOLE", "#111"))
        else:
            out.append(_side_text(-1.4, .3, "LIGNE 42", "#ffffff"))
        front = 2.2
    elif kind == "fire":
        out.append(_at_origin(box(-1.9, -.45, .15, 3.8, .9, 1.0, "#d62828")))
        out.append(_at_origin(box(.9, -.42, 1.15, 1.0, .84, .35, "#1a2438")))
        out.append(_at_origin(line(P(-1.7, 0, 1.35), P(.6, 0, 1.35), "#d9e2ef", 1.6)))
        out.append(_at_origin(quad_y(-1.6, .6, .45, .45, .75, "#ffd166")))
        out.append(_lightbar(1.4, 1.55, [RED, "#ffd166"], L))
        front = 1.9
    elif kind == "ambulance":
        out.append(_at_origin(box(-1.3, -.43, .15, 2.6, .86, 1.05, "#f4f7fb")))
        out.append(_at_origin(quad_y(-1.2, 1.2, .43, .5, .62, "#ff4d6d")))
        out.append(_side_text(-.4, .95, "✚", RED))
        out.append(_lightbar(.6, 1.25, ["#3b82f6", RED], L))
        front = 1.3
    elif kind == "police":
        out.append(_at_origin(box(-.95, -.4, .15, 1.9, .8, .45, "#f4f7fb")))
        out.append(_at_origin(quad_y(-.95, .95, .4, .3, .42, "#1d4ed8")))
        out.append(_at_origin(box(-.5, -.35, .6, 1.0, .7, .33, "#1a2438")))
        out.append(_lightbar(0, 1.0, ["#3b82f6", RED], L))
        front = .95
    elif kind in ("van", "grid"):
        col = "#8a5a2b" if kind == "van" else "#ff9f1c"
        out.append(_at_origin(box(-1.1, -.42, .15, 2.2, .84, .95, col)))
        out.append(_side_text(-.8, .55, "COLIS" if kind == "van" else "⚡ RÉSEAU", "#ffffff"))
        if kind == "grid":
            out.append(_lightbar(0, 1.15, ["#ffb547"], L))
        front = 1.1
    elif kind == "garbage":
        out.append(_at_origin(box(-1.6, -.45, .15, 3.2, .9, 1.05, "#2e8b57")))
        out.append(_at_origin(box(.8, -.42, 1.2, .8, .84, .1, "#1a2438")))
        front = 1.6
    else:   # car, colour in the kind name: car:#hex
        col = kind.split(":", 1)[1] if ":" in kind else "#5c6f88"
        out.append(_at_origin(box(-.9, -.4, .15, 1.8, .8, .45, col)))
        out.append(_at_origin(box(-.5, -.35, .6, 1.0, .7, .33, "#1a2438")))
        front = .9
    out.append(_headlights(front if forward else -front, .4, L))
    return "".join(out)


def drive(fragment: str, x0: float, x1: float, lane: float, dur: float, begin: float) -> str:
    a, b = P(x0, lane), P(x1, lane)
    return (f'<g>{fragment}<animateMotion dur="{dur}s" begin="{-begin:.1f}s" repeatCount="indefinite" '
            f'path="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}"/></g>')


def parked(fragment: str, x: float, lane: float) -> str:
    sx, sy = P(x, lane)
    return f'<g transform="translate({sx:.1f},{sy:.1f})">{fragment}</g>'


def person(kind: str, rng: random.Random, umbrella=False) -> str:
    """A walking figure (screen coords around its feet)."""
    k = .72 if kind in ("kid", "ghost_kid", "witch_kid") else 1.0
    skin = rng.choice(SKIN)
    shirt = rng.choice(["#3b82f6", "#ff4d6d", "#39ff88", "#ffd166", "#a64dff", "#ff9f1c", "#e5e7eb"])
    legs = f'<path class="legA" d="M-1 {-6 * k:.1f}v{6 * k:.1f}" stroke="#2b3a52" stroke-width="1.6"/>' \
           f'<path class="legB" d="M1 {-6 * k:.1f}v{6 * k:.1f}" stroke="#2b3a52" stroke-width="1.6"/>'
    if kind == "ghost_kid":
        body = (f'<path d="M-3.5 0V-8a3.5 3.5 0 0 1 7 0V0l-1.2-1.2-1.2 1.2-1.1-1.2-1.1 1.2-1.2-1.2z" fill="#f4f6ff"/>'
                f'<circle cx="-1.2" cy="-8.4" r=".7" fill="#111"/><circle cx="1.2" cy="-8.4" r=".7" fill="#111"/>')
        return f'<g class="walk">{body}</g>'
    if kind == "witch_kid":
        body = (legs + f'<path d="M-2.6 -5L0 -10L2.6 -5z" fill="#4b1d6b"/><circle cy="-11.2" r="1.8" fill="{skin}"/>'
                f'<path d="M-3.2 -12.4h6.4M-1.6 -12.4L0 -17L1.6 -12.4z" stroke="#111" stroke-width=".8" fill="#111"/>'
                f'<circle cx="2.5" cy="-6" r="1.4" fill="#ff7b00"/>')
        return f'<g class="walk">{body}</g>'
    if kind == "santa":
        shirt, extra = "#d62828", ('<path d="M-1.6 -11.2q1.6 3 3.2 0" fill="#fff"/><path d="M-2 -14.6h4l-2-3z" fill="#d62828"/>'
                                   '<circle cx="0" cy="-17.6" r=".7" fill="#fff"/><circle cx="-4" cy="-8" r="2.8" fill="#8a5a2b"/>')
    else:
        extra = ""
    body = (legs + f'<rect x="{-2.2 * k:.1f}" y="{-11.5 * k:.1f}" width="{4.4 * k:.1f}" height="{6 * k:.1f}" rx="1.4" fill="{shirt}"/>'
            f'<circle cy="{-13.3 * k:.1f}" r="{2 * k:.1f}" fill="{skin}"/>' + extra)
    if kind == "kid":
        body += f'<rect x="-3.6" y="-8.2" width="2" height="3.4" rx=".6" fill="{rng.choice(["#ff4d6d", "#00e5ff", "#ffd166"])}"/>'
    if kind == "elder":
        body += '<path d="M3 -7l1.4 7" stroke="#8a5a2b" stroke-width="1"/>'
    if kind == "walker":
        body += ('<path d="M2 -7Q6 -4 9 -2.5" fill="none" stroke="#c9d6e5" stroke-width=".5"/>'
                 '<g class="walk" style="animation-duration:.3s"><ellipse cx="11" cy="-2.5" rx="3" ry="1.6" fill="#c68642"/>'
                 '<circle cx="13.6" cy="-3.6" r="1.3" fill="#c68642"/><path d="M9 -1.2v1.2M12.6 -1.2v1.2" stroke="#8d5524" stroke-width=".8"/></g>')
    if umbrella and kind in ("adult", "walker", "elder"):
        body += (f'<path d="M0 {-13.3 * k:.1f}V-22" stroke="#111" stroke-width=".6"/>'
                 f'<path d="M-6 -21a6 4 0 0 1 12 0z" fill="{rng.choice(["#ff4d6d", "#3b82f6", "#111", "#ffd166"])}"/>')
    return f'<g class="walk" style="animation-duration:{.3 if kind == "jogger" else .45}s">{body}</g>'


def stroll(fragment: str, forward: bool, lane: float, dur: float, begin: float) -> str:
    x0, x1 = (-1, 54) if forward else (54, -1)
    flip = "" if forward else ' transform="scale(-1,1)"'
    a, b = P(x0, lane), P(x1, lane)
    return (f'<g><g{flip}>{fragment}</g><animateMotion dur="{dur}s" begin="{-begin:.1f}s" repeatCount="indefinite" '
            f'path="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}"/></g>')


def sidewalk(x0, x1, y0, y1) -> str:
    out = [poly([P(x0, y0, .02), P(x1, y0, .02), P(x1, y1, .02), P(x0, y1, .02)], "#273242"),
           line(P(x0, y1, .03), P(x1, y1, .03), "#3a4a63", 1.2)]
    k = x0 + 1
    while k < x1:
        out.append(line(P(k, y0, .03), P(k, y1, .03), "#1e2836", .6))
        k += 1.5
    return "".join(out)


# ------------------------------------------------------------------ street furniture & neighbour gardens

WALK_FAR = (10.15, 10.38)                # far sidewalk lines


def zebra(x, y0, y1, w=1.4) -> str:
    out, y = [], y0 + .1
    while y < y1 - .1:
        out.append(poly([P(x, y, .02), P(x + w, y, .02), P(x + w, y + .2, .02), P(x, y + .2, .02)], "#e8edf5", 'opacity=".75"'))
        y += .4
    return "".join(out)


def bench(x, y) -> str:
    return (box(x, y, .35, 1.4, .35, .08, "#8a5a2b") + box(x, y, .43, 1.4, .08, .35, "#8a5a2b")
            + line(P(x + .1, y + .3, 0), P(x + .1, y + .3, .35), "#3a4a63", 1.2)
            + line(P(x + 1.3, y + .3, 0), P(x + 1.3, y + .3, .35), "#3a4a63", 1.2))


def bin_(x, y) -> str:
    return box(x, y, 0, .35, .35, .55, "#2e8b57") + box(x - .03, y - .03, .55, .41, .41, .06, "#1f5a36")


def hydrant(x, y) -> str:
    sx, sy = P(x, y)
    return (f'<rect x="{sx - 2:.1f}" y="{sy - 7:.1f}" width="4" height="7" rx="1" fill="#d62828"/>'
            f'<circle cx="{sx:.1f}" cy="{sy - 7:.1f}" r="2.2" fill="#d62828"/><rect x="{sx - 3.2:.1f}" y="{sy - 5:.1f}" '
            f'width="6.4" height="1.6" fill="#a61e1e"/>')


def sign(x, y, kind: str) -> str:
    base, top = P(x, y), P(x, y, 2.1)
    out = [line(base, top, "#8aa0b8", 1.1)]
    tx, ty = top
    if kind == "30":
        out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="5" fill="#fff" stroke="#d62828" stroke-width="1.6"/>'
                   f'<text x="{tx:.1f}" y="{ty + 2:.1f}" font-size="5" font-weight="700" text-anchor="middle" style="fill:#111">30</text>')
    elif kind == "school":
        out.append(f'<path d="M{tx:.1f} {ty - 6:.1f}l6 10h-12z" fill="#fff" stroke="#d62828" stroke-width="1.4"/>'
                   f'<path d="M{tx - 2:.1f} {ty + 2:.1f}l1-4 1 4M{tx + .5:.1f} {ty + 2:.1f}l1-3 1 3" stroke="#111" stroke-width=".7" fill="none"/>')
    elif kind == "bus":
        out.append(f'<rect x="{tx - 4:.1f}" y="{ty - 5:.1f}" width="8" height="7" rx="1" fill="#2f6db5"/>'
                   f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="4.5" font-weight="700" text-anchor="middle" style="fill:#fff">BUS</text>')
    elif kind == "stop":
        pts_ = " ".join(f"{tx + 5 * math.cos(math.radians(22.5 + 45 * k)):.1f},{ty + 5 * math.sin(math.radians(22.5 + 45 * k)):.1f}"
                        for k in range(8))
        out.append(f'<polygon points="{pts_}" fill="#d62828"/><text x="{tx:.1f}" y="{ty + 1.6:.1f}" font-size="3.4" '
                   f'font-weight="700" text-anchor="middle" style="fill:#fff">STOP</text>')
    return "".join(out)


def bus_stop(x, y, L) -> str:
    """Glass shelter with a bench and a lit timetable."""
    out = [box(x, y, 0, 2.2, .7, .05, "#3a4658"),
           quad_y(x, x + 2.2, y + .05, .1, 1.9, "#bfe3ff", 'opacity=".25"'),
           box(x - .05, y - .05, 1.9, 2.3, .8, .1, "#2b3a52"),
           box(x + .3, y + .1, .35, 1.4, .3, .08, "#8a5a2b"),
           quad_y(x + 1.8, x + 2.15, y + .7, .4, 1.4, WARM, f'opacity="{.35 + .6 * L:.2f}"')]
    return "".join(out) + sign(x + 2.5, y + .4, "bus")


def street_tree(x, y, L, rng: random.Random) -> str:
    sx, sy = P(x, y)
    key, deco = THEME["key"], THEME["deco"]
    out = [f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="7" ry="3.5" fill="#3a2a1a"/>',
           f'<path d="M{sx:.1f} {sy:.1f}v-18" stroke="#6b4a2b" stroke-width="2.4"/>']
    bare = key in ("hiver", "nouvel_an") or (key == "noel")
    if bare:
        out.append(f'<path d="M{sx:.1f} {sy - 12:.1f}l-8-9m8 4l7-10m-7 4l-2-9m-6 2l-4-3m17-2l5-3" fill="none" '
                   f'stroke="#6b4a2b" stroke-width="1.6" stroke-linecap="round"/>')
        if "snow_roof" in deco:
            out.append(f'<path d="M{sx - 9:.1f} {sy - 21:.1f}l2 1M{sx + 6:.1f} {sy - 25:.1f}l2 1M{sx - 2:.1f} {sy - 25:.1f}l2 1" '
                       f'stroke="#f4f8ff" stroke-width="2" stroke-linecap="round"/>')
        if THEME["garland"]:
            cols = THEME["garland"]
            for i in range(9):
                bx, by = sx + rng.uniform(-9, 9), sy - rng.uniform(10, 26)
                out.append(f'<circle class="blink" style="animation-delay:{i * .23:.2f}s" cx="{bx:.1f}" cy="{by:.1f}" r="1.3" '
                           f'fill="{cols[i % len(cols)]}" opacity="{.5 + .5 * L:.2f}" filter="url(#glow)"/>')
    else:
        col = THEME["foliage"] or ("#3b1f4a" if key == "halloween" else ("#1f6b5a" if key == "cyber" else "#2e8b57"))
        out += [f'<circle cx="{sx + dx:.1f}" cy="{sy + dy:.1f}" r="{r}" fill="{shade(col, k)}"/>'
                for dx, dy, r, k in [(-5, -17, 6, .8), (5, -18, 6, .7), (0, -24, 7.5, 1)]]
        if key == "halloween":
            out.append(pumpkin(sx + 6, sy - 1, 3.5))
    return "".join(out)


def gnome(sx, sy) -> str:
    return (f'<path d="M{sx - 2.5:.1f} {sy:.1f}h5l-1-5h-3z" fill="#3b82f6"/><circle cx="{sx:.1f}" cy="{sy - 6:.1f}" r="1.8" fill="#f1c27d"/>'
            f'<path d="M{sx - 2:.1f} {sy - 7:.1f}L{sx:.1f} {sy - 12:.1f}L{sx + 2:.1f} {sy - 7:.1f}z" fill="#d62828"/>'
            f'<path d="M{sx - 1.6:.1f} {sy - 5.4:.1f}q1.6 3 3.2 0" fill="#fff"/>')


def swing(x, y) -> str:
    a, b = P(x, y, 1.8), P(x + 1.4, y, 1.8)
    return (line(P(x, y), a, "#8a5a2b", 1.4) + line(P(x + 1.4, y), b, "#8a5a2b", 1.4) + line(a, b, "#8a5a2b", 1.4)
            + f'<g class="bob" style="animation-duration:2.2s">{line(P(x + .5, y, 1.8), P(x + .5, y, .5), "#c9d6e5", .5)}'
            f'{line(P(x + .9, y, 1.8), P(x + .9, y, .5), "#c9d6e5", .5)}{box(x + .45, y - .1, .45, .5, .2, .06, "#ff4d6d")}</g>')


def doghouse(x, y) -> str:
    sx, sy = P(x + .4, y + .7, 0)
    return (box(x, y, 0, .8, .7, .55, "#c0392b")
            + poly([P(x - .05, y + .35, .95), P(x + .85, y + .35, .95), P(x + .85, y + .75, .55), P(x - .05, y + .75, .55)], "#7a2418")
            + f'<g class="walk" style="animation-duration:.6s"><ellipse cx="{sx + 7:.1f}" cy="{sy - 2:.1f}" rx="2.6" ry="1.4" fill="#c68642"/>'
            f'<circle cx="{sx + 9.2:.1f}" cy="{sy - 3:.1f}" r="1.2" fill="#c68642"/></g>')


def bbq(x, y) -> str:
    sx, sy = P(x, y, .7)
    return (line(P(x, y), (sx, sy), "#3a4a63", 1) + f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="4" ry="2" fill="#111"/>'
            f'<circle class="smoke" style="animation-delay:.4s" cx="{sx:.1f}" cy="{sy - 3:.1f}" r="2" fill="#8aa0b8"/>')


def greenhouse(x, y) -> str:
    return (box(x, y, 0, 1.2, .9, .8, "#bfe3ff", 'opacity=".45"')
            + poly([P(x, y + .45, 1.2), P(x + 1.2, y + .45, 1.2), P(x + 1.2, y + .9, .8), P(x, y + .9, .8)], "#dff3ff", 'opacity=".5"'))


def neighbour_plot(x, w, y_hedge, y_front, L, rng: random.Random) -> str:
    """Lawn, hedge on the street side, a tall item behind the house and a small one in front."""
    key, deco = THEME["key"], THEME["deco"]
    snowy = "snow_roof" in deco
    lawn = "#2a3442" if snowy else "#14281f"
    out = [poly([P(x - .45, y_hedge, .01), P(x + w + .45, y_hedge, .01), P(x + w + .45, y_front, .01),
                 P(x - .45, y_front, .01)], lawn, f'stroke="{shade(lawn, 1.3)}" stroke-width=".5"')]
    hedge = "#1f5a36"
    out.append(box(x - .45, y_hedge, 0, w + .9, .3, .45, hedge))
    if snowy:
        out.append(poly([P(x - .45, y_hedge, .46), P(x + w + .45, y_hedge, .46), P(x + w + .45, y_hedge + .3, .46),
                         P(x - .45, y_hedge + .3, .46)], "#f4f8ff"))
    if THEME["garland"] and key != "cyber":
        cols = THEME["garland"]
        for i in range(6):
            gx, gy = P(x - .3 + i * (w + .6) / 5, y_hedge + .3, .45)
            out.append(f'<circle class="blink" style="animation-delay:{i * .3:.1f}s" cx="{gx:.1f}" cy="{gy:.1f}" r="1.1" '
                       f'fill="{cols[i % len(cols)]}" opacity="{.5 + .5 * L:.2f}" filter="url(#glow)"/>')
    back = rng.choice(["tree", "swing", "greenhouse", "tree"])
    if back == "tree":
        out.append(street_tree(x + .2, y_hedge + 1.2, L, rng))
    elif back == "swing":
        out.append(swing(x + w - 1.2, y_hedge + .9))
    else:
        out.append(greenhouse(x - .3, y_hedge + .6))
    return "".join(out)


def neighbour_front(x, w, y_front, L, rng: random.Random) -> str:
    """Small things on the front lawn, facing the viewer (and the seasonal touch)."""
    key, deco = THEME["key"], THEME["deco"]
    out = []
    pick = rng.choice(["gnome", "dog", "bbq", "mailbox", "flowers"])
    fx, fy = x + w + .1, y_front - .5
    if pick == "gnome":
        out.append(gnome(*P(fx, fy)))
    elif pick == "dog":
        out.append(doghouse(x + w - .6, y_front - 1.0))
    elif pick == "bbq" and key not in ("hiver", "noel", "nouvel_an"):
        out.append(bbq(fx, fy))
    elif pick == "mailbox":
        out.append(mailbox(fx, fy - .3, rng.random() < .5))
    else:
        out.append(flowers(rng, x - .3, x + w + .3, y_front - .35, y_front - .1, 10))
    if key == "halloween":
        out.append(pumpkin(*P(x - .1, y_front - .3), 3.6))
    elif key == "noel":
        out.append(_mini_xmas(x - .1, y_front - .3, rng))
    elif "snowman" in deco:
        sx, sy = P(x - .1, y_front - .3)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy - 4:.1f}" r="4" fill="#eef4ff"/><circle cx="{sx:.1f}" cy="{sy - 10:.1f}" r="3" fill="#eef4ff"/>'
                   f'<path d="M{sx + 1:.1f} {sy - 10:.1f}l3 .6-3 .6z" fill="#ff7b00"/>')
    elif key in ("printemps", "ete", "quatorze_juillet"):
        out.append(flowers(rng, x - .3, x + w + .3, y_front - .35, y_front - .1, 8))
    return "".join(out)


def _mini_xmas(x, y, rng: random.Random) -> str:
    sx, sy = P(x, y)
    out = [f'<path d="M{sx - 5:.1f} {sy - 2:.1f}L{sx:.1f} {sy - 16:.1f}L{sx + 5:.1f} {sy - 2:.1f}z" fill="#1f6b3a"/>',
           f'<path class="beam" d="M{sx:.1f} {sy - 19:.1f}l1 2.4 2.6.2-2 1.6.7 2.6-2.3-1.4-2.3 1.4.7-2.6-2-1.6 2.6-.2z" fill="#ffd166"/>']
    cols = THEME["garland"] or ["#ff4d6d", "#ffd166"]
    for i in range(5):
        out.append(f'<circle class="blink" style="animation-delay:{i * .3:.1f}s" cx="{sx + rng.uniform(-3, 3):.1f}" '
                   f'cy="{sy - 4 - i * 2.2:.1f}" r="1" fill="{cols[i % len(cols)]}" filter="url(#glow)"/>')
    return "".join(out)
