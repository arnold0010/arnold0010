
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str) -> None:
    source = Path(input_path)

    if not source.is_file():
        raise FileNotFoundError(f"Photo not found: {source}")

    output_path = source.with_name("source-prepped.png")

    # Load the original photo and remove its background.
    with Image.open(source) as image:
        rgba = remove(image.convert("RGBA"))
        rgba_array = np.array(rgba)

    # Composite the subject onto a pure-white background.
    rgb = rgba_array[:, :, :3].astype(np.float32)
    alpha = rgba_array[:, :, 3:4].astype(np.float32) / 255.0
    white = np.full_like(rgb, 255.0)
    composite = (rgb * alpha + white * (1.0 - alpha)).astype(np.uint8)

    # Convert to grayscale and enhance local contrast with CLAHE.
    gray = cv2.cvtColor(composite, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Save the prepared image beside the original photo.
    cv2.imwrite(str(output_path), enhanced)
    print(f"Prepared image saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py <photo-path>")
        raise SystemExit(1)

    prep_photo(sys.argv[1])
