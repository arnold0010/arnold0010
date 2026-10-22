
from pathlib import Path
from datetime import date, timedelta
import json
import html

DATA_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("contrib-heatmap.svg")

CELL = 11
GAP = 3
LEFT = 42
TOP = 42
BOTTOM = 28

BG = "#0D1117"
TEXT = "#C9D1D9"
MUTED = "#8B949E"

LEVEL_COLORS = [
    "#161B22",
    "#0E4429",
    "#006D32",
    "#26A641",
    "#39D353",
]


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing data file: {DATA_FILE}")

    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    by_date = {}

    for item in records:
        try:
            day = date.fromisoformat(item["date"])
        except (ValueError, KeyError, TypeError):
            continue

        level = item.get("level", 0)
        try:
            level = max(0, min(4, int(level)))
        except (ValueError, TypeError):
            level = 0

        by_date[day] = level

    if not by_date:
        raise RuntimeError("No valid dates found in contributions.json")

    first = min(by_date)
    last = max(by_date)

    # Align the grid to Sunday so every column represents one week.
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    end = last + timedelta(days=(5 - last.weekday()) % 7)

    weeks = ((end - start).days // 7) + 1
    width = LEFT + weeks * (CELL + GAP) + 12
    height = TOP + 7 * (CELL + GAP) + BOTTOM

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" rx="8" fill="{BG}"/>',
        f'<text x="{LEFT}" y="22" font-family="Arial, sans-serif" '
        f'font-size="14" font-weight="bold" fill="{TEXT}">'
        f'GitHub Contributions</text>',
    ]

    # Weekday labels on the left.
    weekday_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for row, label in weekday_labels:
        y = TOP + row * (CELL + GAP) + CELL - 1
        svg.append(
            f'<text x="7" y="{y}" font-family="Arial, sans-serif" '
            f'font-size="10" fill="{MUTED}">{label}</text>'
        )

    # Month labels.
    shown_months = set()
    current = start
    while current <= end:
        if current.day == 1 or current == start:
            week = (current - start).days // 7
            month_key = (current.year, current.month)
            if month_key not in shown_months:
                x = LEFT + week * (CELL + GAP)
                label = current.strftime("%b")
                svg.append(
                    f'<text x="{x}" y="36" font-family="Arial, sans-serif" '
                    f'font-size="10" fill="{MUTED}">{html.escape(label)}</text>'
                )
                shown_months.add(month_key)
        current += timedelta(days=1)

    # Contribution cells.
    current = start
    while current <= end:
        week = (current - start).days // 7
        row = (current.weekday() + 1) % 7
        x = LEFT + week * (CELL + GAP)
        y = TOP + row * (CELL + GAP)

        if current in by_date:
            level = by_date[current]
            title = f"{level} intensity level on {current.isoformat()}"
            color = LEVEL_COLORS[level]
        else:
            title = f"No calendar data for {current.isoformat()}"
            color = BG

        svg.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}">'
            f'<title>{html.escape(title)}</title></rect>'
        )
        current += timedelta(days=1)

    # Legend.
    legend_y = height - 16
    legend_x = width - 155

    svg.append(
        f'<text x="{legend_x - 36}" y="{legend_y + 9}" '
        f'font-family="Arial, sans-serif" font-size="10" fill="{MUTED}">'
        f'Less</text>'
    )

    for level, color in enumerate(LEVEL_COLORS):
        x = legend_x + level * (CELL + 4)
        svg.append(
            f'<rect x="{x}" y="{legend_y}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}"/>'
        )

    svg.append(
        f'<text x="{legend_x + 5 * (CELL + 4) + 2}" y="{legend_y + 9}" '
        f'font-family="Arial, sans-serif" font-size="10" fill="{MUTED}">'
        f'More</text>'
    )

    svg.append("</svg>")

    OUTPUT_FILE.write_text("\n".join(svg), encoding="utf-8")
    print(f"Heatmap saved to: {OUTPUT_FILE.resolve()}")
    print(f"Dates represented: {len(by_date)}")
    print(f"SVG size: {width} x {height}")


if __name__ == "__main__":
    main()
