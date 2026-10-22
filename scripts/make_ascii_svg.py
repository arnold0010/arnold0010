from pathlib import Path
import html

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

# Fewer blanks at the bright end, so skin tones still print something.
RAMP = " .,:-=+*#%@@"
COLS = 180

FONT_SIZE = 10
CELL_WIDTH = 6.0
CELL_HEIGHT = 11.5

TEXT_COLOR = "#111111"   # near black (was #444444)
BACKGROUND = "#ffffff"

GAMMA = 1.35             # above 1 = darker, below 1 = lighter

MARGIN_X = 30
MARGIN_Y = 24

NBSP = "&#160;"  # non-breaking space: browsers never collapse it


def load_gray(path):
    """Load the image as grayscale, flattening any transparency onto white."""
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        rgba = image.convert("RGBA")
        canvas = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        canvas.alpha_composite(rgba)
        return canvas.convert("L")


def make_ascii_svg(
    input_path="source-prepped.png",
    output_path="avi-ascii.svg",
):
    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"Source image not found: {source.resolve()}")

    image = load_gray(source)
    image = ImageOps.autocontrast(image, cutoff=0.3)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    gray = np.asarray(image).copy()

    original_height, original_width = gray.shape

    rows = max(
        1,
        round((original_height / original_width) * COLS * CELL_WIDTH / CELL_HEIGHT),
    )

    small = cv2.resize(gray, (COLS, rows), interpolation=cv2.INTER_AREA)

    brightness = small.astype(np.float32) / 255.0
    brightness = np.clip((brightness - 0.02) / 0.96, 0.0, 1.0)
    brightness = brightness ** GAMMA

    indices = np.rint((1.0 - brightness) * (len(RAMP) - 1)).astype(int)
    indices = np.clip(indices, 0, len(RAMP) - 1)

    lines = ["".join(RAMP[i] for i in row) for row in indices]

    portrait_width = COLS * CELL_WIDTH
    portrait_height = rows * CELL_HEIGHT
    width = portrait_width + 2 * MARGIN_X
    height = portrait_height + 2 * MARGIN_Y

    svg = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width:.1f}" height="{height:.1f}" '
            f'viewBox="0 0 {width:.1f} {height:.1f}" '
            'preserveAspectRatio="xMidYMin meet">'
        ),
        f'<rect width="{width:.1f}" height="{height:.1f}" fill="{BACKGROUND}"/>',
        (
            f'<g transform="translate({MARGIN_X},{MARGIN_Y})" '
            "font-family=\"Consolas, 'Courier New', monospace\" "
            f'font-size="{FONT_SIZE}" font-weight="bold" fill="{TEXT_COLOR}" '
            'style="white-space:pre" xml:space="preserve">'
        ),
    ]

    for y, line in enumerate(lines):
        if not line.strip():
            continue  # blank row, nothing to draw
        text = html.escape(line).replace(" ", NBSP)
        svg.append(
            f'<text x="0" y="{y * CELL_HEIGHT + FONT_SIZE:.1f}" '
            f'textLength="{portrait_width:.1f}" lengthAdjust="spacing">'
            f"{text}</text>"
        )

    svg.extend(["</g>", "</svg>"])

    Path(output_path).write_text("\n".join(svg), encoding="utf-8")

    print(f"ASCII SVG saved to: {Path(output_path).resolve()}")
    print(f"Character grid: {COLS} columns x {rows} rows")
    print(f"SVG dimensions: {width:.0f} x {height:.0f}")


if __name__ == "__main__":
    make_ascii_svg()