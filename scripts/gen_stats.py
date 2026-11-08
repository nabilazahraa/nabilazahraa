import json
import os
import urllib.request

USER = os.environ.get("GH_USER", "nabilazahraa")
TOKEN = os.environ.get("GH_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes { stargazerCount }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        user = json.load(r)["data"]["user"]
    c = user["contributionsCollection"]
    stars = sum(n["stargazerCount"] for n in user["repositories"]["nodes"])
    return [
        (f'{c["contributionCalendar"]["totalContributions"]:,}', "contributions, last year"),
        (f'{c["totalCommitContributions"] + c["restrictedContributionsCount"]:,}', "commits"),
        (f'{c["totalPullRequestContributions"]:,}', "pull requests"),
        (f"{stars:,}", "stars earned"),
    ]


THEMES = {
    "light": dict(bg0="#FFF6FB", bg1="#FFDDEE", num="#E02A80", label="#8A3F6E", line="#EE5A9F", border="rgba(224,42,128,0.32)"),
    "dark": dict(bg0="#0B0614", bg1="#1A0B2E", num="#FF4FA3", label="#D9A9CB", line="#FF8DC7", border="rgba(255,141,199,0.30)"),
}


def render(stats, t):
    w, h = 830, 132
    col = w / len(stats)
    parts = []
    for i, (value, label) in enumerate(stats):
        cx = col * i + col / 2
        parts.append(f'<text x="{cx}" y="70" text-anchor="middle" font-size="42" font-weight="800" fill="{t["num"]}">{value}</text>')
        parts.append(f'<text x="{cx}" y="98" text-anchor="middle" font-size="13" letter-spacing=".6" fill="{t["label"]}">{label}</text>')
        if i:
            parts.append(f'<rect x="{col * i}" y="26" width="1" height="80" fill="{t["line"]}" opacity=".4"/>')
    desc = ", ".join(f"{v} {l}" for v, l in stats)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">'
        f'<title id="t">GitHub stats: {desc}</title>'
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>'
        '<style>text{font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}</style></defs>'
        f'<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>'
        + "".join(parts)
        + f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{t["border"]}"/></svg>'
    )


def main():
    if TOKEN:
        stats = fetch()
    else:
        stats = [("-", "contributions, last year"), ("-", "commits"), ("-", "pull requests"), ("-", "stars earned")]
    for name, theme in THEMES.items():
        with open(os.path.join(OUT, f"stats-card-{name}.svg"), "w", encoding="utf-8") as f:
            f.write(render(stats, theme))


if __name__ == "__main__":
    main()
