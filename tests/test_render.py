import datetime as dt
import tomllib
import unittest
import xml.dom.minidom
from pathlib import Path

from generator import data as data_mod
from generator.main import PANELS, ROOT, featured_table

CFG = tomllib.loads((ROOT / "generator" / "config.toml").read_text(encoding="utf-8"))


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.data = data_mod.sample(CFG["login"], today=dt.date(2026, 10, 12))
        self.st = data_mod.stats(self.data)

    def test_panels_are_valid_static_svg(self):
        for name, mod in PANELS.items():
            svg = mod.render(CFG, self.data, self.st)
            with self.subTest(panel=name):
                xml.dom.minidom.parseString(svg.encode())  # well-formed
                self.assertNotIn("<script", svg)  # GitHub strips/blocks JS anyway
                self.assertNotIn("foreignObject", svg)
                self.assertLess(len(svg), 1_000_000)

    def test_streaks(self):
        days = [{"date": f"2026-01-{d:02d}", "count": c} for d, c in enumerate([1, 1, 0, 2, 3, 1, 0], 1)]
        st = data_mod.stats({"days": days, "repos": []}, today=dt.date(2026, 1, 7))
        self.assertEqual(st["current_streak"], 3)  # today empty doesn't break the streak
        self.assertEqual(st["longest_streak"], 3)

    def test_featured_skips_unknown_repos(self):
        table = featured_table({"featured": [{"repo": "nope-private", "icon": "x"}]}, self.data)
        self.assertNotIn("nope-private", table)

    def test_escaping(self):
        self.data["repos"][0]["name"] = "<evil&repo>"
        svg = PANELS["soc"].render(CFG, self.data, self.st)
        xml.dom.minidom.parseString(svg.encode())


if __name__ == "__main__":
    unittest.main()
