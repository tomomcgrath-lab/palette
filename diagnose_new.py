"""Diagnose 7 new sources — tries both curl_cffi and Playwright."""
import re, json, time
from curl_cffi import requests

SOURCES = {
    "brownthomas": {
        "urls": [
            "https://www.brownthomas.com/search?q=blue&lang=en_IE",
            "https://www.brownthomas.com/women/clothing/?q=blue",
        ]
    },
    "debenhams": {
        "urls": [
            "https://www.debenhams.ie/search/blue",
            "https://www.debenhams.ie/women?q=blue",
            "https://www.debenhams.ie/search?q=blue",
        ]
    },
    "next": {
        "urls": [
            "https://www.next.ie/en/search?w=blue+women",
            "https://www.next.ie/en/shop/gender-women/colour-blue",
        ]
    },
    "hm": {
        "urls": [
            "https://www2.hm.com/en_ie/search-results.html?q=blue",
            "https://www2.hm.com/en_ie/ladies/shop-by-colour/blue.html",
        ]
    },
    "reiss": {
        "urls": [
            "https://www.reiss.com/womens/search?q=blue",
            "https://www.reiss.com/search?q=blue",
        ]
    },
    "johnlewis": {
        "urls": [
            "https://www.johnlewis.com/search?search-term=blue+women",
            "https://www.johnlewis.com/women/blue/c6000013",
        ]
    },
    "zara": {
        "urls": [
            "https://www.zara.com/ie/en/search?searchTerm=blue",
            "https://www.zara.com/ie/en/woman-new-in-l1180.html",
        ]
    },
}

session = requests.Session(impersonate="chrome")

for name, config in SOURCES.items():
    print(f"\n{'#' * 60}")
    print(f"# {name.upper()}")
    print(f"{'#' * 60}")

    for url in config["urls"]:
        print(f"\n  Trying: {url}")
        try:
            resp = session.get(url, timeout=20)
            print(f"  Status: {resp.status_code}, Size: {len(resp.text)} bytes")

            if resp.status_code != 200:
                continue

            html = resp.text
            soup_needed = False

            # Page title
            title_m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
            title = title_m.group(1).strip()[:80] if title_m else "(no title)"
            print(f"  Title: {title}")

            # Bot check
            for sign in ["captcha", "challenge-platform", "access denied", "robot"]:
                if sign.lower() in html.lower():
                    print(f"  ⚠ BOT: '{sign}' found")

            # Platform detection
            for pat, label in [
                (r'Shopify\.', "Shopify"), (r'__NEXT_DATA__', "Next.js"),
                (r'__NUXT__', "Nuxt"), (r'dataLayer', "dataLayer"),
                (r'__INITIAL_STATE__', "Initial State"),
            ]:
                if re.search(pat, html):
                    print(f"  Platform: {label}")

            # Product-like links
            for pat in ['/p/', '/prd/', '/product/', '/pdp/', '/item/']:
                links = re.findall(rf'href="([^"]*{pat}[^"]*)"', html)
                if links:
                    print(f"  Links with '{pat}': {len(links)}")
                    print(f"    e.g. {links[0][:100]}")
                    break

            # Script tags with product data
            prod_scripts = 0
            for m in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
                text = m.group(1)
                if len(text) < 200: continue
                keywords = [kw for kw in ['"products"','"items"','"name"','"price"']
                           if kw in text]
                if len(keywords) >= 2:
                    prod_scripts += 1
                    if prod_scripts <= 2:
                        print(f"  Script ({len(text)} chars): {', '.join(keywords)}")
                        preview = text[:200].replace('\n',' ').strip()
                        print(f"    Preview: {preview[:150]}...")

            # Product-related CSS classes
            classes = set()
            for m in re.finditer(r'class="([^"]*)"', html):
                for cls in m.group(1).split():
                    if any(kw in cls.lower() for kw in ["product","card","tile","price","listing"]):
                        classes.add(cls)
            if classes:
                print(f"  CSS classes: {', '.join(sorted(classes)[:10])}")

            if resp.status_code == 200 and len(html) > 5000:
                break  # got a good response, skip alt URLs

        except Exception as e:
            print(f"  ERROR: {e}")

        time.sleep(2)

print(f"\n{'=' * 60}")
print("Done! Paste everything above back to Claude.")
