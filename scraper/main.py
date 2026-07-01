"""
Palette — Main Scraper Runner

Run this daily to scrape all enabled sources and produce
a products.json file for the frontend.

Usage:
    python -m scraper.main                     # scrape all sources
    python -m scraper.main --source asos       # scrape only ASOS
    python -m scraper.main --dry-run           # parse & print, don't save
    python -m scraper.main --output data/      # custom output directory
"""

import os
import json
import logging
import argparse
from datetime import datetime, timezone

from scraper.config import SOURCES, OUTPUT_DIR, OUTPUT_FILE
from scraper.sources import SCRAPERS

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("palette")


def run_scraper(source_filter: str = None, output_dir: str = None, dry_run: bool = False):
    """Run all enabled scrapers and save results."""
    output_dir = output_dir or OUTPUT_DIR
    all_products = []
    scrape_time = datetime.now(timezone.utc).isoformat()

    # Determine which sources to scrape
    sources_to_run = {}
    for key, config in SOURCES.items():
        if not config.get("enabled", True):
            logger.info(f"[{key}] Skipping (disabled)")
            continue
        if source_filter and key != source_filter:
            continue
        if key not in SCRAPERS:
            logger.warning(f"[{key}] No scraper registered — skipping")
            continue
        sources_to_run[key] = config

    if not sources_to_run:
        logger.error("No sources to scrape. Check config or --source flag.")
        return

    # Run each scraper
    for key, config in sources_to_run.items():
        scraper_class = SCRAPERS[key]
        scraper = scraper_class(source_key=key, source_config=config)
        products = scraper.run()
        all_products.extend(products)
        logger.info(f"[{key}] → {len(products)} products")

    logger.info(f"Total: {len(all_products)} products from {len(sources_to_run)} sources")

    if dry_run:
        for p in all_products[:10]:
            print(f"  {p.source} | {p.colour:18s} | {p.currency}{p.price:>7.2f} | {p.name}")
        if len(all_products) > 10:
            print(f"  ... and {len(all_products) - 10} more")
        return

    # Build output
    output = {
        "scraped_at": scrape_time,
        "sources": list(sources_to_run.keys()),
        "total": len(all_products),
        "products": [p.to_dict() for p in all_products],
    }

    # Write JSON
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved to {output_path}")

    # Also keep a dated archive copy
    date_str = datetime.now().strftime("%Y-%m-%d")
    archive_path = os.path.join(output_dir, "archive", f"products-{date_str}.json")
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Archived to {archive_path}")


def main():
    parser = argparse.ArgumentParser(description="Palette — daily fashion scraper")
    parser.add_argument("--source", type=str, help="Scrape only this source (e.g. 'asos')")
    parser.add_argument("--output", type=str, help="Output directory (default: data/)")
    parser.add_argument("--dry-run", action="store_true", help="Print results without saving")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("palette").setLevel(logging.DEBUG)

    run_scraper(
        source_filter=args.source,
        output_dir=args.output,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
