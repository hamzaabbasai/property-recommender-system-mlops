from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlopen

SNAPSHOT_DATE = "2026-06-26"
BASE_URL = f"https://data.insideairbnb.com/germany/be/berlin/{SNAPSHOT_DATE}"
FILES = {
    "listings.csv.gz": f"{BASE_URL}/data/listings.csv.gz",
    "reviews.csv.gz": f"{BASE_URL}/data/reviews.csv.gz",
    "neighbourhoods.geojson": f"{BASE_URL}/visualisations/neighbourhoods.geojson",
}
CALENDAR_URL = f"{BASE_URL}/data/calendar.csv.gz"


def download_file(url: str, output: Path, force: bool = False) -> None:
    if output.exists() and not force:
        print(f"Using existing file: {output}")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(f"{output.suffix}.part")
    with urlopen(url, timeout=60) as response, temporary.open("wb") as file:
        while chunk := response.read(1024 * 1024):
            file.write(chunk)
    temporary.replace(output)
    print(f"Downloaded: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the Inside Airbnb Berlin data.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--with-calendar", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    files = dict(FILES)
    if args.with_calendar:
        files["calendar.csv.gz"] = CALENDAR_URL

    for name, url in files.items():
        download_file(url, args.output_dir / name, force=args.force)

    print("Source: Inside Airbnb, Berlin snapshot 2026-06-26, CC BY 4.0")


if __name__ == "__main__":
    main()
