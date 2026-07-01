"""Very.ie scraper — extracts from window.__product_listing_initial_state__ JSON."""
import re, json, logging
from bs4 import BeautifulSoup
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product
from scraper.categories import guess_category

logger = logging.getLogger("palette")

class VeryScraper(BaseScraper):
    SEARCH_URL = "https://www.very.ie/e/q/{query}.end"

    def _extract_products(self, html: str) -> list[dict]:
        # Very embeds: window.__product_listing_initial_state__={...}
        match = re.search(
            r'window\.__product_listing_initial_state__\s*=\s*(\{.*?\});\s*$',
            html, re.MULTILINE | re.DOTALL
        )
        if match:
            try:
                data = json.loads(match.group(1))
                return self._dig(data)
            except json.JSONDecodeError:
                pass

        # Broader search for the same pattern
        match = re.search(
            r'__product_listing_initial_state__\s*=\s*(\{.+?\})\s*;',
            html, re.DOTALL
        )
        if match:
            try:
                data = json.loads(match.group(1))
                return self._dig(data)
            except:
                pass

        # Fallback: parse HTML cards
        return self._parse_html_cards(html)

    def _dig(self, data, depth=0):
        if depth > 15: return []
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if any(k in data[0] for k in ("product_id","productId","id","name","title")):
                return data
        if isinstance(data, dict):
            for key in ("products","items","results","data","queries",
                        "state","pages","searchResults"):
                if key in data:
                    r = self._dig(data[key], depth+1)
                    if r: return r
            for v in data.values():
                if isinstance(v, (dict, list)):
                    r = self._dig(v, depth+1)
                    if r: return r
        return []

    def _parse_html_cards(self, html: str) -> list[dict]:
        """Fallback: parse product cards from HTML."""
        soup = BeautifulSoup(html, "lxml")
        products = []
        cards = soup.select('[data-testid="gallery-product-card"]')
        for card in cards:
            try:
                brand_el = card.select_one('[class*="productCard__brand"]')
                title_el = card.select_one('[class*="productCard__title"]')
                price_el = card.select_one('[class*="price"]')
                link = card.select_one('a[class*="productCard__link"]')
                img = card.select_one('img[src]')

                name_parts = []
                if brand_el: name_parts.append(brand_el.get_text(strip=True))
                if title_el: name_parts.append(title_el.get_text(strip=True))
                name = " ".join(name_parts) or ""

                url = link.get("href","") if link else ""
                if url and not url.startswith("http"):
                    url = f"https://www.very.ie{url}"

                price_text = price_el.get_text(strip=True) if price_el else "0"
                pm = re.search(r'[\d,.]+', price_text.replace(",",""))
                price = float(pm.group()) if pm else 0

                image_url = img.get("src","") if img else ""
                if image_url.startswith("//"): image_url = f"https:{image_url}"

                pid = card.get("data-cnstrc-item-id",
                      card.get("data-tagg-id", url.split("/")[-1] if url else ""))

                if name:
                    products.append({"id": pid, "name": name, "price": price,
                                     "url": url, "image": image_url})
            except:
                continue
        return products

    def _parse(self, item: dict, colour_name: str) -> Product | None:
        try:
            name = item.get("name", item.get("title", item.get("productTitle", "")))
            pid = str(item.get("product_id", item.get("productId",
                      item.get("id", name[:20]))))
            if not name: return None

            # Price handling
            price_d = item.get("price", item.get("prices", 0))
            if isinstance(price_d, dict):
                price = float(price_d.get("current", price_d.get("now",
                              price_d.get("value", 0))) or 0)
                was = float(price_d.get("was", price_d.get("previous", 0)) or 0)
            elif isinstance(price_d, (int, float)):
                price = float(price_d)
                was = 0
            else:
                pm = re.search(r'[\d.]+', str(price_d))
                price = float(pm.group()) if pm else 0
                was = 0

            sale = None
            if was and was > price: sale = price; price = was

            url = item.get("url", item.get("link", item.get("pdpUrl", "")))
            if url and not url.startswith("http"):
                url = f"https://www.very.ie{url}"

            img = item.get("image", item.get("imageUrl", item.get("heroImageUrl", "")))
            if isinstance(img, list): img = img[0] if img else ""
            if isinstance(img, dict): img = img.get("src", img.get("url", ""))
            if img and img.startswith("//"): img = f"https:{img}"

            brand = item.get("brand", item.get("brandName", ""))
            if isinstance(brand, dict): brand = brand.get("name", "")

            return Product(id=f"very-{pid}", name=name, price=price, currency="EUR",
                colour=colour_name, colour_original=item.get("colour",""),
                source="very", url=url, image_url=img,
                category=guess_category(name), brand=brand, sale_price=sale)
        except Exception as e:
            logger.debug(f"[very] parse error: {e}")
            return None

    def _guess_cat(self, name):
        n = name.lower()
        for k, v in {"dress":"Dresses","skirt":"Skirts","trouser":"Trousers",
            "jean":"Jeans","top":"Tops","blouse":"Tops","shirt":"Tops",
            "jumper":"Knitwear","cardigan":"Knitwear","coat":"Coats",
            "jacket":"Jackets","blazer":"Jackets","short":"Shorts",
            "jumpsuit":"Jumpsuits","bag":"Bags","boot":"Shoes","shoe":"Shoes"}.items():
            if k in n: return v
        return "Clothing"

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
                    logger.debug(f"[very] '{term}': {len(items)} raw items")
                    for item in items:
                        pid = str(item.get("product_id", item.get("id", "")))
                        if pid in seen: continue
                        col = self.colour_matches(item.get("colour","")) or colour["name"]
                        p = self._parse(item, col)
                        if p: seen.add(pid); products.append(p)
                except Exception as e:
                    logger.warning(f"[very] '{term}': {e}")
        return products
