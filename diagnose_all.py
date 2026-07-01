"""
Palette — Full Source Diagnostic
Analyses all 7 retailer sites to find their product data structure.
Run this, paste the FULL output back to Claude.

Usage:
    python diagnose_all.py
"""

import re
import json
import time
from curl_cffi import requests
from bs4 import BeautifulSoup

SOURCES = {
    "asos": "https://www.asos.com/search/?q=women+blue+dress",
    "very": "https://www.very.ie/e/q/women-blue.end",
    "mintvelvet": "https://mintvelvet.com/en-ie/search?q=blue",
    "sezane": "https://www.sezane.com/us-en/search?q=blue",
    "nobodyschild": "https://www.nobodyschild.com/en-ie/search?q=blue",
    "marksandspencer": "https://www.marksandspencer.com/ie/l/women/blue?q=blue",
    "riverisland": "https://www.riverisland.com/ie/search?q=blue+women",
}

# Some sites might need different search URL patterns — try alternatives
ALT_URLS = {
    "mintvelvet": [
        "https://mintvelvet.com/en-ie/search?q=blue",
        "https://www.mintvelvet.com/en-ie/search?q=blue",
        "https://www.mintvelvet.com/en-ie/clothing?colour=blue",
    ],
    "sezane": [
        "https://www.sezane.com/us-en/search?q=blue",
        "https://www.sezane.com/us-en/collection/all?q=blue",
    ],
    "nobodyschild": [
        "https://www.nobodyschild.com/en-ie/search?q=blue",
        "https://www.nobodyschild.com/en-ie/collections/all?q=blue",
    ],
    "marksandspencer": [
        "https://www.marksandspencer.com/ie/l/women/blue?q=blue",
        "https://www.marksandspencer.com/ie/search?q=women+blue",
    ],
    "riverisland": [
        "https://www.riverisland.com/ie/search?q=blue+women",
        "https://www.riverisland.com/ie/women/search?q=blue",
    ],
}

session = requests.Session(impersonate="chrome")


