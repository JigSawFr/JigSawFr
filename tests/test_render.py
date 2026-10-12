import datetime as dt
import tomllib
import unittest
import xml.dom.minidom
from pathlib import Path

from generator import data as data_mod
from generator import environment, seasons, svg
from generator.main import PANELS, ROOT, featured_table

CFG = tomllib.loads((ROOT / "generator" / "config.toml").read_text(encoding="utf-8"))


class RenderTest(unittest.TestCase):
    def setUp(self):
        svg.use_theme(seasons.theme("cyber"))
        self.data = data_mod.sample(CFG["login"], today=dt.date(2026, 10, 12))
        self.st = data_mod.stats(self.data)
        self.st["env"] = environment.load(offline=True, phase="night", weather="rain")

    def test_panels_are_valid_static_svg(self):
        for name, mod in PANELS.items():
            svg = mod.render(CFG, self.data, self.st)
            with self.subTest(panel=name):
                xml.dom.minidom.parseString(svg.encode())  # well-formed
                self.assertNotIn("<script", svg)  # GitHub strips/blocks JS anyway
                self.assertNotIn("foreignObject", svg)
                self.assertLess(len(svg), 1_000_000)

    def test_every_season_renders(self):
        for key in seasons.THEMES:
            svg.use_theme(seasons.theme(key))
            for name, mod in PANELS.items():
                with self.subTest(season=key, panel=name):
                    xml.dom.minidom.parseString(mod.render(CFG, self.data, self.st).encode())

    def test_every_phase_and_weather_renders(self):
        self.st["intrusions"] = [{"repo": "x", "number": 1, "created_at": "2026-10-12"}]
        for phase in environment.PHASES:
            for weather in environment.WEATHERS + (None,):
                self.st["env"] = {**self.st["env"], "phase": phase, "weather": weather}
                with self.subTest(phase=phase, weather=weather):
                    xml.dom.minidom.parseString(PANELS["house"].render(CFG, self.data, self.st).encode())

    def test_weather_codes(self):
        self.assertEqual(environment.weather_kind(0), "clear")
        self.assertEqual(environment.weather_kind(61), "rain")
        self.assertEqual(environment.weather_kind(73), "snow")
        self.assertEqual(environment.weather_kind(95), "storm")
        self.assertEqual(environment.weather_kind(45), "fog")

    def test_intrusions_ignore_me_and_bots(self):
        today = dt.date(2026, 10, 12)
        data = {"login": "Me", "repos": [{"name": "r", "issues": [
            {"number": 1, "created_at": "2026-10-11T00:00:00Z", "author": "me"},
            {"number": 2, "created_at": "2026-10-11T00:00:00Z", "author": "dependabot[bot]"},
            {"number": 3, "created_at": "2026-09-01T00:00:00Z", "author": "stranger"},
            {"number": 4, "created_at": "2026-10-10T00:00:00Z", "author": "stranger"}]}]}
        self.assertEqual([h["number"] for h in data_mod.intrusions(data, today)], [4])

    def test_season_calendar(self):
        cases = {
            (2026, 10, 31): "halloween", (2026, 12, 24): "noel", (2026, 12, 31): "nouvel_an",
            (2027, 1, 1): "nouvel_an", (2027, 2, 10): "hiver", (2027, 4, 1): "printemps",
            (2027, 7, 14): "quatorze_juillet", (2027, 8, 1): "ete", (2027, 9, 30): "automne",
            (2027, 11, 15): "automne",
        }
        for (y, m, d), key in cases.items():
            with self.subTest(date=(y, m, d)):
                self.assertEqual(seasons.season_key(dt.date(y, m, d)), key)

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
