
from pathlib import Path
import html
import os

OUTPUT = Path("info-card.svg")

WIDTH = 490
HEIGHT = 430

BG = "#111827"
BORDER = "#374151"
TEXT = "#E5E7EB"
MUTED = "#9CA3AF"
GREEN = "#86EFAC"
CYAN = "#67E8F9"

STATIC = os.getenv("STATIC", "0") == "1"


def add_text(x, y, content, size=14, color=TEXT, weight="normal"):
    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="Consolas, monospace" '
        f'font-size="{size}" fill="{color}" '
        f'font-weight="{weight}">{html.escape(content)}</text>'
    )


def animated_group(content, delay, index):
    if STATIC:
        return f'<g id="row-{index}">{content}</g>'

    return f"""
    <g id="row-{index}">
      <animateTransform
        attributeName="transform"
        type="translate"
        values="0 8; 0 0"
        keyTimes="0;1"
        dur="0.35s"
        begin="{delay:.2f}s"
        fill="freeze"
        calcMode="spline"
        keySplines="0.2 0.7 0.2 1"/>
      <animate
        attributeName="opacity"
        values="0;1"
        keyTimes="0;1"
        dur="0.35s"
        begin="{delay:.2f}s"
        fill="freeze"/>
      {content}
    </g>
    """


def make_card():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<rect x="1" y="1" width="{WIDTH-2}" '
        f'height="{HEIGHT-2}" rx="12" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="2"/>',
        '<circle cx="22" cy="22" r="5" fill="#F87171"/>',
        '<circle cx="40" cy="22" r="5" fill="#FBBF24"/>',
        '<circle cx="58" cy="22" r="5" fill="#86EFAC"/>',
        add_text(78, 27, "tushar@github ~", 13, MUTED),
        f'<line x1="16" y1="43" x2="{WIDTH-16}" y2="43" '
        f'stroke="{BORDER}"/>',
    ]

    rows = [
        (22, 75, "NOW", 14, GREEN, "bold"),
        (22, 101, "MBA Finance & Data Science / AI", 14, TEXT, "normal"),
        (22, 124, "Building skills in finance and analytics", 12, MUTED, "normal"),

        (22, 165, "PREV", 14, CYAN, "bold"),
        (22, 191, "B.Tech in Electrical Engineering", 14, TEXT, "normal"),
        (22, 214, "Marketing and finance internship experience", 11, MUTED, "normal"),

        (22, 255, "STACK", 14, GREEN, "bold"),
        (22, 281, "Excel  |  Python  |  SQL  |  Power BI", 13, TEXT, "normal"),

        (22, 322, "HIGHLIGHTS", 14, CYAN, "bold"),
        (22, 348, "Credit risk analysis and financial research", 12, TEXT, "normal"),
        (22, 370, "Business analytics and practical projects", 12, TEXT, "normal"),
    ]

    for index, (x, y, label, size, color, weight) in enumerate(rows):
        content = add_text(x, y, label, size, color, weight)
        delay = 0.15 + index * 0.13
        parts.append(animated_group(content, delay, index))

    parts.extend([
        f'<line x1="16" y1="390" x2="{WIDTH-16}" y2="390" '
        f'stroke="{BORDER}"/>',
        animated_group(
            add_text(22, 414, "STATUS: LEARNING • BUILDING • IMPROVING",
                     10, GREEN),
            1.65,
            "status",
        ),
        "</svg>",
    ])

    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Saved: {OUTPUT.resolve()}")
    print("Preview mode:", "STATIC" if STATIC else "ANIMATED")


if __name__ == "__main__":
    make_card()
