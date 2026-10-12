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
    pullRequests(states: OPEN) { totalCount }
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
        releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { tagName publishedAt }
        }
        issues(states: OPEN, first: 3, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { number createdAt author { login } }
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
        if r["name"].lower() == user["login"].lower():  # the profile repo itself is noise
            continue
        repos.append({
            "name": r["name"],
            "description": r.get("description") or "",
            "url": r["url"],
            "stars": r["stargazerCount"],
            "archived": r["isArchived"],
            "pushed_at": r["pushedAt"],
            "language": (r.get("primaryLanguage") or {}).get("name"),
            "release": next(({"tag": n["tagName"], "published_at": n["publishedAt"]}
                             for n in r["releases"]["nodes"] if n.get("publishedAt")), None),
            "issues": [{"number": i["number"], "created_at": i["createdAt"],
                        "author": (i.get("author") or {}).get("login") or "ghost"}
                       for i in r["issues"]["nodes"]],
        })
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "login": user["login"],
        "name": user.get("name") or user["login"],
        "created_at": user["createdAt"],
        "followers": user["followers"]["totalCount"],
        "open_prs": user["pullRequests"]["totalCount"],
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
        {"name": "eurodns-mcp", "description": "Model Context Protocol server for the EuroDNS User API — domains, DNS zones, subscriptions and SSL.", "stars": 1, "language": "TypeScript", "pushed_at": pushed(25),
         "release": {"tag": "v1.4.0", "published_at": pushed(2)}},
        {"name": "lacale-prowlarr-indexer", "description": "La-Cale Prowlarr API Indexer", "stars": 140, "language": None, "pushed_at": pushed(60), "archived": True},
        {"name": "aiometadata-docker", "description": "🐳 Automated Docker images for AIOMetadata - The Ultimate Stremio Metadata Addon | Multi-arch (amd64/arm64) | Auto-sync with upstream | Cosign signed", "stars": 3, "language": "Dockerfile", "pushed_at": pushed(57)},
        {"name": "asustor-runtipi", "description": "📦 Runtipi package for ASUSTOR NAS - Self-hosted app management platform with 200+ one-click apps, automatic HTTPS, and beautiful web UI. Supports x86-64 & ARM64 architectures.", "stars": 6, "language": "Python", "pushed_at": pushed(110)},
        {"name": "comet-docker", "description": "", "stars": 0, "language": "Dockerfile", "pushed_at": pushed(260)},
        {"name": "docker-crowdsec-dashboard", "description": "Crowdsec dashboard.", "stars": 1, "language": None, "pushed_at": pushed(1400)},
    ]
    for r in repos:
        r.setdefault("archived", False)
        r.setdefault("release", None)
        r.setdefault("issues", [])
        r["url"] = f"https://github.com/{login}/{r['name']}"
    total = sum(x["count"] for x in days)
    return {
        "login": login, "name": login, "created_at": "2013-06-01T00:00:00Z", "followers": 42, "open_prs": 2,
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
        "release": recent_release(data, today),
        "intrusions": intrusions(data, today),
    }


def _age(ts: str, today: dt.date) -> int:
    return (today - dt.date.fromisoformat(ts[:10])).days


def recent_release(data: dict, today: dt.date, days: int = 7) -> dict | None:
    """Newest release published in the last week → the car is parked in the driveway."""
    found = [(r["release"]["published_at"], r["name"], r["release"]["tag"])
             for r in data["repos"] if r.get("release") and _age(r["release"]["published_at"], today) <= days]
    if not found:
        return None
    ts, repo, tag = max(found)
    return {"repo": repo, "tag": tag, "published_at": ts}


def intrusions(data: dict, today: dt.date, days: int = 7) -> list[dict]:
    """Open issues filed by someone else (not a bot) on my public repos during the last week."""
    me = data.get("login", "").lower()
    hits = [
        {"repo": r["name"], "number": i["number"], "created_at": i["created_at"]}
        for r in data["repos"] for i in r.get("issues", [])
        if i["author"].lower() != me and not i["author"].endswith("[bot]") and _age(i["created_at"], today) <= days
    ]
    return sorted(hits, key=lambda h: h["created_at"], reverse=True)
