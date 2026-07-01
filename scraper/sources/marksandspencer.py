"""M&S Ireland scraper — Next.js site, extracts from __NEXT_DATA__."""
import re, json, logging
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product

logger = logging.getLogger("palette")

class MarksAndSpencerScraper(BaseScraper):
    # Try multiple URL patterns — M&S changes these
    SEARCH_URLS = [
        "https://www.marksandspencer.com/ie/srp?keyword={query}",
        "https://www.marksandspencer.com/ie/l/women?q={query}",
        "https://www.marksandspencer.com/ie/search?q={query}",
    ]

    def _fetch_search(self, query: str) -> str | None:
        for url_tpl in self.SEARCH_URLS:
            url = url_tpl.format(query=query.replace(" ", "+"))
            try:
                resp = self._throttled_get(url)
                if resp.status_code == 200 and len(resp.text) > 10000:
                    logger.debug(f"[m&s] Working URL: {url}")
                    return resp.text
            except:
                continue
        return None

    def _extract_products(self, html: str) -> list[dict]:
        # M&S uses __NEXT_DATA__ with product data
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not match:
            match = re.search(r'__NEXT_DATA__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return self._dig(data)
            except:
                pass
        return []

    def _dig(self, data, depth=0):
        if depth > 15: return []
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if any(k in data[0] for k in ("productId","id","name","title","price")):
                return data
        if isinstance(data, dict):
            for key in ("products","items","results","searchResults","data",
                        "props","pageProps","productList","listings"):
                if key in data:
                    r = self._dig(data[key], depth+1)
                    if r: return r
            for v in data.values():
                if isinstance(v, (dict, list)):
                    r = self._dig(v, depth+1)
                    if r: return r
        return []

    def _parse(self, item: dict, colour_name: str) -> Product | None:
        try:
            name = item.get("name", item.get("title", item.get("productName", "")))
            pid = str(item.get("productId", item.get("id", "")))
            if not name: return None

            price_d = item.get("price", item.get("prices", {}))
            if isinstance(price_d, dict):
                price = float(price_d.get("current", price_d.get("now",
                    price_d.get("salePrice", price_d.get("value", 0)))) or 0)
                was = float(price_d.get("was", price_d.get("previous", 0)) or 0)
            elif isinstance(price_d, (int, float)):
                price = float(price_d); was = 0
            else:
                pm = re.search(r'[\d.]+', str(price_d))
                price = float(pm.group()) if pm else 0; was = 0

            sale = None
            if was and was > price: sale = price; price = was

            url = item.get("url", item.get("link", ""))
            if url and not url.startswith("http"):
                url = f"https://www.marksandspencer.com{url}"

            img = item.get("image", item.get("imageUrl", item.get("media",{}).get("src","")))
            if isinstance(img, list): img = img[0] if img else ""
            if isinstance(img, dict): img = img.get("src", img.get("url", ""))
            if img and img.startswith("//"): img = f"https:{img}"

            return Product(id=f"m&s-{pid}", name=name, price=price, currency="EUR",
                colour=colour_name, colour_original=item.get("colour",""),
                source="marksandspencer", url=url, image_url=img,
                category=item.get("category","Clothing"),
                brand=item.get("brand","M&S"), sale_price=sale)
        except Exception as e:
            logger.debug(f"[m&s] parse error: {e}")
            return None

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            for term in colour["search_terms"][:1]:  # 1 term — M&S is slow
                if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
                try:
                    html = self._fetch_search(f"women {term}")
                    if not html: continue
                    items = self._extract_products(html)
                    logger.debug(f"[m&s] '{term}': {len(items)} items")
                    for item in items:
                        pid = str(item.get("productId", item.get("id","")))
                        if pid in seen: continue
                        col = self.colour_matches(item.get("colour","")) or colour["name"]
                        p = self._parse(item, col)
                        if p: seen.add(pid); products.append(p)
                except Exception as e:
                    logger.warning(f"[m&s] '{term}': {e}")
        return products
