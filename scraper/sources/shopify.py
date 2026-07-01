"""
Shopify-based scraper — works for any Shopify store.
Used for: Mint Velvet, Nobody's Child (and any future Shopify source).

Shopify stores expose JSON endpoints:
  /search/suggest.json?q=...&resources[type]=product
  /products.json
  /collections/all.json
  /search?q=...&type=product&view=json
"""
import re, json, logging
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product
from scraper.categories import guess_category, is_clothing

logger = logging.getLogger("palette")


class ShopifyScraper(BaseScraper):
    """Generic scraper for Shopify-powered stores."""

    def _search_suggest(self, query: str) -> list[dict]:
        """Try Shopify's suggest endpoint — returns JSON directly."""
        url = f"{self.config['base_url']}/search/suggest.json"
        params = {
            "q": query,
            "resources[type]": "product",
            "resources[limit]": "20",
        }
        try:
            resp = self._throttled_get(url, params=params)
            data = resp.json()
            products = data.get("resources", {}).get("results", {}).get("products", [])
            return products
        except Exception as e:
            logger.debug(f"[{self.source_key}] suggest failed: {e}")
            return []

    def _search_json(self, query: str) -> list[dict]:
        """Try Shopify's search page with JSON view."""
        url = f"{self.config['base_url']}/search"
        params = {"q": query, "type": "product"}
        try:
            resp = self._throttled_get(url, params=params)
            # Try to find product JSON in the HTML
            html = resp.text
            products = []

            # Look for product data in JSON-LD
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                                 html, re.DOTALL):
                try:
                    data = json.loads(m.group(1))
                    if isinstance(data, dict):
                        if data.get("@type") == "ItemList":
                            for item in data.get("itemListElement", []):
                                products.append(item.get("item", item))
                        elif data.get("@type") == "Product":
                            products.append(data)
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("@type") == "Product":
                                products.append(item)
                except:
                    continue

            if products:
                return products

            # Look for Shopify product JSON in script tags
            for m in re.finditer(r'"product":\s*(\{[^}]+?"title"[^}]+?\})', html):
                try:
                    products.append(json.loads(m.group(1)))
                except:
                    continue

            return products
        except Exception as e:
            logger.debug(f"[{self.source_key}] search_json failed: {e}")
            return []

    def _products_json(self, page: int = 1) -> list[dict]:
        """Try Shopify's products.json endpoint."""
        url = f"{self.config['base_url']}/products.json"
        params = {"page": str(page), "limit": "50"}
        try:
            resp = self._throttled_get(url, params=params)
            data = resp.json()
            return data.get("products", [])
        except Exception as e:
            logger.debug(f"[{self.source_key}] products.json failed: {e}")
            return []

    def _parse(self, item: dict, colour_name: str) -> Product | None:
        try:
            # Handle both suggest API and JSON-LD formats
            name = item.get("title", item.get("name", ""))
            pid = str(item.get("id", item.get("sku", name[:20])))
            if not name: return None
            if not is_clothing(name): return None

            # Price — Shopify suggest returns price as string "49.00"
            price_str = item.get("price", item.get("price_min",
                        item.get("price_max", "0")))
            if isinstance(price_str, str):
                price_str = price_str.replace(",", "").replace("€", "").replace("£", "").strip()
                pm = re.search(r'[\d.]+', price_str)
                price = float(pm.group()) if pm else 0
            else:
                price = float(price_str) if price_str else 0

            # Shopify sometimes returns price in cents
            if price > 1000 and "." not in str(item.get("price", "")):
                price = price / 100

            # Compare price
            compare = item.get("compare_at_price", item.get("compare_at_price_max", 0))
            sale = None
            if compare:
                compare = float(compare) if not isinstance(compare, float) else compare
                if compare > 1000 and "." not in str(item.get("compare_at_price", "")):
                    compare = compare / 100
                if compare > price:
                    sale = price; price = compare

            # URL — item url may already include the locale path (e.g. /en-ie/products/...)
            # so build from the domain root, not base_url (which includes /en-ie)
            url = item.get("url", item.get("handle", ""))
            if url and not url.startswith("http"):
                # Strip query params for a clean link
                url = url.split("?")[0]
                if not url.startswith("/"):
                    url = f"/products/{url}"
                # Get just the scheme+domain from base_url
                m = re.match(r'(https?://[^/]+)', self.config['base_url'])
                domain = m.group(1) if m else self.config['base_url']
                url = f"{domain}{url}"

            # Image
            img = item.get("image", item.get("featured_image", ""))
            if isinstance(img, dict):
                img = img.get("src", img.get("url", ""))
            if img and img.startswith("//"):
                img = f"https:{img}"

            # Vendor/brand
            brand = item.get("vendor", item.get("brand", ""))

            # Product type as category
            category = item.get("product_type", item.get("type", "Clothing"))

            return Product(
                id=f"{self.source_key}-{pid}", name=name, price=price,
                currency=self.config.get("currency", "EUR"),
                colour=colour_name, colour_original="",
                source=self.source_key, url=url, image_url=img,
                category=(category if category and category != "Clothing" else guess_category(name)), brand=brand, sale_price=sale)
        except Exception as e:
            logger.debug(f"[{self.source_key}] parse error: {e}")
            return None

    def _colour_in_text(self, item: dict, search_terms: list[str]) -> bool:
        """Check if any colour search term appears in the product title/tags."""
        text = (item.get("title", "") + " " + item.get("body", "") +
                " " + str(item.get("tags", ""))).lower()
        return any(term.lower() in text for term in search_terms)

    def search_products(self) -> list[Product]:
        products, seen = [], set()

        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            for term in colour["search_terms"][:2]:
                if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
                try:
                    # Try suggest API first (most reliable)
                    items = self._search_suggest(f"women {term}")
                    if not items:
                        items = self._search_suggest(term)
                    if not items:
                        items = self._search_json(f"women {term}")

                    logger.debug(f"[{self.source_key}] '{term}': {len(items)} items")

                    for item in items:
                        pid = str(item.get("id", item.get("handle", "")))
                        if pid in seen: continue
                        p = self._parse(item, colour["name"])
                        if p: seen.add(pid); products.append(p)
                except Exception as e:
                    logger.warning(f"[{self.source_key}] '{term}': {e}")
        return products
