"""A tiny capture-the-flag hidden in the rendered SVGs (view-source is the way in).

Fragment 1 → XML comment in assets/house.svg
Fragment 2 → invisible text in assets/soc.svg
Fragment 3 → base64 in the <desc> of assets/boot.svg
Yes, reading this file is a valid solve too. Source is a legit recon path.
"""

from __future__ import annotations

import base64

FRAGMENTS = ("JIGSAW{1f_1t_h4s_", "4n_1p_", "1_4ut0m4t3_1t}")


def comment() -> str:
    return f"<!-- 🏁 1/3 · {FRAGMENTS[0]} · the rest is hiding in soc.svg and boot.svg -->"


def invisible() -> str:
    return (f'<text x="830" y="12" font-size="2" fill-opacity="0" aria-hidden="true">'
            f"2/3 · {FRAGMENTS[1]}</text>")


def desc() -> str:
    b64 = base64.b64encode(f"3/3 · {FRAGMENTS[2]}".encode()).decode()
    return f"<desc>maintenance token: {b64}</desc>"
