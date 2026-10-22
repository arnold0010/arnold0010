
from pathlib import Path
import json
import re
import requests
from bs4 import BeautifulSoup

USERNAME = "arnold0010"
OUTPUT = Path("data/contributions.json")
URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"https://github.com/{USERNAME}",
}


def main():
    print(f"Fetching contribution calendar for {USERNAME}...")

    response = requests.get(URL, headers=HEADERS, timeout=30)
    print("HTTP status:", response.status_code)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    days = []

    # GitHub exposes exact counts in tooltip elements linked by cell ID.
    tooltips = {}
    for tip in soup.find_all("tool-tip"):
        cell_id = tip.get("for")
        match = re.search(r"(\d+)\s+contributions?", tip.get_text(" ", strip=True))
        if cell_id and match:
            tooltips[cell_id] = int(match.group(1))

    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level", "0")

        if not date or not re.fullmatch(r"\d", level):
            continue

        cell_id = cell.get("id")
        count = tooltips.get(cell_id) if cell_id else None

        days.append({
            "date": date,
            "count": count,
            "level": max(0, min(4, int(level))),
        })

    if not days:
        Path("data").mkdir(parents=True, exist_ok=True)
        Path("data/github-response-debug.html").write_text(
            response.text, encoding="utf-8"
        )
        raise RuntimeError(
            "No contribution cells found. Saved the response to "
            "data/github-response-debug.html for inspection."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(days, indent=2), encoding="utf-8")

    print(f"Saved {len(days)} days to {OUTPUT.resolve()}")
    print("Exact counts available:", sum(d["count"] is not None for d in days))


if __name__ == "__main__":
    main()
