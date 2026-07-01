"""John Lewis scraper — extracts from __NEXT_DATA__ productListingData."""
import re, json, logging
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product
from scraper.categories import guess_category

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

            # Price from variantPriceRange.value.min
            price = 0.0
            sale_price = None
            pr = item.get("variantPriceRange", {})
            if isinstance(pr, dict):
                val = pr.get("value", {})
                if isinstance(val, dict):
                    price = float(str(val.get("min", 0)).replace(",", "") or 0)
                # Check reduction history for original price
                rh = pr.get("reductionHistory", [])
                if rh and isinstance(rh, list):
                    was_disp = rh[0].get("display", {}).get("max", "")
                    was = float(re.sub(r'[^\d.]', '', was_disp) or 0)
                    if was > price:
                        sale_price = price
                        price = was

            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://www.johnlewis.com{url}"

            image = item.get("image", "")
            if image and image.startswith("//"):
                image = f"https:{image}"

            brand = item.get("brand", "")

            colour_orig = ""
            swatches = item.get("colorSwatches", [])
            if swatches and isinstance(swatches, list) and isinstance(swatches[0], dict):
                colour_orig = swatches[0].get("color", "")

            return Product(
                id=f"jl-{pid}", name=name, price=price, currency="GBP",
                colour=colour_name, colour_original=colour_orig,
                source="johnlewis", url=url, image_url=image,
                category=guess_category(name), brand=brand, sale_price=sale_price)
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
