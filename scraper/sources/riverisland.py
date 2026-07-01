"""River Island scraper — uses Playwright to render JavaScript."""
import re, logging
from playwright.sync_api import sync_playwright
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product
from scraper.categories import guess_category

logger = logging.getLogger("palette")

class RiverIslandScraper(BaseScraper):
    SEARCH_URL = "https://www.riverisland.com/ie/c/women?q={query}"

    def _scrape_page(self, url: str) -> list[dict]:
        """Load page in headless Chrome and extract product cards."""
        products = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)

                # River Island cards: a.card___* with /p/ links
                cards = page.query_selector_all('a[href*="/p/"]')
                for card in cards:
                    try:
                        href = card.evaluate("e => e.href") or ""
                        text = card.evaluate("e => e.textContent.trim()") or ""
                        img_el = card.query_selector("img.single-tile-image, img[class*='tile-image']")
                        img_src = img_el.evaluate("e => e.src") if img_el else ""

                        # Extract name — it's the first part of text before the price
                        price_match = re.search(r'[€£]\s*[\d,.]+', text)
                        name = text[:price_match.start()].strip() if price_match else text[:60].strip()
                        price = float(price_match.group().replace("€","").replace("£","").replace(",","").strip()) if price_match else 0

                        # Product ID from URL
                        pid = href.rstrip("/").split("-")[-1] if href else ""

                        if name and price > 0:
                            products.append({
                                "name": name, "price": price, "url": href,
                                "image": img_src, "id": pid,
                            })
                    except:
                        continue

                browser.close()
        except Exception as e:
            logger.warning(f"[ri] Playwright error: {e}")
        return products

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            term = colour["search_terms"][0]  # 1 term per colour — Playwright is slow
            try:
                url = self.SEARCH_URL.format(query=f"women+{term}".replace(" ", "+"))
                items = self._scrape_page(url)
                logger.debug(f"[ri] '{term}': {len(items)} items")
                for item in items:
                    pid = item.get("id", "")
                    if pid in seen: continue
                    p = Product(
                        id=f"ri-{pid}", name=item["name"],
                        price=item["price"], currency="EUR",
                        colour=colour["name"], colour_original="",
                        source="riverisland", url=item["url"],
                        image_url=item["image"],
                        category=guess_category(item["name"]), brand="River Island",
                    )
                    seen.add(pid)
                    products.append(p)
            except Exception as e:
                logger.warning(f"[ri] '{term}': {e}")
        return products
