"""Panel 2 — isometric smart home.

* garden: the contribution calendar in 3D, 1 pillar = 1 day (height = events)
* 12 front windows: the last 12 months (top floor = older), brightness = activity
* sky: real time of day + average weather over France (environment.py)
* garage door open = I have open PRs · car in the driveway = I shipped a release this week
* intrusion mode: someone opened an issue on one of my repos this week → alarm beacon
* seasonal decorations from the active theme (seasons.py)
"""

from __future__ import annotations

import datetime as dt
import math
import random

from .. import ctf, environment
from ..svg import EDGE, RED, THEME, document, esc, shade, text
from . import props
from .iso import P, box, halo_defs, line, poly, pts, quad_x, quad_y

H = 512
HX0, HX1, HY0, HY1, WALL = 30, 44, -13, -3, 7.5   # house footprint & wall height
RIDGE_Y, RIDGE_Z, EAVE_Z = -8, 11.05, 7.15
LIGHT = {"night": 1.0, "dusk": .9, "dawn": .7, "day": .12}

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
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
.burst { animation: burst 2.6s ease-out infinite; opacity: 0; transform-box: fill-box; transform-origin: center; }
@keyframes burst { 0% { opacity: 1; transform: scale(.05); } 65% { opacity: 1; } 100% { opacity: 0; transform: scale(1); } }
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 30s linear infinite; transform-box: fill-box; transform-origin: center; }
.fly { animation: fly .9s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes fly { 50% { transform: scaleY(.35); } }
.beam { animation: beam 2s ease-in-out infinite; }
@keyframes beam { 0%,100% { opacity: .25; } 50% { opacity: 1; } }
.firefly { animation: ff 4s ease-in-out infinite; }
@keyframes ff { 0%,100% { opacity: 0; transform: translate(0,0); } 50% { opacity: 1; transform: translate(6px,-10px); } }
.holo { animation: holo 4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes holo { 0%,100% { transform: scaleX(1); opacity: .9; } 50% { transform: scaleX(-1); opacity: .6; } 52% { opacity: .2; } 54% { opacity: .8; } }
.drift { animation: drift linear infinite; }
@keyframes drift { from { transform: translateX(-180px); } to { transform: translateX(1000px); } }
.fogband { animation: fogb 18s ease-in-out infinite alternate; }
@keyframes fogb { from { transform: translateX(-60px); } to { transform: translateX(60px); } }
.flash { opacity: 0; animation: flash 7s linear infinite; }
@keyframes flash { 0%, 100% { opacity: 0; } 61% { opacity: 0; } 62% { opacity: .55; } 63% { opacity: 0; } 65% { opacity: .35; } 66% { opacity: 0; } }
.alarm { animation: alarm 1.2s ease-in-out infinite; }
.peck { animation: peck 4s ease-in-out infinite; transform-box: fill-box; transform-origin: 50% 100%; }
@keyframes peck { 0%, 80%, 100% { transform: rotate(0); } 85% { transform: rotate(18deg); } 90% { transform: rotate(0); } 93% { transform: rotate(14deg); } }
.ups { animation: ups 3s ease-in-out infinite; }
.walk { animation: walk .45s ease-in-out infinite alternate; }
@keyframes walk { to { transform: translateY(-1.2px); } }
.legA, .legB { transform-box: fill-box; transform-origin: 50% 0; animation: legs .45s ease-in-out infinite alternate; }
.legB { animation-direction: alternate-reverse; }
@keyframes legs { from { transform: rotate(22deg); } to { transform: rotate(-22deg); } }
@keyframes ups { 0%,100% { opacity: 1; } 50% { opacity: .3; } }
@keyframes alarm { 0%,100% { opacity: .05; } 50% { opacity: .5; } }
"""


def fall_css(h: int) -> str:
    return (f"@keyframes fallA {{ from {{ transform: translate(0,-20px) rotate(0); }} to {{ transform: translate(40px,{h}px) rotate(320deg); }} }}"
            f"@keyframes fallB {{ from {{ transform: translate(0,-20px) rotate(0); }} to {{ transform: translate(-50px,{h}px) rotate(-280deg); }} }}"
            f"@keyframes rain {{ from {{ transform: translate(0,-30px); }} to {{ transform: translate(-60px,{h}px); }} }}")


# ------------------------------------------------------------------ sky & weather

SKY = {  # (top colour, top opacity, mid colour, mid opacity)
    "night": ("#0e1a3a", .55, "#0b1430", .2),
    "dawn": ("#ff9a6b", .45, "#7a4fa0", .2),
    "day": ("#3a7bd5", .55, "#1c3b63", .25),
    "dusk": ("#ff5e7e", .45, "#4a2f7a", .25),
}


def sky(env: dict, rng: random.Random) -> str:
    phase = env["phase"]
    top, top_o, mid, mid_o = SKY[phase]
    gloomy = env["weather"] in ("rain", "storm", "fog")
    if gloomy:
        top, mid = shade(top, .6), shade(mid, .6)
    out = [f'<defs><linearGradient id="skyg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{top}" stop-opacity="{top_o}"/>'
           f'<stop offset=".45" stop-color="{mid}" stop-opacity="{mid_o}"/><stop offset="1" stop-color="{mid}" stop-opacity="0"/>'
           f'</linearGradient><filter id="fogblur"><feGaussianBlur stdDeviation="10"/></filter></defs>'
           f'<rect x="1" y="1" width="838" height="{H * .75:.0f}" rx="14" fill="url(#skyg)"/>']
    if phase != "day" and not gloomy:
        star_o = 1 if phase == "night" else .4
        for _ in range(50):
            x, y = rng.uniform(20, 820), rng.uniform(30, 230)
            if x < 430 and y < 100:          # keep the title area clean
                continue
            out.append(f'<circle class="twinkle" style="animation-delay:{rng.uniform(0, 3):.2f}s" cx="{x:.0f}" cy="{y:.0f}" '
                       f'r="{rng.uniform(.5, 1.4):.1f}" fill="#dfe8ff" opacity="{star_o}"/>')
    mx, my = 788, 64
    if phase == "night":
        moon = "#ffb347" if THEME["key"] == "halloween" else "#f3f1d0"
        out.append(f'<circle cx="{mx}" cy="{my}" r="24" fill="{moon}" filter="url(#softglow)" opacity=".95"/>'
                   f'<circle cx="{mx - 7}" cy="{my - 5}" r="4" fill="{shade(moon, .85)}"/>'
                   f'<circle cx="{mx + 8}" cy="{my + 7}" r="3" fill="{shade(moon, .85)}"/>')
    elif not (gloomy or env["weather"] == "snow") or phase != "day":
        sun = {"day": "#ffd166", "dawn": "#ff9a4d", "dusk": "#ff6b4a"}[phase]
        sy = my if phase == "day" else 128
        rays = "".join(f'<path d="M{mx} {sy - 30}V{sy - 40}" stroke="{sun}" stroke-width="2.5" stroke-linecap="round" '
                       f'transform="rotate({a} {mx} {sy})"/>' for a in range(0, 360, 30))
        out.append(f'<g class="spin">{rays}</g><circle cx="{mx}" cy="{sy}" r="22" fill="{sun}" filter="url(#softglow)"/>')
    return "".join(out)


def clouds(env: dict, rng: random.Random) -> str:
    n = round((env.get("cloud") or 0) / 20)
    if env["weather"] in ("cloudy", "rain", "storm"):
        n = max(n, 3)
    dark = env["phase"] == "night" or env["weather"] in ("rain", "storm")
    col = "#2a3448" if dark else "#e3ebf7"
    op = .85 if env["weather"] == "storm" else (.7 if dark else .45)
    out = []
    for _ in range(n):
        y, s, dur = rng.uniform(26, 150), rng.uniform(.8, 1.5), rng.uniform(70, 130)
        puff = "".join(f'<ellipse cx="{dx * s:.0f}" cy="{dy * s:.0f}" rx="{rx * s:.0f}" ry="{ry * s:.0f}" fill="{col}"/>'
                       for dx, dy, rx, ry in [(0, 0, 40, 14), (-22, 4, 24, 11), (24, 3, 28, 12), (4, -9, 24, 13)])
        out.append(f'<g transform="translate(0,{y:.0f})"><g class="drift" style="animation-duration:{dur:.0f}s;'
                   f'animation-delay:{-rng.uniform(0, dur):.0f}s" opacity="{op}">{puff}</g></g>')
    return "".join(out)


def precipitation(kind: str, rng: random.Random) -> str:
    out = []
    if kind in ("rain", "storm"):
        for _ in range(110 if kind == "storm" else 80):
            x, d = rng.uniform(0, 900), rng.uniform(.55, .95)
            out.append(f'<g transform="translate({x:.0f},0)"><path d="M0 0l-3 10" stroke="#9cc8ff" stroke-width="1.1" '
                       f'opacity="{rng.uniform(.35, .8):.2f}" style="animation:rain {d:.2f}s linear {-rng.uniform(0, d):.2f}s infinite"/></g>')
        if kind == "storm":
            out.append(f'<rect class="flash" x="1" y="1" width="838" height="{H - 2}" rx="14" fill="#eaf2ff"/>'
                       '<path class="flash" d="M610 30l-16 46h14l-12 44 34-58h-16l14-32z" fill="#fff6c2" filter="url(#glow)"/>')
        return "".join(out)
    if kind == "fog":
        return "".join(f'<ellipse class="fogband" style="animation-delay:{-i * 5}s" cx="{420 + i * 60}" cy="{180 + i * 110}" '
                       f'rx="520" ry="34" fill="#c9d6e5" opacity=".16" filter="url(#fogblur)"/>' for i in range(3))
    n = {"snow": 70, "leaves": 22, "petals": 26, "fireflies": 22, "confetti": 60}[kind]
    for i in range(n):
        x = rng.uniform(0, 840)
        dur = rng.uniform(9, 17)
        anim = f"{'fallA' if i % 2 else 'fallB'} {dur:.1f}s linear {-rng.uniform(0, dur):.1f}s infinite"
        if kind == "snow":
            shape = f'<circle r="{rng.uniform(.8, 2.4):.1f}" fill="#f4f8ff" opacity="{rng.uniform(.45, .95):.2f}"/>'
        elif kind == "fireflies":
            fx, fy = rng.uniform(40, 800), rng.uniform(250, 490)
            out.append(f'<circle class="firefly" style="animation-delay:{rng.uniform(0, 4):.2f}s" cx="{fx:.0f}" cy="{fy:.0f}" '
                       f'r="1.8" fill="#fff07a" filter="url(#glow)"/>')
            continue
        elif kind == "confetti":
            cols = THEME["garland"] or ["#ffd166", "#ff2fd0", "#00e5ff"]
            shape = f'<rect width="4" height="2" fill="{cols[i % len(cols)]}"/>'
        else:
            cols = ["#e07b39", "#c0392b", "#ffb547", "#a0522d"] if kind == "leaves" else ["#ffb3d9", "#ff8fd8", "#fff0f7"]
            shape = f'<ellipse rx="4" ry="1.9" fill="{cols[i % len(cols)]}" opacity=".9"/>'
        out.append(f'<g transform="translate({x:.0f},0)"><g style="animation:{anim}">{shape}</g></g>')
    return "".join(out)


def pick_particles(env: dict) -> list[str]:
    """Real precipitation wins over decorative particles; festive snow/confetti stay anyway."""
    w, seasonal = env["weather"], THEME["particles"]
    kinds = [w] if w in ("rain", "storm", "snow", "fog") else []
    if not seasonal:
        return kinds
    if seasonal == "fireflies":
        if env["phase"] in ("night", "dusk") and w not in ("rain", "storm", "snow"):
            kinds.append(seasonal)
    elif seasonal == "snow":
        if (w is None or THEME["key"] in ("noel", "nouvel_an")) and "snow" not in kinds:
            kinds.append(seasonal)
    elif w not in ("rain", "storm"):
        kinds.append(seasonal)
    return kinds


# ------------------------------------------------------------------ the house

def house(months_power: list[float], hot: int, live: int, L: float, intrusion: bool, outage: bool,
          ticker_msg: str, inverter_lines: tuple[str, str, str]) -> str:
    """`outage`: no contribution for a week → mains lost, the house runs on its UPS (lights off)."""
    neon_a, neon_b = THEME["neon"]
    edge = f'stroke="{neon_a}" stroke-opacity=".75" stroke-width="1.2" stroke-linejoin="round"'
    deco = THEME["deco"]
    snow = "snow_roof" in deco
    out = []

    # walls
    out.append(quad_y(HX0, HX1, HY1, 0, WALL, "#111b2b", edge))
    out.append(quad_x(HX1, HY0, HY1, 0, WALL, "#0b1320", edge))
    if outage:
        L = 0.0

    # 12 month windows on the front wall (top floor = older months)
    win = THEME["window"]
    for i, p in enumerate(months_power):
        row, col = divmod(i, 6)
        z0 = 4.9 if row == 0 else 1.2
        x0 = HX0 + .8 + col * 2.15
        out.append(quad_y(x0 - .1, x0 + 1.45, HY1, z0 - .15, z0, "#2b3a52"))   # sill
        if p <= 0 or outage:
            out.append(quad_y(x0, x0 + 1.35, HY1, z0, z0 + 1.6, "#0a111c", f'stroke="{EDGE}"'))
            continue
        cls = "flick" if i == hot else ("beam" if i == live else "")
        out.append(quad_y(x0, x0 + 1.35, HY1, z0, z0 + 1.6, win, f'fill-opacity="{.25 + .75 * p:.2f}" class="{cls}" filter="url(#glow)"'))
        out.append(line(P(x0 + .675, HY1, z0), P(x0 + .675, HY1, z0 + 1.6), "#111b2b", 1))
        if "candles" in deco:   # Scandinavian candle bridge
            for k in range(5):
                cx, cy = P(x0 + .25 + k * .21, HY1, z0 + .15 + .35 * math.sin(math.pi * k / 4))
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r=".9" fill="#fff3c4"/>')

    # side: door (+ wreath), lantern, server-room window with blinking LEDs
    out.append(quad_x(HX1, -6.3, -4.9, 0, 2.7, "#1a2740", edge))
    kx, ky = P(HX1, -5.15, 1.3)
    out.append(f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="1.2" fill="{neon_b}"/>')
    if "wreath" in deco:
        wx, wy = P(HX1, -5.6, 2.05)
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="4" fill="none" stroke="#1f8a4c" stroke-width="2.6"/>'
                   f'<path d="M{wx - 2:.1f} {wy + 3:.1f}l2-1.5 2 1.5" stroke="#ff4d6d" stroke-width="1.6" fill="none"/>'
                   + "".join(f'<circle class="blink" style="animation-delay:{k * .3:.1f}s" cx="{wx + 4 * math.cos(k):.1f}" '
                             f'cy="{wy + 4 * math.sin(k):.1f}" r=".9" fill="#ffd166"/>' for k in range(6)))
    out.append(props.lantern(P(HX1, -6.75, 2.3), L))
    out.append(quad_x(HX1, -11.4, -9.2, 4.8, 6.6, "#050a12", edge))
    for j in range(3):
        for k in range(3):
            lx, ly = P(HX1, -11.0 + k * .7, 5.2 + j * .55)
            c = "#ffb547" if outage else ("#39ff88" if (j + k) % 3 else RED)
            out.append(f'<circle class="blink" style="animation-delay:{(j * 3 + k) * .23:.2f}s" cx="{lx:.1f}" cy="{ly:.1f}" r="1.1" fill="{c}"/>')

    # gable + round attic window
    out.append(poly([P(HX1, HY0, WALL), P(HX1, HY1, WALL), P(HX1, RIDGE_Y, RIDGE_Z - .35)], "#0b1320", edge))
    attic = [P(HX1, RIDGE_Y + .8 * math.cos(t), 8.75 + .8 * math.sin(t)) for t in [k * math.pi / 8 for k in range(16)]]
    out.append(poly(attic, "#0a111c" if outage else win, 'fill-opacity=".8" filter="url(#glow)" class="beam"'))
    # solar inverter (or UPS) screen on the side wall, LED ticker with my last commit on the front
    out.append(props.inverter(HX1, -7.3, -11.3, 2.75, 1.45, *inverter_lines))
    out.append(props.ticker(HX0 + .3, HX1 - .3, HY1, 4.5, 1.45, ticker_msg, "#ffb547" if not outage else "#5c6f88"))

    # roof: back plane, chimney + smoke, front plane
    back = [P(HX0 - .5, HY0 - .5, EAVE_Z), P(HX1 + .5, HY0 - .5, EAVE_Z), P(HX1 + .5, RIDGE_Y, RIDGE_Z), P(HX0 - .5, RIDGE_Y, RIDGE_Z)]
    out.append(poly(back, "#e8f0fa" if snow else "#162034", edge))
    out.append(box(33, -11.2, 8.6, 1.4, 1.4, 4.0, "#3a2f3a", f'stroke="{neon_a}" stroke-opacity=".4" stroke-width=".6"'))
    smx, smy = P(33.7, -10.5, 12.6)
    for k in range(3):
        out.append(f'<circle class="smoke" style="animation-delay:{k * 1.5}s" cx="{smx:.1f}" cy="{smy - 3:.1f}" r="4" fill="{THEME["smoke"]}"/>')

    def roof_pt(x, t):
        return P(x, RIDGE_Y + (HY1 + .5 - RIDGE_Y) * t, RIDGE_Z - (RIDGE_Z - EAVE_Z) * t)

    out.append(poly([roof_pt(HX0 - .5, 0), roof_pt(HX1 + .5, 0), roof_pt(HX1 + .5, 1), roof_pt(HX0 - .5, 1)], "#1a2438", edge))
    # solar panels (energy = commits), shimmering
    for r in range(2):
        for c in range(5):
            x0, t0 = HX0 + 1 + c * 2.45, .14 + r * .4
            quad = [roof_pt(x0, t0), roof_pt(x0 + 2.2, t0), roof_pt(x0 + 2.2, t0 + .34), roof_pt(x0, t0 + .34)]
            out.append(poly(quad, "#0d2c52", f'stroke="{neon_a}" stroke-opacity=".55" stroke-width=".7"'))
            if not outage:
                out.append(poly(quad, neon_a, f'class="sweep" style="animation-delay:{1 + c * .25 + r * .1:.2f}s"'))
    if snow:
        out.append(poly([roof_pt(HX0 - .5, 0), roof_pt(HX1 + .5, 0), roof_pt(HX1 + .5, .12), roof_pt(HX0 - .5, .12)], "#f4f8ff"))
        out.append(poly([roof_pt(HX0 - .5, .92), roof_pt(HX1 + .5, .92), roof_pt(HX1 + .5, 1), roof_pt(HX0 - .5, 1)], "#f4f8ff"))
    if "icicles" in deco:
        for i in range(30):
            ix, iy = roof_pt(HX0 - .4 + i * .5, 1)
            ln = 3 + (i * 7) % 6
            out.append(f'<path class="twinkle" style="animation-delay:{(i % 5) * .4:.1f}s" d="M{ix - 1:.1f} {iy:.1f}l1 {ln}l1 -{ln}z" '
                       f'fill="#dff3ff" opacity=".9"/>')

    # antenna (+ star / flag) and zigbee/thread mesh waves
    ax, ay = P(41, RIDGE_Y, RIDGE_Z)
    tx, ty = P(41, RIDGE_Y, RIDGE_Z + 3.4)
    out.append(line((ax, ay), (tx, ty), neon_a, 1.6))
    if "star" in deco:
        out.append(f'<path class="beam" d="M{tx:.1f} {ty - 8:.1f}l2.4 5.6 6 .4-4.6 3.8 1.6 6-5.4-3.4-5.4 3.4 1.6-6-4.6-3.8 6-.4z" '
                   f'fill="#ffd166" filter="url(#glow)"/>')
    else:
        out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="2.5" fill="{neon_b}" filter="url(#glow)"/>')
    for k in range(3):
        out.append(f'<circle class="wave" style="animation-delay:{k * .85:.2f}s" cx="{tx:.1f}" cy="{ty:.1f}" r="16" fill="none" '
                   f'stroke="{neon_a}" stroke-width="1"/>')
    if "flag" in deco:
        fx, fy = tx + 1, ty
        out.append(f'<g class="bob"><rect x="{fx:.1f}" y="{fy:.1f}" width="6" height="11" fill="#3b82f6"/>'
                   f'<rect x="{fx + 6:.1f}" y="{fy:.1f}" width="6" height="11" fill="#f5f5f5"/>'
                   f'<rect x="{fx + 12:.1f}" y="{fy:.1f}" width="6" height="11" fill="#ef4444"/></g>')

    # light string on the eaves and gable
    if THEME["garland"] and not outage:
        cols = THEME["garland"]
        dots = [roof_pt(HX0 - .5 + i * .75, 1) for i in range(21)]
        dots += [P(HX1 + .5, RIDGE_Y + (HY1 + .5 - RIDGE_Y) * t, RIDGE_Z - (RIDGE_Z - EAVE_Z) * t) for t in (i / 8 for i in range(9))]
        for i, (gx, gy) in enumerate(dots):
            out.append(f'<circle class="blink" style="animation-delay:{(i % 4) * .25:.2f}s" cx="{gx:.1f}" cy="{gy + 2:.1f}" r="1.9" '
                       f'fill="{cols[i % len(cols)]}" opacity="{.55 + .45 * L:.2f}" filter="url(#glow)"/>')

    # smart-home & security gear
    out.append(props.camera(HX0 + .2, HY1, 7.0, flip=True) + props.camera(HX1, HY1 + .1, 7.0))
    out.append(props.unifi_ap(37, HY1, 7.05))
    if "web" in deco:
        out.append(props.web(*P(HX0, HY1, WALL)))
    if intrusion:
        out.append(props.beacon(*P(36.5, RIDGE_Y, RIDGE_Z + .3)))
    return "".join(out)


def mower() -> str:
    ox, oy = P(0, 0)
    body = f'<g transform="translate({-ox:.1f},{-oy:.1f})">{box(-.5, -.35, 0, 1.0, .7, .35, "#39ff88")}</g>'
    x1, y1 = P(.5, 7.55)
    x2, y2 = P(52.5, 7.55)
    return (f'<g>{body}<circle class="blink" cx="0" cy="-6" r="1.5" fill="{RED}"/>'
            f'<animateMotion dur="40s" repeatCount="indefinite" path="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}L{x1:.1f} {y1:.1f}"/></g>')


def yard(rng: random.Random, L: float) -> str:
    """Front-left corner of the scene: the seasonal set piece."""
    deco, out = THEME["deco"], []
    if "xmas_tree" in deco:
        out.append(props.pine(4.5, 12.5, snowy=True, xmas=True, rng=rng))
    elif "pine" in deco:
        out.append(props.pine(4.5, 12.5, snowy=True) + props.pine(2.8, 15.2, snowy=True))
    elif "dead_tree" in deco:
        out.append(props.dead_tree(4.5, 12.5))
    elif THEME["foliage"]:
        out.append(props.tree(4.5, 12.5, THEME["foliage"]))
    if "pool" in deco:
        out.append(props.pool(6.5, 10.5, 13.2, 15.6) + props.parasol(12.4, 12.4) + props.deckchair(13.2, 14.2))
    else:
        if "gifts" in deco:
            out.append(props.gifts(7.2, 13.3))
        if "tombstones" in deco:
            out.append(props.tombstone(7.5, 12.6, -6) + props.tombstone(9.6, 14.2, 4) + props.tombstone(12.4, 12.4, -3))
        if "parasol" in deco:
            out.append(props.parasol(8, 13.5))
        if "deckchair" in deco:
            out.append(props.deckchair(9.4, 13.0))
        if "leaf_piles" in deco:
            out.append(props.leaf_pile(8, 13.6, rng))
    if "reindeer" in deco:
        out.append(props.reindeer(12, 12.4, L))
    if "snowman" in deco:
        out.append(props.snowman(15.6, 13.2))
    if "scarecrow" in deco:
        out.append(props.scarecrow(12, 12.6))
    if "birdhouse" in deco:
        out.append(props.birdhouse(11, 12.8))
    if "sled" in deco:
        out.append(props.sled(9, 13.4))
    if "mushrooms" in deco:
        out.append(props.mushrooms(15, 13.8))
    if "pumpkins" in deco:
        out.append(props.pumpkin(*P(15, 13.6), 8) + props.pumpkin(*P(16.8, 14.6), 5.5))
    if "flowers" in deco:
        out.append(props.flowers(rng, 6, 16, 11.5, 15.5, 26))
    if "light_bushes" in deco and "pool" not in deco:
        out.append(props.bush(17.5, 15.2, rng, lights=True, r=6))
    return "".join(out)


def lot_front(rng: random.Random, L: float, st: dict, data: dict) -> str:
    """Everything standing on the front strip of the lot, between the house and the garden."""
    deco, out = THEME["deco"], []
    snowy = "snowy_bushes" in deco or "snow_roof" in deco
    out.append(props.stepping_stones([(44.9, -5.6), (45.7, -5.5), (46.5, -5.6)]))
    out.append(props.bush(46.4, -3.3, rng, "light_bushes" in deco, snowy))
    if st["release"]:
        out.append(props.car(st["release"], L))
    out.append(props.mailbox(31.0, -2.0, data["prs"] > 0))
    if "flowers" in deco:
        out.append(props.flowers(rng, 32, 44.5, -1.6, -1.15))
    if "pumpkins" in deco:
        for x, y, r in [(32.6, -1.4, 6), (38.2, -1.4, 7.5), (41.2, -1.6, 5.5)]:
            out.append(props.pumpkin(*P(x, y), r))
    if "leaf_piles" in deco:
        out.append(props.leaf_pile(39, -1.8, rng))
    lamps = [(24.0, -1.6), (35.5, -1.6), (45.8, -1.7)]
    for x, y in lamps:
        out.append(props.lamp_post(x, y, L))
    heads = [P(x, y, 2.6) for x, y in lamps]
    if "guinguette" in deco:
        for a, b in zip(heads, heads[1:]):
            out.append(props.string_lights(a, b, ["#ffd27a"], L))
    if "bunting" in deco:
        for a, b in zip(heads, heads[1:]):
            out.append(props.bunting((a[0], a[1] + 4), (b[0], b[1] + 4), ["#3b82f6", "#f5f5f5", "#ef4444"]))
    return "".join(out)


# ------------------------------------------------------------------ street life

def street(st: dict, env: dict, L: float) -> str:
    rng = random.Random(11)
    key = THEME["key"]
    rainy = env["weather"] in ("rain", "storm")
    out = [props.sidewalk(0, 53, 7.72, 8.28)]

    walkers = [("adult", True, 70, 0), ("kid", True, 60, 22), ("jogger", True, 28, 6), ("walker", True, 82, 44),
               ("elder", False, 110, 12), ("adult", False, 75, 50), ("kid", False, 62, 30)]
    if key == "halloween":
        walkers = [(("ghost_kid" if i % 2 else "witch_kid") if k == "kid" else k, f, d, b)
                   for i, (k, f, d, b) in enumerate(walkers)] + [("ghost_kid", True, 64, 40)]
    if key == "noel":
        walkers.append(("santa", False, 90, 70))
    for kind, fwd, dur, begin in walkers:
        out.append(props.stroll(props.person(kind, rng, umbrella=rainy), fwd,
                                props.WALK_FWD if fwd else props.WALK_BACK, dur, begin))

    out.append(props.road(0, 53, 8.3, 9.9))
    # incidents park a vehicle at the curb in front of the house
    if st["intrusions"]:
        out.append(props.parked(props.vehicle("police", True, L), 37, 8.55))
    if st["outage"]:
        out.append(props.parked(props.vehicle("grid", True, L), 41.5, 8.55))
    fwd = ["car:#ff4d6d", "bus", "police", "car:#39ff88", "school"]
    back = ["fire", "car:#ffd166", "van", "ambulance", "garbage", "car:#a64dff"]
    for lane, kinds, forward, dur in ((props.LANE_FWD, fwd, True, 26), (props.LANE_BACK, back, False, 30)):
        x0, x1 = (-3, 56) if forward else (56, -3)
        for i, kind in enumerate(kinds):
            out.append(props.drive(props.vehicle(kind, forward, L), x0, x1, lane, dur, i * dur / len(kinds)))
    return "".join(out)


# ------------------------------------------------------------------ live captions

def ticker_text(st: dict) -> str:
    c = st["last_commit"]
    if not c:
        return "▶ no public commit yet · stay tuned · restez branchés"
    age = (st["today"] - dt.date.fromisoformat(c["date"][:10])).days
    when = "today" if age <= 0 else f"{age}d ago"
    return f"▶ last commit · {c['repo']}: {c['headline']} · {when}"


def inverter_lines(st: dict, env: dict) -> tuple[str, str, str]:
    """Solar production = today's contributions (1 event = 1 kWh); the battery takes over at night."""
    if st["outage"]:
        pct = max(5, 100 - 7 * (st["idle_days"] - 7))
        return f"UPS {pct}%", "on battery", "#ffb547"
    kwh = st["today_count"]
    if env["phase"] == "night":
        return f"🔋 {kwh} kWh", "stored today", "#39ff88"
    return f"☀ {kwh} kWh", "solar today", "#ffd166"


def status_line(st: dict) -> tuple[str, str, float]:
    if st["intrusions"]:
        hit = st["intrusions"][0]
        more = f" (+{len(st['intrusions']) - 1})" if len(st["intrusions"]) > 1 else ""
        return f"⚠ INTRUSION: issue {hit['repo']}#{hit['number']}{more}", f'class="pulse" style="fill:{RED}" font-weight="700"', 11
    if st["outage"]:
        return (f"⚡ POWER OUTAGE: idle {st['idle_days']}d, UPS on battery", 'class="ups" style="fill:#ffb547" font-weight="700"', 11)
    if st["birthday"]:
        return "🎂 HAPPY BIRTHDAY · JOYEUX ANNIVERSAIRE !", f'class="pulse" style="fill:{THEME["neon"][1]}" font-weight="700"', 11
    if st["milestone"]:
        m = st["milestone"]
        return f"🎉 {m['repo']} just passed {m['stars']}★", f'class="pulse" style="fill:#ffd166" font-weight="700"', 11
    return "perimeter secure · robot mower on duty", "", 10.5


# ------------------------------------------------------------------ render

def render(cfg: dict, data: dict, st: dict) -> str:
    rng = random.Random(7)
    env = st["env"]
    L = LIGHT[env["phase"]]
    heat = THEME["heat"]
    a, b = THEME["neon"]
    peak = max(st["max_day"], 1)
    days = data["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7    # GitHub weeks start on Sunday
    deco = THEME["deco"]
    intrusion = bool(st["intrusions"])
    outage = st["outage"]
    Lh = 0.0 if outage else L               # lights of my own property
    party = st["birthday"] or st["milestone"]

    totals = [sum(d["count"] for d in ds) for _, ds in st["months"]]
    top = max(totals or [1]) or 1
    power = [t / top for t in totals]
    hot = max(range(len(totals)), key=totals.__getitem__) if any(totals) else -1

    body = [halo_defs([props.WARM, props.COLD, RED]), sky(env, rng), clouds(env, rng)]
    if (THEME["fireworks"] or party) and env["phase"] != "day":
        body.append(props.fireworks(THEME["fireworks"] or ["#ffd166", "#ff2fd0", "#00e5ff", "#39ff88"]))
    if "bats" in deco:
        body.append(props.bats())
    if "sleigh" in deco and env["phase"] in ("night", "dusk"):
        body.append(props.sleigh())

    # lot, fence, weather station, back bushes
    lawn = "#2a3442" if ("snow_roof" in deco or env["weather"] == "snow") else "#0f1f1b"
    body.append(box(13, -15.5, -.35, 34, 14.5, .35, lawn, f'stroke="{EDGE}" stroke-width=".6"'))
    body.append(props.fence(13, 47, -15.5, -1.2))
    body.append(props.weather_station(14.1, -14.4, env))
    lights, snowy = "light_bushes" in deco, "snowy_bushes" in deco
    body.append(props.bush(45.6, -14.2, rng, lights, snowy))

    # garage (door open = open PRs) + driveway, then the house in front of it
    edge = f'stroke="{a}" stroke-opacity=".6" stroke-width="1"'
    gx0, gx1, _, gy1, _ = props.GARAGE
    body.append(poly([P(gx0 + .8, gy1, .01), P(gx1 - .5, gy1, .01), P(gx1 - .5, -1.0, .01), P(gx0 + .8, -1.0, .01)], "#1a2230"))
    body.append(props.garage(data.get("open_prs", 0), bool(st["release"]), Lh, edge))
    body.append(props.bush(23.6, -6.5, rng, lights, snowy, r=6))
    sign = "HBD!" if st["birthday"] else THEME["sign"]
    if sign and not outage:
        year = st["today"].year + (st["today"].month == 12)
        body.append(props.neon_sign(sign.format(year=year), b))
    body.append(house(power, hot, len(totals) - 1, L, intrusion, outage, ticker_text(st), inverter_lines(st, env)))
    for i, x in enumerate([31.2, 35.4, 36.8, 38.2, 39.6, 42.4, 43.6][:min(7, st["stars_week"])]):
        body.append(props.bird(*P(x, RIDGE_Y, RIDGE_Z), b if i % 2 else a, i * .7))
    body.append(lot_front(rng, Lh, st, data))
    if st["birthday"]:
        body.append(props.cake(27.3, -1.9) + props.balloons(31.1, -2.1, 2.2))
    if "ghost" in deco:
        body.append(props.ghost(560, 70))
    if "hologram" in deco:
        body.append(props.hologram(26, 3.5, 6))

    # the garden: 1 pillar per day, back to front
    cells = [((offset + i) // 7, (offset + i) % 7, d) for i, d in enumerate(days)]
    for w, dow, d in sorted(cells, key=lambda c: (c[0] + c[1], c[0])):
        n = d["count"]
        x, y = w + .1, dow + .1
        delay = .3 + w * .035
        if n == 0:
            tile = poly([P(x, y), P(x + .8, y), P(x + .8, y + .8), P(x, y + .8)], heat[0])
            body.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">{tile}</g>')
            continue
        lvl = min(4, 1 + int(3 * math.log1p(n) / math.log1p(peak)))
        dz = .35 + 2.6 * math.sqrt(n / peak)
        top_face = [P(x, y, dz), P(x + .8, y, dz), P(x + .8, y + .8, dz), P(x, y + .8, dz)]
        shine = poly(top_face, "#ffffff", f'class="sweep" style="animation-delay:{3 + w * .06:.2f}s"')
        cap = poly(top_face, "#f4f8ff", 'opacity=".85"') if env["weather"] == "snow" else ""
        body.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">{box(x, y, 0, .8, .8, dz, heat[lvl])}{cap}{shine}'
                    f'<title>{esc(d["date"])}: {n}</title></g>')

    # beacon on today
    w, dow, d = cells[-1]
    bx, by = P(w + .5, dow + .5, .35 + 2.6 * math.sqrt(d["count"] / peak) if d["count"] else 0)
    body.append(f'<path class="beam" d="M{bx:.1f} {by:.1f}V{by - 46:.1f}" stroke="{b}" stroke-width="2" filter="url(#glow)"/>'
                f'<circle class="wave" cx="{bx:.1f}" cy="{by:.1f}" r="7" fill="none" stroke="{b}"/>')
    body.append(text(round(bx), round(by - 52), "today", "", 9, "middle", f'style="fill:{b}"'))
    body.append(mower())

    # the street: sidewalk with passers-by, two lanes of traffic, then my followers' houses across it
    body.append(street(st, env, L))
    nrng = random.Random(3)
    for i, n in enumerate(data.get("neighbours", [])[:6]):
        body.append(props.neighbour(22.5 + i * 4, 10.8, n["total"], n["login"], L, nrng))
    if "butterflies" in deco:
        body.append(props.butterflies())
    body.append(yard(rng, Lh))
    body.append(props.drone())

    # captions
    body.append(text(24, 40, "SMART-HOME // ISO VIEW", "b", 15, extra=f'style="fill:{a}" filter="url(#glow)"'))
    body.append(text(24, 58, "garden: 1 pillar = 1 day · windows: 1 = 1 month", "dim", 10.5))
    body.append(text(24, 72, "jardin : 1 pilier = 1 jour · fenêtres : 1 = 1 mois", "dim", 10.5))
    body.append(text(24, 94, f"{THEME['icon']} {THEME['label']} MODE", "b", 11, extra=f'style="fill:{b}"'))
    rel, prs = st["release"], data.get("open_prs", 0)
    garage = f"garage open ({prs} PRs)" if prs else "garage closed"
    drive = f"car: {rel['tag']} {rel['repo']}" if rel else "no release this week"
    birds = f" · {st['stars_week']} new ★ = {min(7, st['stars_week'])} birds" if st["stars_week"] else ""
    info = [
        (f"{data['total']} events · 365 days · streak {st['current_streak']}d", f'style="fill:{a}" font-weight="700"', 11),
        (environment.describe(env)[0] + (f" · avg of {env['cities']} cities" if env["cities"] else ""), "", 10.5),
        (f"{garage} · {drive}", "", 10.5),
        (f"{inverter_lines(st, env)[0]} {inverter_lines(st, env)[1]}{birds}", "", 10.5),
        status_line(st),
    ]
    for i, (msg, extra, size) in enumerate(info):
        body.append(text(24, 404 + i * 16, msg, "" if extra else "dim", size, extra=extra))
    lx, ly = 690, 494
    body.append(text(lx - 6, ly, "less", "dim", 9.5, "end"))
    for i, c in enumerate(heat):
        body.append(f'<rect x="{lx + i * 15}" y="{ly - 9}" width="11" height="11" rx="2" fill="{c}"/>')
    body.append(text(lx + 5 * 15 + 3, ly, "more", "dim", 9.5))

    kinds = pick_particles(env)
    if st["birthday"] and "confetti" not in kinds:
        kinds.append("confetti")
    for kind in kinds:
        body.append(precipitation(kind, rng))
    body.append(ctf.comment())
    if intrusion:
        body.append(f'<rect class="alarm" x="3" y="3" width="834" height="{H - 6}" rx="13" fill="none" stroke="{RED}" stroke-width="6"/>')
    return document(H, "\n".join(body), f"Isometric smart home built from GitHub contributions ({THEME['label']})",
                    CSS + fall_css(H + 20))
