"""Debenhams scraper — uses Playwright to render JavaScript."""
import re, logging
from playwright.sync_api import sync_playwright
from scraper.config import COLOURS, MAX_PRODUCTS_PER_SOURCE
from scraper.sources.base import BaseScraper, Product
from scraper.categories import guess_category

logger = logging.getLogger("palette")

class DebenhamsScraper(BaseScraper):
    SEARCH_URL = "https://www.debenhams.ie/search/{query}"

    def _scrape_page(self, url: str) -> list[dict]:
        products = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 900},
                    locale="en-IE",
                )
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3500)

                cards = page.query_selector_all('a[href*="/product/"]')
                for card in cards:
                    try:
                        href = card.evaluate("e => e.href") or ""
                        text = card.evaluate("e => e.textContent.trim()") or ""
                        img = card.evaluate("e => e.querySelector('img')?.src || ''") or ""

                        # text looks like: "CoastChiffon Cape Pencil Dress€105.35€150.50-30%"
                        # Split brand+name from prices
                        price_match = re.search(r'€\s*([\d,.]+)', text)
                        name = text[:price_match.start()].strip() if price_match else text[:80].strip()

                        # Get all prices — first is current, second (if any) is original
                        prices = re.findall(r'€\s*([\d,.]+)', text)
                        price = float(prices[0].replace(",", "")) if prices else 0
                        sale_price = None
                        if len(prices) >= 2:
                            orig = float(prices[1].replace(",", ""))
                            if orig > price:
                                sale_price = price
                                price = orig

                        pid = ""
                        pid_match = re.search(r'_([a-z0-9]+)(?:\?|$)', href)
                        if pid_match:
                            pid = pid_match.group(1)
                        elif href:
                            pid = href.rstrip("/").split("/")[-1].split("?")[0]

                        if name and price > 0:
                            products.append({
                                "name": name, "price": price, "sale_price": sale_price,
                                "url": href, "image": img, "id": pid,
                            })
                    except:
                        continue

                browser.close()
        except Exception as e:
            logger.warning(f"[debenhams] Playwright error: {e}")
        return products

    def search_products(self) -> list[Product]:
        products, seen = [], set()
        for colour in COLOURS:
            if len(products) >= MAX_PRODUCTS_PER_SOURCE: break
            term = colour["search_terms"][0]
            try:
                q = f"{term}".replace(" ", "%20")
                url = self.SEARCH_URL.format(query=q)
                items = self._scrape_page(url)
                logger.debug(f"[debenhams] '{term}': {len(items)} items")
                for item in items:
                    pid = item.get("id", "")
                    if pid in seen: continue
                    p = Product(
                        id=f"deb-{pid}", name=item["name"],
                        price=item["price"], currency="EUR",
                        colour=colour["name"], colour_original="",
                        source="debenhams", url=item["url"],
                        image_url=item["image"],
                        category=guess_category(item["name"]),
                        brand="", sale_price=item.get("sale_price"))
                    seen.add(pid)
                    products.append(p)
            except Exception as e:
                logger.warning(f"[debenhams] '{term}': {e}")
        return products
