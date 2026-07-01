"""
Palette — Base Scraper
Abstract base class for all retailer scrapers.

Uses curl_cffi instead of requests to bypass bot detection.
curl_cffi impersonates real browser TLS fingerprints (Chrome),
which gets past Akamai and similar anti-bot systems.
"""

import time
import logging
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional

from curl_cffi import requests

from scraper.config import SIZE_CONFIG, match_colour

logger = logging.getLogger("palette")


@dataclass
class Product:
    """A single product result."""
    id: str
    name: str
    price: float
    currency: str
    colour: str
    colour_original: str
    source: str
    url: str
    image_url: str
    category: str
    brand: str = ""
    sale_price: Optional[float] = None

    def to_dict(self):
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


class BaseScraper(ABC):
    """
    Base class for retailer scrapers.
    Uses curl_cffi to impersonate Chrome and bypass bot detection.
    """

    # Polite delay between requests (seconds)
    REQUEST_DELAY = 3.0  # slightly longer to be polite and avoid bans

    def __init__(self, source_key: str, source_config: dict):
        self.source_key = source_key
        self.config = source_config
        # curl_cffi session with Chrome impersonation
        self.session = requests.Session(impersonate="chrome")
        self._last_request_time = 0

    def _throttled_get(self, url: str, params: dict = None, **kwargs) -> requests.Response:
        """Make a GET request with polite rate limiting and Chrome impersonation."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)

        logger.debug(f"[{self.source_key}] GET {url}")
        try:
            resp = self.session.get(url, params=params, timeout=30, **kwargs)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"[{self.source_key}] Request failed: {e}")
            raise
        finally:
            self._last_request_time = time.time()

        return resp

    def _extract_json_from_html(self, html: str, pattern: str) -> dict | None:
        """Extract JSON data embedded in HTML using a regex pattern."""
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def size_matches(self, size_text: str) -> bool:
        """Check if a size string matches UK Medium."""
        size_text = str(size_text).strip().upper()
        schema = self.config.get("size_schema", "uk")
        acceptable = SIZE_CONFIG["mappings"].get(schema, [])
        return size_text in [s.upper() for s in acceptable]

    def colour_matches(self, colour_text: str) -> Optional[str]:
        """Check if a colour string matches any palette colour."""
        return match_colour(colour_text)

    @abstractmethod
    def search_products(self) -> list[Product]:
        """Search the retailer and return matching products."""
        ...

    def run(self) -> list[Product]:
        """Run the scraper with error handling."""
        logger.info(f"[{self.source_key}] Starting scrape...")
        try:
            products = self.search_products()
            seen = set()
            unique = []
            for p in products:
                if p.id not in seen:
                    seen.add(p.id)
                    unique.append(p)
            logger.info(f"[{self.source_key}] Found {len(unique)} matching products")
            return unique
        except Exception as e:
            logger.error(f"[{self.source_key}] Scrape failed: {e}", exc_info=True)
            return []
