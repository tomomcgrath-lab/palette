"""
Peek at M&S, River Island, and Sézane using a real browser.
Playwright renders all the JavaScript so we can see the actual products.
"""
import json, re
from playwright.sync_api import sync_playwright

def peek_site(page, name, url, search_term="blue"):
    print(f"\n{'#' * 60}")
    print(f"# {name}")
    print(f"# {url}")
    print(f"{'#' * 60}")

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)  # extra wait for lazy-loading

    title = page.title()
    print(f"Page title: {title}")

    html = page.content()
    print(f"Rendered HTML size: {len(html)} bytes")

    # Look for product cards
    selectors_to_try = [
        ('a[href*="/p/"]', '/p/ links'),
        ('a[href*="/prd/"]', '/prd/ links'),
        ('a[href*="/product/"]', '/product/ links'),
        ('[class*="product-card"]', 'product-card class'),
        ('[class*="productCard"]', 'productCard class'),
        ('[class*="Product"]', 'Product class'),
        ('[data-testid*="product"]', 'product testid'),
        ('[data-product-id]', 'data-product-id'),
        ('article', 'article tags'),
        ('[class*="tile"]', 'tile class'),
        ('[class*="card"]', 'card class'),
    ]

    for selector, label in selectors_to_try:
        try:
            elements = page.query_selector_all(selector)
            if elements and len(elements) > 1:
                print(f"\n  '{selector}' ({label}): {len(elements)} found")
                # Show first element's details
                el = elements[0]
                tag = el.evaluate("e => e.tagName")
                classes = el.evaluate("e => e.className")
                href = el.evaluate("e => e.href || ''")
                text = el.evaluate("e => e.textContent.trim().substring(0, 80)")
                inner = el.evaluate("e => e.innerHTML.substring(0, 300)")
                print(f"    Tag: {tag}, Class: {str(classes)[:80]}")
                if href:
                    print(f"    Href: {href[:100]}")
                if text:
                    print(f"    Text: {text[:80]}")
                print(f"    Inner HTML: {inner[:250]}...")
        except:
            pass

    # Check for product images
    try:
        imgs = page.query_selector_all('img[src*="product"], img[src*="media"], img[class*="product"]')
        if imgs:
            print(f"\n  Product images: {len(imgs)}")
            src = imgs[0].evaluate("e => e.src")
            print(f"    First: {src[:100]}")
    except:
        pass

    # Look for price elements
    try:
        prices = page.query_selector_all('[class*="price"], [class*="Price"]')
        if prices:
            print(f"\n  Price elements: {len(prices)}")
            for p in prices[:3]:
                text = p.evaluate("e => e.textContent.trim()")
                if text and any(c in text for c in "€£$0123456789"):
                    print(f"    {text[:60]}")
    except:
        pass


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
    )
    page = context.new_page()

    # M&S — try their search
    try:
        peek_site(page, "M&S Ireland",
            "https://www.marksandspencer.com/ie/l/women?q=blue")
    except Exception as e:
        print(f"  ERROR: {e}")

    # River Island — try their category with query
    try:
        peek_site(page, "River Island",
            "https://www.riverisland.com/ie/c/women?q=blue")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Sézane
    try:
        peek_site(page, "Sézane",
            "https://www.sezane.com/us-en/search?q=blue")
    except Exception as e:
        print(f"  ERROR: {e}")

    browser.close()

print(f"\n{'=' * 60}")
print("Done! Paste everything above back to Claude.")
