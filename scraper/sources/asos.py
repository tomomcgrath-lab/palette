"""ASOS scraper — extracts from window.asos.plp embedded in search pages."""
import re, json, logging
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product
from scraper.categories import guess_category, is_clothing

logger = logging.getLogger("palette")

def clean_json_string(s: str) -> str:
    """Fix invalid escape sequences that ASOS puts in their JSON."""
    # Replace invalid \x hex escapes with unicode escapes
    s = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), s)
    # Replace other invalid escapes
    s = s.replace('\\/', '/')
    # Remove any remaining invalid single-char escapes
    s = re.sub(r'\\([^"\\/bfnrtu])', r'\1', s)
    return s

class AsosScraper(BaseScraper):
    SEARCH_URL = "https://www.asos.com/search/"

    def _extract_products(self, html: str) -> list[dict]:
        for m in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
            text = m.group(1)
            if '"products"' not in text or len(text) < 5000:
                continue
            idx = text.find('"products":[')
            if idx < 0:
                continue
            start = idx + len('"products":')
            depth = 0
            end = start
            for i in range(start, min(start + 500000, len(text))):
                if text[i] == '[': depth += 1
                elif text[i] == ']':
                    depth -= 1
                    if depth == 0: end = i + 1; break
            if end > start:
                raw = text[start:end]
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    # Clean invalid escapes and retry
                    try:
                        return json.loads(clean_json_string(raw))
                    except json.JSONDecodeError as e:
                        logger.debug(f"[asos] JSON parse failed even after cleaning: {e}")
        return []

    def _parse(self, item: dict, colour_name: str) -> Product | None:
        try:
            pid = str(item.get("id", ""))
            name = item.get("description", "")
            if not pid or not name: return None
            if not is_clothing(name): return None

            price = float(item.get("price", 0))
            sale_price = None
            reduced = item.get("reducedPrice")
            if reduced and item.get("isSale"):
                sale_price = float(reduced)

            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://www.asos.com/{url.lstrip('/')}"

            image = item.get("image", "")
            if image and not image.startswith("http"):
                image = f"https://{image}"

            return Product(
                id=f"asos-{pid}", name=name, price=price, currency="GBP",
                colour=colour_name, colour_original=item.get("colour", ""),
                source="asos", url=url, image_url=image,
                category=guess_category(name), brand=item.get("brandName", ""),
                sale_price=sale_price)
        except Exception as e:
            logger.debug(f"[asos] parse error: {e}")
            return None

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            for term in colour["search_terms"][:2]:
                if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
                try:
                    resp = self._throttled_get(self.SEARCH_URL,
                        params={"q": f"women {term}"})
                    if resp.status_code != 200: continue
                    items = self._extract_products(resp.text)
                    logger.debug(f"[asos] '{term}': {len(items)} items")
                    for item in items:
                        pid = str(item.get("id", ""))
                        if pid in seen: continue
                        col = self.colour_matches(item.get("colour", "")) or colour["name"]
                        p = self._parse(item, col)
                        if p: seen.add(pid); products.append(p)
                except Exception as e:
                    logger.warning(f"[asos] '{term}': {e}")
        return products
