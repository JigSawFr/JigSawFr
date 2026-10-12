"""Seasonal themes, picked from the date (override: --season NAME or PROFILE_SEASON=NAME)."""

from __future__ import annotations

import datetime as dt

BASE = {
    "neon": ("#00e5ff", "#ff2fd0"),
    "heat": ["#111a28", "#0a4452", "#087c8f", "#00b8d4", "#7af6ff"],
    "window": "#ffd27a",
    "sky": "moon",          # moon | sun
    "particles": None,      # snow | leaves | petals | fireflies
    "fireworks": None,      # list of colours
    "deco": set(),          # see panels/house.py
    "smoke": "#8aa0b8",
    "foliage": None,        # tree colour, None = no tree
}

THEMES: dict[str, dict] = {
    "cyber": {"label": "CYBER", "icon": "⚡", "boot": "neon.target — default theme"},
    "nouvel_an": {
        "label": "NEW YEAR · BONNE ANNÉE", "icon": "🎆", "boot": "fireworks.service — happy new year / bonne année",
        "neon": ("#ffd166", "#ff2fd0"),
        "heat": ["#141228", "#3a2466", "#7a3fbf", "#ff2fd0", "#ffd166"],
        "window": "#ffd166",
        "fireworks": ["#ffd166", "#ff2fd0", "#00e5ff", "#39ff88"],
        "particles": "snow", "deco": {"snow_roof"},
    },
    "noel": {
        "label": "CHRISTMAS · NOËL", "icon": "🎄", "boot": "christmas.target — garland online / guirlande allumée",
        "neon": ("#ff4d6d", "#39ff88"),
        "heat": ["#111a28", "#0d4d2b", "#169147", "#ff4d6d", "#ffd166"],
        "window": "#ffcf6e",
        "particles": "snow", "deco": {"snow_roof", "garland", "xmas_tree", "gifts"}, "smoke": "#c9d6e5",
    },
    "halloween": {
        "label": "HALLOWEEN", "icon": "🎃", "boot": "halloween.target — spooky mode / mode frisson",
        "neon": ("#ff7b00", "#a64dff"),
        "heat": ["#17121f", "#3b1a5a", "#7b2cbf", "#ff7b00", "#ffc15e"],
        "window": "#ff9a1f",
        "deco": {"pumpkins", "bats", "ghost", "dead_tree"}, "smoke": "#a64dff",
    },
    "quatorze_juillet": {
        "label": "14 JUILLET", "icon": "🇫🇷", "boot": "bastille-day.service — feu d'artifice !",
        "neon": ("#3b82f6", "#ef4444"),
        "heat": ["#111a28", "#1e3a8a", "#3b82f6", "#e5e7eb", "#ef4444"],
        "fireworks": ["#3b82f6", "#f5f5f5", "#ef4444"],
        "deco": {"flag"}, "foliage": "#2e8b57",
    },
    "hiver": {
        "label": "WINTER · HIVER", "icon": "❄️", "boot": "heating.service — 21°C, thermostat engaged",
        "neon": ("#7fc8ff", "#c6a0ff"),
        "heat": ["#111a28", "#1b3a5c", "#2f6fa8", "#7fc8ff", "#e8f6ff"],
        "particles": "snow", "deco": {"snow_roof", "snowman", "pine"}, "smoke": "#c9d6e5",
    },
    "printemps": {
        "label": "SPRING · PRINTEMPS", "icon": "🌸", "boot": "garden.service — sprinklers scheduled",
        "neon": ("#7ed957", "#ff8fd8"),
        "heat": ["#111a28", "#16492f", "#2e8b57", "#7ed957", "#ffb3d9"],
        "particles": "petals", "deco": {"flowers"}, "foliage": "#ff8fd8",
    },
    "ete": {
        "label": "SUMMER · ÉTÉ", "icon": "☀️", "boot": "cooling.service — AC on, shutters closed",
        "neon": ("#ffb547", "#ff4d6d"),
        "heat": ["#111a28", "#5a3a0a", "#c77d0a", "#ffb547", "#fff07a"],
        "sky": "sun", "particles": "fireflies", "deco": {"flowers"}, "foliage": "#39b54a",
    },
    "automne": {
        "label": "AUTUMN · AUTOMNE", "icon": "🍂", "boot": "leaf-blower.timer — gutters need love",
        "neon": ("#e07b39", "#ff2fd0"),
        "heat": ["#111a28", "#4a2a12", "#a0522d", "#e07b39", "#ffc66b"],
        "particles": "leaves", "foliage": "#e07b39",
    },
}

# (key, (month, day) start, (month, day) end), first match wins; ranges may wrap the year.
CALENDAR = [
    ("nouvel_an", (12, 31), (1, 2)),
    ("noel", (12, 1), (12, 30)),
    ("halloween", (10, 10), (11, 2)),
    ("quatorze_juillet", (7, 13), (7, 15)),
    ("hiver", (12, 21), (3, 19)),
    ("printemps", (3, 20), (6, 20)),
    ("ete", (6, 21), (9, 22)),
    ("automne", (9, 23), (11, 30)),
]


def season_key(day: dt.date) -> str:
    md = (day.month, day.day)
    for key, start, end in CALENDAR:
        if (start <= md <= end) if start <= end else (md >= start or md <= end):
            return key
    return "cyber"


def theme(key: str) -> dict:
    if key not in THEMES:
        raise SystemExit(f"unknown season {key!r}; choose from {', '.join(THEMES)}")
    return {**BASE, **THEMES[key], "key": key}
