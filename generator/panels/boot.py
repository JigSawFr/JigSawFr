"""Panel 1 — SSH into the homelab: banner + systemd-style boot log built from real stats."""

from __future__ import annotations

from ..svg import AMBER, CYAN, DIM, GREEN, MAGENTA, document, esc, text, titlebar

BANNER = [
    "     ██╗██╗ ██████╗ ███████╗ █████╗ ██╗    ██╗",
    "     ██║██║██╔════╝ ██╔════╝██╔══██╗██║    ██║",
    "     ██║██║██║  ███╗███████╗███████║██║ █╗ ██║",
    "██   ██║██║██║   ██║╚════██║██╔══██║██║███╗██║",
    "╚█████╔╝██║╚██████╔╝███████║██║  ██║╚███╔███╔╝",
    " ╚════╝ ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ ",
]

CSS = """
.glitch { animation: glitch 6s infinite; }
@keyframes glitch {
  0%, 91%, 100% { transform: translate(0,0); }
  92% { transform: translate(-3px,1px); } 93% { transform: translate(3px,-1px); }
  94% { transform: translate(-1px,0); }
}
.ghost { animation: ghost 6s infinite; opacity: 0; }
@keyframes ghost { 0%,91%,95%,100% { opacity: 0; } 92%,94% { opacity: .6; } }
"""



def typed(x, y, s, begin, cls="green", size=12.5):
    """A command line that types itself (SMIL clip width animation)."""
    w = len(s) * 7.9 + 10  # generous: any monospace font at 12.5px fits
    cid = f"t{int(y)}"
    return (
        f'<clipPath id="{cid}"><rect x="{x}" y="{y - 14}" width="0" height="20">'
        f'<animate attributeName="width" from="0" to="{w}" begin="{begin}s" dur="{len(s) * 0.035:.2f}s" fill="freeze"/>'
        f"</rect></clipPath>"
        f'<g clip-path="url(#{cid})">{text(x, y, s, cls, size)}</g>'
    )


def render(cfg: dict, data: dict, st: dict) -> str:
    years = st["today"].year - int(data["created_at"][:4])
    integ = len(cfg["integrations"])
    body = [titlebar(f"{data['login'].lower()}@{cfg['hostname']} — ssh — 120×32", "● CONNECTED")]

    # banner (top-left) with glitch + magenta ghost copy
    bx, by = 34, 68
    def banner(fill):
        return "".join(
            f'<text x="{bx}" y="{by + i * 15}" font-size="13" textLength="{len(line) * 8.4:.1f}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve" style="fill:{fill}">{esc(line)}</text>'
            for i, line in enumerate(BANNER)
        )

    body.append(f'<g class="ghost" transform="translate(4,0)">{banner(MAGENTA)}</g>')
    body.append(f'<g class="glitch" filter="url(#glow)">{banner("url(#neon)")}</g>')

    # whoami card (top-right)
    cx = 470
    card = [
        (f"{cfg['display_name']}", "b cyan", 15),
        ("IT · Domotique · SecOps", "mag", 11.5),
        (f"loc     {cfg['location']}", "", 11),
        (f"uptime  {years} yrs on GitHub", "", 11),
        (f"repos   {data['repo_count']} public · {st['stars']} ★", "", 11),
        (f"motto   « if it has an IP, I automate it »", "dim", 11),
    ]
    body.append(f'<rect x="{cx - 14}" y="50" width="{840 - cx - 10}" height="114" rx="8" fill="none" stroke="{CYAN}" stroke-opacity=".35"/>')
    for i, (s, cls, size) in enumerate(card):
        body.append(text(cx, 70 + i * 16, s, f"fade {cls}", size,
                         extra=f'style="animation-delay:{0.2 + i * 0.12:.2f}s"'))

    # boot log
    y0 = 186
    t = 0.6
    body.append(typed(30, y0, f"$ ssh {data['login'].lower()}@{cfg['hostname']}", t))
    t += 1.3
    log = [
        ("OK", f"Started home-assistant.service — {integ} integrations loaded"),
        ("OK", "Started crowdsec.service — firewall bouncers armed"),
        ("OK", f"Mounted /dev/github — {data['repo_count']} public repos, {st['stars']} stars"),
        ("OK", f"Reached target contributions.target — {data['total']} events / 365 days"),
        ("OK", f"Started streak.timer — current {st['current_streak']}d, record {st['longest_streak']}d"),
        ("WARN", "coffee.service: level low — please refill ☕ / café à recharger"),
    ]
    for i, (lvl, msg) in enumerate(log):
        y = y0 + 22 + i * 19
        color = GREEN if lvl == "OK" else AMBER
        delay = f"animation-delay:{t + i * 0.28:.2f}s"
        body.append(
            f'<g class="fade" style="{delay}">'
            f'<text x="30" y="{y}" font-size="12" xml:space="preserve"><tspan fill="{DIM}">[</tspan>'
            f'<tspan fill="{color}" font-weight="700">{lvl:^6}</tspan><tspan fill="{DIM}">]</tspan> {esc(msg)}</text></g>'
        )
    t += len(log) * 0.28 + 0.3
    y = y0 + 22 + len(log) * 19 + 8
    body.append(typed(30, y, "$ echo $WELCOME", t))
    t += 0.8
    msg = "Welcome home, visitor. / Bienvenue à la maison."
    body.append(f'<g class="fade" style="animation-delay:{t:.2f}s">{text(30, y + 20, msg, "cyan b", 12.5)}</g>')
    cur_x = 30 + len(msg) * 7.55 + 6
    body.append(f'<rect class="blink" x="{cur_x:.0f}" y="{y + 9}" width="8" height="14" fill="{CYAN}"/>')
    return document(y + 42, "\n".join(body), f"{cfg['display_name']} — homelab boot console")
