"""John Lewis scraper — extracts from __NEXT_DATA__ productListingData."""
import re, json, logging
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product

logger = logging.getLogger("palette")

class JohnLewisScraper(BaseScraper):
    SEARCH_URL = "https://www.johnlewis.com/search"

    def _extract_products(self, html: str) -> list[dict]:
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not m: return []
        try:
            data = json.loads(m.group(1))
            return data["props"]["pageProps"]["productListingData"]["products"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []

    def _parse(self, item: dict, colour_name: str) -> Product | None:
        try:
            pid = str(item.get("productId", ""))
            name = item.get("title", "")
            if not pid or not name: return None

            # Price from variantPriceRange
            price_range = item.get("variantPriceRange", {})
            if isinstance(price_range, dict):
                lowest = price_range.get("lowest", {})
                if isinstance(lowest, dict):
                    now = lowest.get("now", lowest.get("price", 0))
                    was = lowest.get("was", 0)
                else:
                    now = float(lowest) if lowest else 0
                    was = 0
            else:
                now = 0
                was = 0

            price = float(str(now).replace("£", "").replace(",", "").strip() or 0)
            sale_price = None
            if was:
                was_f = float(str(was).replace("£", "").replace(",", "").strip() or 0)
                if was_f > price:
                    sale_price = price
                    price = was_f

            # URL
            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://www.johnlewis.com{url}"

            # Image
            image = item.get("image", "")
            if image and image.startswith("//"):
                image = f"https:{image}"

            # Brand
            brand = item.get("brand", "")

            # Color from colorSwatches
            colour_orig = ""
            swatches = item.get("colorSwatches", [])
            if swatches and isinstance(swatches, list):
                colour_orig = swatches[0].get("color", "") if isinstance(swatches[0], dict) else ""

            return Product(
                id=f"jl-{pid}", name=name, price=price, currency="GBP",
                colour=colour_name, colour_original=colour_orig,
                source="johnlewis", url=url, image_url=image,
                category="Clothing", brand=brand, sale_price=sale_price)
        except Exception as e:
            logger.debug(f"[jl] parse error: {e}")
            return None

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            for term in colour["search_terms"][:1]:
                if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
                try:
                    resp = self._throttled_get(self.SEARCH_URL,
                        params={"search-term": f"women {term}"})
                    if resp.status_code != 200: continue
                    items = self._extract_products(resp.text)
                    logger.debug(f"[jl] '{term}': {len(items)} items")
                    for item in items:
                        pid = str(item.get("productId", ""))
                        if pid in seen: continue
                        col_orig = ""
                        swatches = item.get("colorSwatches", [])
                        if swatches:
                            col_orig = swatches[0].get("color", "")
                        col = self.colour_matches(col_orig) or colour["name"]
                        p = self._parse(item, col)
                        if p: seen.add(pid); products.append(p)
                except Exception as e:
                    logger.warning(f"[jl] '{term}': {e}")
        return products
