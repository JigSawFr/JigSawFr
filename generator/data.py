"""Fetch and normalise GitHub activity (GraphQL), or synthesise sample data offline."""

from __future__ import annotations

import datetime as dt
import json
import os
import random
import urllib.request
from collections import OrderedDict

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name
        description
        url
        stargazerCount
        isArchived
        pushedAt
        primaryLanguage { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "homelab-os-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return normalise(payload["data"]["user"])


def normalise(user: dict) -> dict:
    cc = user["contributionsCollection"]
    days = [
        {"date": d["date"], "count": d["contributionCount"]}
        for w in cc["contributionCalendar"]["weeks"]
        for d in w["contributionDays"]
    ]
    repos = []
    langs: dict[str, int] = {}
    for r in user["repositories"]["nodes"]:
        repos.append({
            "name": r["name"],
            "description": r.get("description") or "",
            "url": r["url"],
            "stars": r["stargazerCount"],
            "archived": r["isArchived"],
            "pushed_at": r["pushedAt"],
            "language": (r.get("primaryLanguage") or {}).get("name"),
        })
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "login": user["login"],
        "name": user.get("name") or user["login"],
        "created_at": user["createdAt"],
        "followers": user["followers"]["totalCount"],
        "days": sorted(days, key=lambda d: d["date"]),
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "repo_count": user["repositories"]["totalCount"],
        "repos": repos,
        "languages": sorted(langs.items(), key=lambda kv: -kv[1]),
    }


def sample(login: str, today: dt.date | None = None) -> dict:
    """Deterministic fake data, used for offline rendering and tests."""
    rng = random.Random(42)
    today = today or dt.date.today()
    start = today - dt.timedelta(days=364 + (today.weekday() + 1) % 7)
    days = []
    d = start
    while d <= today:
        burst = 1 + 2 * (d.month in (3, 9, 10))
        n = 0 if rng.random() < 0.35 else int(rng.expovariate(1 / (3 * burst)))
        days.append({"date": d.isoformat(), "count": n})
        d += dt.timedelta(days=1)
    for i in range(1, 9):  # a nice live streak
        days[-i]["count"] = max(days[-i]["count"], rng.randint(1, 9))
    pushed = lambda k: (today - dt.timedelta(days=k)).isoformat() + "T12:00:00Z"
    repos = [
        {"name": "playguard-ha", "description": "", "stars": 0, "language": "Python", "pushed_at": pushed(2)},
        {"name": "eurodns-mcp", "description": "Model Context Protocol server for the EuroDNS User API — domains, DNS zones, subscriptions and SSL.", "stars": 1, "language": "TypeScript", "pushed_at": pushed(25)},
        {"name": "lacale-prowlarr-indexer", "description": "La-Cale Prowlarr API Indexer", "stars": 140, "language": None, "pushed_at": pushed(60), "archived": True},
        {"name": "aiometadata-docker", "description": "🐳 Automated Docker images for AIOMetadata - The Ultimate Stremio Metadata Addon | Multi-arch (amd64/arm64) | Auto-sync with upstream | Cosign signed", "stars": 3, "language": "Dockerfile", "pushed_at": pushed(57)},
        {"name": "asustor-runtipi", "description": "📦 Runtipi package for ASUSTOR NAS - Self-hosted app management platform with 200+ one-click apps, automatic HTTPS, and beautiful web UI. Supports x86-64 & ARM64 architectures.", "stars": 6, "language": "Python", "pushed_at": pushed(110)},
        {"name": "comet-docker", "description": "", "stars": 0, "language": "Dockerfile", "pushed_at": pushed(260)},
        {"name": "docker-crowdsec-dashboard", "description": "Crowdsec dashboard.", "stars": 1, "language": None, "pushed_at": pushed(1400)},
    ]
    for r in repos:
        r.setdefault("archived", False)
        r["url"] = f"https://github.com/{login}/{r['name']}"
    total = sum(x["count"] for x in days)
    return {
        "login": login, "name": login, "created_at": "2013-06-01T00:00:00Z", "followers": 42,
        "days": days, "total": total, "commits": int(total * 0.8), "prs": 64, "issues": 21, "reviews": 9,
        "repo_count": 9, "repos": repos,
        "languages": [("TypeScript", 820_000), ("Python", 410_000), ("JavaScript", 150_000),
                      ("Dockerfile", 60_000), ("Shell", 30_000), ("PHP", 12_000)],
    }


def load(login: str, offline: bool = False) -> dict:
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if offline or not token:
        return sample(login)
    return fetch(login, token)


# ---------------------------------------------------------------- derived stats

def stats(data: dict, today: dt.date | None = None) -> dict:
    days = data["days"]
    counts = [d["count"] for d in days]
    today = today or dt.date.fromisoformat(days[-1]["date"])

    # current streak tolerates "nothing yet today"
    i = len(days) - 1
    if counts and counts[i] == 0 and days[i]["date"] == today.isoformat():
        i -= 1
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)

    best = max(days, key=lambda d: d["count"]) if days else {"date": today.isoformat(), "count": 0}
    months: "OrderedDict[str, list[dict]]" = OrderedDict()
    for d in days:
        months.setdefault(d["date"][:7], []).append(d)
    last12 = list(months.items())[-12:]
    return {
        "today": today,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "last7": sum(counts[-7:]),
        "last30": counts[-30:],
        "active_days": sum(1 for c in counts if c),
        "months": last12,
        "max_day": max(counts or [0]),
        "stars": sum(r["stars"] for r in data["repos"]),
    }
