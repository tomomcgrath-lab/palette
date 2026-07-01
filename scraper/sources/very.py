"""Very.ie scraper — extracts from window.__product_listing_initial_state__."""
import re, json, logging
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product
from scraper.categories import guess_category, is_clothing

logger = logging.getLogger("palette")

class VeryScraper(BaseScraper):
    SEARCH_URL = "https://www.very.ie/e/q/{query}.end"

    def _extract_products(self, html: str) -> list[dict]:
        """Extract products via the initial state JSON (bracket-counted)."""
        key = "__product_listing_initial_state__"
        idx = html.find(key)
        if idx < 0:
            return []
        eq = html.find("=", idx)
        start = html.find("{", eq)
        if start < 0:
            return []
        depth = 0; end = start; in_str = False; escape = False
        for i in range(start, len(html)):
            c = html[i]
            if escape: escape = False; continue
            if c == "\\": escape = True; continue
            if c == '"': in_str = not in_str
            elif not in_str:
                if c == "{": depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0: end = i + 1; break
        raw = html[start:end]
        # Clean JS-isms that break JSON parsing
        raw = re.sub(r':\s*undefined', ': null', raw)
        raw = re.sub(r':\s*NaN', ': null', raw)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.debug(f"[very] JSON parse failed: {e}")
            return []

        # Navigate to products
        try:
            return data["queryState"]["queries"][0]["state"]["data"]["products"]
        except (KeyError, IndexError, TypeError):
            # Fallback: dig for it
            def dig(d, depth=0):
                if depth > 15: return []
                if isinstance(d, list) and d and isinstance(d[0], dict):
                    if "product_id" in d[0]:
                        return d
                if isinstance(d, dict):
                    for v in d.values():
                        if isinstance(v, (dict, list)):
                            r = dig(v, depth+1)
                            if r: return r
                return []
            return dig(data)

    def _parse(self, item: dict) -> Product | None:
        try:
            pid = str(item.get("product_id", ""))
            name = item.get("title", "")
            if not pid or not name:
                return None
            if not is_clothing(name):
                return None

            # Skip sold-out items if flagged
            roundel = str(item.get("roundelId", "")).lower()
            if roundel in ("soldout", "sold-out", "outofstock", "out-of-stock"):
                return None

            # Price
            price_d = item.get("price", {})
            price = float(price_d.get("current", 0) or 0)
            previous = float(price_d.get("previous", 0) or 0)
            sale_price = None
            if previous and previous > price:
                sale_price = price
                price = previous
            currency = price_d.get("currencyCode", "EUR")

            # URL
            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://www.very.ie{url}"

            # Image
            image = item.get("image_url", "")
            if not image:
                img_obj = item.get("image", {})
                if isinstance(img_obj, dict):
                    image = img_obj.get("url", "")

            # Colour — from options.COLOUR (the real fix)
            colour_orig = ""
            options = item.get("options", {})
            if isinstance(options, dict):
                colour_orig = options.get("COLOUR", "")
            # Also try swatchSources displayName as backup
            if not colour_orig:
                swatches = item.get("swatchSources", [])
                if swatches and isinstance(swatches, list):
                    colour_orig = swatches[0].get("displayName", "")

            # Match to palette colour
            matched = self.colour_matches(colour_orig)
            if not matched:
                # Try matching against the product title
                matched = self.colour_matches(name)
            if not matched:
                return None  # can't confidently assign a palette colour — skip

            brand = item.get("brand", "")

            return Product(
                id=f"very-{pid}", name=name, price=price, currency=currency,
                colour=matched, colour_original=colour_orig,
                source="very", url=url, image_url=image,
                category=guess_category(name), brand=brand, sale_price=sale_price)
        except Exception as e:
            logger.debug(f"[very] parse error: {e}")
            return None

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            for term in colour["search_terms"][:2]:
                if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
                try:
                    q = f"women-{term}".replace(" ", "-").lower()
                    url = self.SEARCH_URL.format(query=q)
                    resp = self._throttled_get(url)
                    if resp.status_code != 200: continue
                    items = self._extract_products(resp.text)
                    logger.debug(f"[very] '{term}': {len(items)} items")
                    for item in items:
                        pid = str(item.get("product_id", ""))
                        if pid in seen: continue
                        p = self._parse(item)
                        if p:
                            seen.add(pid)
                            products.append(p)
                except Exception as e:
                    logger.warning(f"[very] '{term}': {e}")
        return products
