"""A tiny capture-the-flag hidden in the rendered SVGs.

The flag itself lives in the PROFILE_CTF_FLAG repository secret, never in the code.
It is split in three fragments, each one encoded differently:

  1/3 → XML comment in assets/house.svg   (rot13)
  2/3 → invisible text in assets/soc.svg  (xor with a short key, hex)
  3/3 → <desc> of assets/boot.svg         (base64)

Without the secret the challenge is simply switched off.
"""

from __future__ import annotations

import base64
import codecs
import os

XOR_KEY = b"HA"   # hint given in the SVG: "the platform that runs my house"


def flag() -> str | None:
    return os.environ.get("PROFILE_CTF_FLAG") or None


def fragments() -> tuple[str, str, str] | None:
    f = flag()
    if not f:
        return None
    n = -(-len(f) // 3)
    return f[:n], f[n:2 * n], f[2 * n:]


def xor_hex(s: str) -> str:
    return bytes(b ^ XOR_KEY[i % len(XOR_KEY)] for i, b in enumerate(s.encode())).hex()


def comment() -> str:
    fr = fragments()
    if not fr:
        return ""
    return f"<!-- 🏁 1/3 · rot13 · {codecs.encode(fr[0], 'rot13')} · next: soc.svg -->"


def invisible() -> str:
    fr = fragments()
    if not fr:
        return ""
    return (f'<text x="830" y="12" font-size="2" fill-opacity="0" aria-hidden="true">'
            f"2/3 · xor(key = the platform that runs my house, 2 letters) · {xor_hex(fr[1])} · next: boot.svg</text>")


def desc() -> str:
    fr = fragments()
    if not fr:
        return ""
    b64 = base64.b64encode(f"3/3 · {fr[2]}".encode()).decode()
    return f"<desc>maintenance token: {b64}</desc>"
