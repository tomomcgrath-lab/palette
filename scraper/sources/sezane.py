"""Sézane scraper — products load via JS, so this uses their API if available."""
import re, json, logging
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product

logger = logging.getLogger("palette")

class SezaneScraper(BaseScraper):
    """
    Sézane loads products entirely via JavaScript. This scraper tries
    their internal API endpoints. If those fail, it falls back to
    parsing whatever HTML is available.

    This is the least reliable scraper — Sézane may need Playwright
    (a real browser) to work properly.
    """
    SEARCH_URLS = [
        "https://www.sezane.com/us-en/search?q={query}",
        "https://www.sezane.com/us-en/collection/all?q={query}",
    ]
    # Sézane may have an API at /api/... — try common patterns
    API_URLS = [
        "https://www.sezane.com/api/search?q={query}&locale=us-en",
        "https://www.sezane.com/api/products/search?q={query}",
    ]

    def _fetch_products(self, query: str) -> list[dict]:
        # Try API endpoints first
        for url_tpl in self.API_URLS:
            url = url_tpl.format(query=query.replace(" ", "+"))
            try:
                resp = self._throttled_get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    items = self._dig(data)
                    if items:
                        logger.debug(f"[sezane] API worked: {url}")
                        return items
            except:
                continue

        # Fall back to HTML page
        for url_tpl in self.SEARCH_URLS:
            url = url_tpl.format(query=query.replace(" ", "+"))
            try:
                resp = self._throttled_get(url)
                if resp.status_code != 200: continue
                html = resp.text
                # Look for JSON in script tags
                for m in re.finditer(r'"products"\s*:\s*(\[.*?\])', html, re.DOTALL):
                    try:
                        items = json.loads(m.group(1))
                        if items: return items
                    except: continue
                # JSON-LD
                for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                                     html, re.DOTALL):
                    try:
                        data = json.loads(m.group(1))
                        if isinstance(data, dict) and data.get("@type") == "ItemList":
                            return [i.get("item",i) for i in data.get("itemListElement",[])]
                    except: continue
            except:
                continue
        return []

    def _dig(self, data, depth=0):
        if depth > 12: return []
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if any(k in data[0] for k in ("id","name","title","price")):
                return data
        if isinstance(data, dict):
            for key in ("products","items","results","data","hits"):
                if key in data:
                    r = self._dig(data[key], depth+1)
                    if r: return r
        return []

    def _parse(self, item: dict, colour_name: str) -> Product | None:
        try:
            name = item.get("name", item.get("title", ""))
            pid = str(item.get("id", name[:20]))
            if not name: return None
            price = float(item.get("price", 0) or 0)
            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://www.sezane.com{url}"
            img = item.get("image", item.get("imageUrl", ""))
            if isinstance(img, dict): img = img.get("src","")
            if isinstance(img, list): img = img[0] if img else ""

            return Product(id=f"sezane-{pid}", name=name, price=price, currency="EUR",
                colour=colour_name, colour_original="",
                source="sezane", url=url, image_url=img,
                category="Clothing", brand="Sézane", sale_price=None)
        except: return None

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            for term in colour["search_terms"][:1]:
                if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
                try:
                    items = self._fetch_products(term)
                    logger.debug(f"[sezane] '{term}': {len(items)} items")
                    for item in items:
                        pid = str(item.get("id",""))
                        if pid in seen: continue
                        p = self._parse(item, colour["name"])
                        if p: seen.add(pid); products.append(p)
                except Exception as e:
                    logger.warning(f"[sezane] '{term}': {e}")
        return products
