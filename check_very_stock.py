"""Check what fields Very.ie gives us — especially stock status and colour."""
import re, json
from curl_cffi import requests

session = requests.Session(impersonate="chrome")

r = session.get("https://www.very.ie/e/q/women-blue.end", timeout=30)
print(f"Status: {r.status_code}, size: {len(r.text)}")

# Find the product listing state
m = re.search(r'window\.__product_listing_initial_state__\s*=\s*(\{.*?\});',
              r.text, re.DOTALL)
if not m:
    m = re.search(r'__product_listing_initial_state__\s*=\s*(\{.+?\})\s*;', r.text, re.DOTALL)

if m:
    try:
        data = json.loads(m.group(1))
        # Dig for products
        def dig(d, depth=0):
            if depth > 15: return []
            if isinstance(d, list) and d and isinstance(d[0], dict):
                if any(k in d[0] for k in ("product_id","productId","id","name","title")):
                    return d
            if isinstance(d, dict):
                for v in d.values():
                    if isinstance(v, (dict, list)):
                        r2 = dig(v, depth+1)
                        if r2: return r2
            return []
        products = dig(data)
        print(f"\nFound {len(products)} products\n")
        for p in products[:3]:
            print("=" * 50)
            print(f"Name: {p.get('name', p.get('title', '?'))[:50]}")
            print(f"ALL KEYS: {list(p.keys())}")
            # Look for stock-related fields
            for k, v in p.items():
                if any(w in k.lower() for w in ["stock", "avail", "sold", "status", "colour", "color"]):
                    print(f"  {k}: {v}")
            print()
    except Exception as e:
        print(f"Parse error: {e}")
else:
    print("Could not find product listing state")

print("=" * 50)
print("Done! Paste back to Claude.")
