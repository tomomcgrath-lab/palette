"""Check ASOS price fields and Shopify (Mint Velvet / Nobody's Child) URL fields."""
import re, json
from curl_cffi import requests

session = requests.Session(impersonate="chrome")

# ── ASOS: what does price actually look like vs the website? ──
print("=" * 60)
print("ASOS — price fields")
print("=" * 60)
r = session.get("https://www.asos.com/search/", params={"q": "women blue dress"})
for m in re.finditer(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL):
    text = m.group(1)
    if '"products":[' not in text or len(text) < 5000:
        continue
    idx = text.find('"products":[')
    start = idx + len('"products":')
    depth = 0; end = start
    for i in range(start, min(start+500000, len(text))):
        if text[i] == '[': depth += 1
        elif text[i] == ']':
            depth -= 1
            if depth == 0: end = i+1; break
    raw = text[start:end]
    raw = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1),16)), raw)
    raw = raw.replace('\\/', '/')
    raw = re.sub(r'\\([^"\\/bfnrtu])', r'\1', raw)
    try:
        items = json.loads(raw)
        for it in items[:3]:
            print(f"\n  {it.get('description','?')[:50]}")
            print(f"    price: {it.get('price')} (type {type(it.get('price')).__name__})")
            print(f"    reducedPrice: {it.get('reducedPrice')}")
            print(f"    isSale: {it.get('isSale')}")
            print(f"    priceLocalCurrency: {it.get('priceLocalCurrency')}")
            # dump ALL keys with 'price' in them
            price_keys = {k:v for k,v in it.items() if 'price' in k.lower()}
            print(f"    all price keys: {price_keys}")
        break
    except Exception as e:
        print(f"  parse error: {e}")

# ── Shopify: what does the URL field look like? ──
for name, base in [("MINT VELVET", "https://mintvelvet.com/en-ie"),
                   ("NOBODY'S CHILD", "https://www.nobodyschild.com/en-ie")]:
    print(f"\n{'=' * 60}")
    print(f"{name} — URL fields (suggest.json)")
    print(f"{'=' * 60}")
    try:
        r = session.get(f"{base}/search/suggest.json",
            params={"q": "blue", "resources[type]": "product", "resources[limit]": "5"})
        data = r.json()
        prods = data.get("resources", {}).get("results", {}).get("products", [])
        print(f"  {len(prods)} products")
        for pr in prods[:3]:
            print(f"\n  {pr.get('title','?')[:50]}")
            print(f"    url: {pr.get('url')}")
            print(f"    handle: {pr.get('handle')}")
            print(f"    price: {pr.get('price')}")
            # all keys
            print(f"    all keys: {list(pr.keys())}")
    except Exception as e:
        print(f"  error: {e}")

print(f"\n{'=' * 60}")
print("Done! Paste back to Claude.")