def diagnose_source(name, url):
    """Diagnose a single source."""
    print(f"\n{'#' * 70}")
    print(f"# {name.upper()}")
    print(f"# {url}")
    print(f"{'#' * 70}")

    try:
        resp = session.get(url, timeout=30)
        print(f"Status: {resp.status_code}, Size: {len(resp.text)} bytes")
    except Exception as e:
        print(f"FAILED TO FETCH: {e}")
        # Try alternatives
        if name in ALT_URLS:
            for alt_url in ALT_URLS[name][1:]:
                try:
                    print(f"  Trying alt: {alt_url}")
                    resp = session.get(alt_url, timeout=30)
                    print(f"  Status: {resp.status_code}, Size: {len(resp.text)} bytes")
                    url = alt_url
                    break
                except Exception as e2:
                    print(f"  Also failed: {e2}")
                    continue
            else:
                print(f"  ALL URLs FAILED for {name}")
                return
        else:
            return

    if resp.status_code != 200:
        print(f"  Non-200 status! Trying alternatives...")
        if name in ALT_URLS:
            for alt_url in ALT_URLS[name]:
                if alt_url == url:
                    continue
                try:
                    resp2 = session.get(alt_url, timeout=30)
                    if resp2.status_code == 200:
                        print(f"  SUCCESS with: {alt_url} ({len(resp2.text)} bytes)")
                        resp = resp2
                        url = alt_url
                        break
                    else:
                        print(f"  {alt_url} → {resp2.status_code}")
                except Exception as e:
                    print(f"  {alt_url} → {e}")
        if resp.status_code != 200:
            print(f"  Could not get 200 for {name}")

    html = resp.text
    soup = BeautifulSoup(html, "lxml")

    # Title (tells us if we got a real page or a bot challenge)
    title = soup.title.string.strip() if soup.title and soup.title.string else "(no title)"
    print(f"Page title: {title}")

    # Bot detection check
    bot_signs = ["captcha", "challenge-platform", "access denied", "are you a robot", "cf-browser"]
    for sign in bot_signs:
        if sign.lower() in html.lower():
            print(f"  ⚠ BOT DETECTION: Found '{sign}' in page!")

    # 1. Embedded JSON state
    print(f"\n  --- Embedded JSON State ---")
    for pat_name, pattern in [
        ("__NEXT_DATA__", r'__NEXT_DATA__'),
        ("__INITIAL_STATE__", r'__INITIAL_STATE__'),
        ("__NUXT__", r'__NUXT__'),
        ("window.__data", r'window\.__data'),
        ("Shopify", r'Shopify\.'),
        ("dataLayer", r'dataLayer\s*='),
    ]:
        if re.search(pattern, html):
            print(f"    FOUND: {pat_name}")

    # 2. JSON-LD
    ld_scripts = soup.find_all("script", type="application/ld+json")
    if ld_scripts:
        print(f"\n  --- JSON-LD ({len(ld_scripts)} scripts) ---")
        for i, script in enumerate(ld_scripts):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data[:2]:
                        if isinstance(item, dict):
                            print(f"    [{i}] @type={item.get('@type', '?')}, keys={list(item.keys())[:8]}")
                elif isinstance(data, dict):
                    print(f"    [{i}] @type={data.get('@type', '?')}, keys={list(data.keys())[:8]}")
                    # If ItemList, show first item
                    if data.get("@type") == "ItemList" and "itemListElement" in data:
                        items = data["itemListElement"]
                        print(f"         ItemList has {len(items)} items")
                        if items:
                            first = items[0].get("item", items[0]) if isinstance(items[0], dict) else items[0]
                            if isinstance(first, dict):
                                print(f"         First item keys: {list(first.keys())[:10]}")
            except Exception as e:
                print(f"    [{i}] parse error: {e}")

    # 3. Big script tags with product-like content
    print(f"\n  --- Script tags with product data ---")
    found_scripts = 0
    for i, script in enumerate(soup.find_all("script")):
        text = script.string or ""
        if len(text) < 200:
            continue
        product_keywords = ['"products"', '"productId"', '"product_id"', '"items"',
                           '"searchResults"', '"name"', '"price"', '"variants"']
        matches = [(kw, text.count(kw)) for kw in product_keywords if kw in text]
        if matches and len(text) > 500:
            found_scripts += 1
            if found_scripts <= 3:  # show max 3
                print(f"    Script {i} (len={len(text)}):")
                for kw, count in matches:
                    print(f"      {kw} x{count}")
                # Show a small preview
                preview = text[:400].replace('\n', ' ').replace('  ', ' ').strip()
                print(f"      Preview: {preview[:250]}...")
    if found_scripts == 0:
        print(f"    (none found)")
    elif found_scripts > 3:
        print(f"    ... and {found_scripts - 3} more")

    # 4. HTML product cards
    print(f"\n  --- Product card elements ---")
    card_selectors = [
        ('article', 'article'),
        ('product-testid', '[data-testid*="product"]'),
        ('class~product', '[class*="product"]'),
        ('class~Product', '[class*="Product"]'),
        ('class~card', '[class*="card"]'),
        ('class~Card', '[class*="Card"]'),
        ('class~tile', '[class*="tile"]'),
        ('class~Tile', '[class*="Tile"]'),
        ('class~item', '[class*="item-"]'),
        ('class~grid', '[class*="grid-item"]'),
        ('data-product-id', '[data-product-id]'),
        ('data-sku', '[data-sku]'),
        ('data-pid', '[data-pid]'),
    ]
    for label, sel in card_selectors:
        try:
            found = soup.select(sel)
            if found and len(found) > 1:
                first = found[0]
                classes = " ".join(first.get("class", []))[:80]
                tag = first.name
                # Get data attributes
                data_attrs = {k: v for k, v in first.attrs.items() if k.startswith("data-")}
                data_str = str(data_attrs)[:80] if data_attrs else ""
                print(f"    '{sel}' → {len(found)} elements")
                print(f"      First: <{tag} class=\"{classes}\">")
                if data_str:
                    print(f"      Data attrs: {data_str}")
        except:
            pass

    # 5. Product-like links
    link_patterns = ['/p/', '/product/', '/prd/', '/pdp/', '/item/']
    print(f"\n  --- Product links ---")
    for pat in link_patterns:
        links = soup.select(f'a[href*="{pat}"]')
        if links:
            print(f"    Links with '{pat}': {len(links)}")
            for link in links[:2]:
                href = link.get("href", "")[:100]
                text = link.get_text(strip=True)[:50]
                print(f"      href={href}")
                if text:
                    print(f"      text={text}")

    # 6. Key CSS classes
    print(f"\n  --- Product-related CSS classes ---")
    classes_found = set()
    for el in soup.find_all(True, class_=True):
        for cls in el.get("class", []):
            cl = cls.lower()
            if any(kw in cl for kw in ["product", "card", "tile", "price", "listing", "result", "grid-item"]):
                classes_found.add(cls)
    for cls in sorted(classes_found)[:20]:
        print(f"    .{cls}")

    # 7. Save HTML for reference
    filename = f"{name}_debug.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  HTML saved to {filename}")


def main():
    print("Palette Source Diagnostic")
    print("Testing all 7 retailer sources...\n")

    for name, url in SOURCES.items():
        diagnose_source(name, url)
        time.sleep(2)  # polite delay between sites

    print(f"\n\n{'=' * 70}")
    print("DONE! Paste everything above back to Claude.")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
