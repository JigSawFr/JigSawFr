"""Isometric projection + primitives shared by the house scene and its props."""

from __future__ import annotations

from ..svg import shade

S = 12                      # iso unit (px)
CX, CY = 0.866 * S, 0.5 * S
OX, OY = 181, 112           # screen position of world origin


def P(x, y, z=0.0):
    """World (x right-down, y left-down, z up) → screen."""
    return OX + (x - y) * CX, OY + (x + y) * CY - z * S


def pts(points) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def poly(points, fill, extra="") -> str:
    return f'<polygon points="{pts(points)}" fill="{fill}" {extra}/>'


def line(a, b, color, width=1.0, extra="") -> str:
    return (f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" {extra}/>')


def box(x, y, z, dx, dy, dz, color, extra="", top_extra="") -> str:
    """Iso box; visible faces: top, +y (lower-left), +x (lower-right)."""
    top = [P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
    left = [P(x, y + dy, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
    right = [P(x + dx, y, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x + dx, y, z + dz)]
    return (poly(left, shade(color, 0.7), extra) + poly(right, shade(color, 0.48), extra)
            + poly(top, color, extra + " " + top_extra))


def quad_y(x0, x1, y, z0, z1, fill, extra="") -> str:
    """Rectangle lying on a y = const wall (the front faces)."""
    return poly([P(x0, y, z0), P(x1, y, z0), P(x1, y, z1), P(x0, y, z1)], fill, extra)


def quad_x(x, y0, y1, z0, z1, fill, extra="") -> str:
    """Rectangle lying on an x = const wall (the side faces)."""
    return poly([P(x, y0, z0), P(x, y1, z0), P(x, y1, z1), P(x, y0, z1)], fill, extra)


def glow(cx, cy, r, color, opacity=1.0, cls="") -> str:
    """Soft light halo (radial gradient defined once per colour by the caller via halo_defs)."""
    c = f' class="{cls}"' if cls else ""
    return (f'<circle{c} cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="url(#halo{color[1:]})" '
            f'opacity="{opacity:.2f}"/>')


def halo_defs(colors) -> str:
    return "<defs>" + "".join(
        f'<radialGradient id="halo{c[1:]}"><stop offset="0" stop-color="{c}" stop-opacity=".9"/>'
        f'<stop offset=".35" stop-color="{c}" stop-opacity=".35"/><stop offset="1" stop-color="{c}" stop-opacity="0"/>'
        f"</radialGradient>" for c in sorted(set(colors))) + "</defs>"
