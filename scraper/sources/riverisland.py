"""River Island IE scraper — tries multiple URL patterns."""
import re, json, logging
from bs4 import BeautifulSoup
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product

logger = logging.getLogger("palette")

class RiverIslandScraper(BaseScraper):
    SEARCH_URLS = [
        "https://www.riverisland.com/ie/search/{query}",
        "https://www.riverisland.com/ie/c/women?q={query}",
        "https://www.riverisland.com/search?q={query}",
        "https://www.riverisland.com/ie/search?term={query}",
    ]

    def _fetch_search(self, query: str) -> str | None:
        q = query.replace(" ", "+")
        for url_tpl in self.SEARCH_URLS:
            url = url_tpl.format(query=q)
            try:
                resp = self._throttled_get(url)
                if resp.status_code == 200 and len(resp.text) > 10000:
                    logger.debug(f"[ri] Working URL: {url}")
                    return resp.text
            except:
                continue
        return None

    def _extract_products(self, html: str) -> list[dict]:
        # Try __NEXT_DATA__ first
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                items = self._dig(data)
                if items: return items
            except: pass

        # Try any embedded JSON with products
        for pattern in [r'"products"\s*:\s*(\[.*?\])', r'"items"\s*:\s*(\[.*?\])']:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    items = json.loads(match.group(1))
                    if items and isinstance(items[0], dict): return items
                except: continue

        # HTML fallback
        soup = BeautifulSoup(html, "lxml")
        products = []
        for card in soup.select('[class*="product"], [class*="Product"], article'):
            try:
                link = card.select_one('a[href*="/p/"], a[href]')
                name_el = card.select_one('[class*="name"], [class*="title"], h3, h2')
                price_el = card.select_one('[class*="price"]')
                img = card.select_one('img[src]')

                name = name_el.get_text(strip=True) if name_el else ""
                if not name: continue
                url = link.get("href","") if link else ""
                if url and not url.startswith("http"):
                    url = f"https://www.riverisland.com{url}"
                pm = re.search(r'[\d.]+', (price_el.get_text() if price_el else "0").replace(",",""))
                price = float(pm.group()) if pm else 0
                image_url = img.get("src","") if img else ""
                if image_url.startswith("//"): image_url = f"https:{image_url}"

                products.append({"name":name,"url":url,"price":price,"image":image_url,
                    "id":url.split("/")[-1] if url else name[:20]})
            except: continue
        return products

    def _dig(self, data, depth=0):
        if depth > 15: return []
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if any(k in data[0] for k in ("productId","id","name","title","price")):
                return data
        if isinstance(data, dict):
            for key in ("products","items","results","searchResults","data","props","pageProps"):
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
            name = item.get("name", item.get("title", ""))
            pid = str(item.get("id", item.get("productId", name[:20])))
            if not name: return None
            price = float(item.get("price", 0) or 0)
            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://www.riverisland.com{url}"
            img = item.get("image", item.get("imageUrl", ""))
            if isinstance(img, dict): img = img.get("src","")
            if img and img.startswith("//"): img = f"https:{img}"

            return Product(id=f"ri-{pid}", name=name, price=price, currency="EUR",
                colour=colour_name, colour_original=item.get("colour",""),
                source="riverisland", url=url, image_url=img,
                category="Clothing", brand="River Island", sale_price=None)
        except Exception as e:
            logger.debug(f"[ri] parse error: {e}")
            return None

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            for term in colour["search_terms"][:1]:
                if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
                try:
                    html = self._fetch_search(f"women {term}")
                    if not html: continue
                    items = self._extract_products(html)
                    logger.debug(f"[ri] '{term}': {len(items)} items")
                    for item in items:
                        pid = str(item.get("id",""))
                        if pid in seen: continue
                        p = self._parse(item, colour["name"])
                        if p: seen.add(pid); products.append(p)
                except Exception as e:
                    logger.warning(f"[ri] '{term}': {e}")
        return products
