"""
Peek at the harder sources using a real browser (Playwright).
Renders JavaScript so we can see the actual products.
Paste the output back to Claude.
"""
from playwright.sync_api import sync_playwright

SITES = {
    "debenhams": "https://www.debenhams.ie/search/blue",
    "next": "https://www.next.ie/en/search?w=blue+women",
    "reiss": "https://www.reiss.com/search?q=blue",
    "hm": "https://www2.hm.com/en_ie/ladies/shop-by-colour/blue.html",
    "zara": "https://www.zara.com/ie/en/search?searchTerm=blue",
    "brownthomas": "https://www.brownthomas.com/search?q=blue&lang=en_IE",
}


def peek(page, name, url):
    print(f"\n{'#' * 60}")
    print(f"# {name.upper()}")
    print(f"# {url}")
    print(f"{'#' * 60}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(4000)  # let JS render
    except Exception as e:
        print(f"  LOAD ERROR: {str(e)[:100]}")
        # Still try to read whatever loaded
    try:
        title = page.title()
        print(f"  Title: {title[:70]}")
        html_len = len(page.content())
        print(f"  Rendered size: {html_len} bytes")
    except:
        pass

    # Try to find product cards
    selectors = [
        'a[href*="/p/"]', 'a[href*="/prd/"]', 'a[href*="/product/"]',
        'a[href*="/pdp/"]', 'a[href*="-p"]',
        '[class*="product-card"]', '[class*="productCard"]',
        '[class*="product-tile"]', '[class*="ProductCard"]',
        '[data-testid*="product"]', '[data-auto-id*="product"]',
        'article[class*="product"]', 'li[class*="product"]',
    ]
    best = None
    for sel in selectors:
        try:
            els = page.query_selector_all(sel)
            if els and len(els) > 3:
                print(f"\n  '{sel}': {len(els)} found")
                if best is None:
                    best = (sel, els)
        except:
            pass

    # Dump details of the best match
    if best:
        sel, els = best
        print(f"\n  --- Details from '{sel}' (first 2) ---")
        for el in els[:2]:
            try:
                tag = el.evaluate("e => e.tagName")
                classes = el.evaluate("e => e.className")
                href = el.evaluate("e => e.href || e.querySelector('a')?.href || ''")
                text = el.evaluate("e => e.textContent.trim().substring(0,100)")
                img = el.evaluate("e => e.querySelector('img')?.src || ''")
                print(f"    <{tag} class='{str(classes)[:60]}'>")
                if href: print(f"      href: {href[:90]}")
                if text: print(f"      text: {text[:90]}")
                if img: print(f"      img: {img[:90]}")
            except Exception as e:
                print(f"      (read error: {str(e)[:50]})")

    # Look for prices
    try:
        prices = page.query_selector_all('[class*="price"], [class*="Price"]')
        shown = 0
        for p in prices:
            t = p.evaluate("e => e.textContent.trim()")
            if t and any(c in t for c in "€£$") and shown < 3:
                print(f"    price sample: {t[:40]}")
                shown += 1
    except:
        pass


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        locale="en-IE",
    )
    page = context.new_page()
    for name, url in SITES.items():
        try:
            peek(page, name, url)
        except Exception as e:
            print(f"  FATAL: {str(e)[:100]}")
    browser.close()

print(f"\n{'=' * 60}")
print("Done! Paste everything above back to Claude.")
