#!/usr/bin/env python3
"""Download Roboto fonts needed by the image composer.

Run once: python scripts/download_fonts.py
"""

import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).parent.parent / "templates" / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

FONTS = {
    "Roboto-Regular.ttf": (
        "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
    ),
    "Roboto-Bold.ttf": (
        "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
    ),
}


def main():
    for filename, url in FONTS.items():
        dest = FONTS_DIR / filename
        if dest.exists():
            print(f"  already exists: {dest}")
            continue
        print(f"  downloading {filename}...")
        urllib.request.urlretrieve(url, dest)
        print(f"  saved to {dest}")
    print("Done.")


if __name__ == "__main__":
    main()
