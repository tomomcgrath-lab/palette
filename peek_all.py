"""Test ASOS fix + peek at M&S and River Island data."""
import re, json
from curl_cffi import requests

session = requests.Session(impersonate="chrome")

# ── Test ASOS fix ──
print("=" * 60)
print("ASOS — testing fix")
print("=" * 60)
r = session.get("https://www.asos.com/search/", params={"q": "women blue dress"})
for m in re.finditer(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL):
    text = m.group(1)
    if '"products"' not in text or len(text) < 5000:
        continue
    idx = text.find('"products":[')
    if idx < 0: continue
    start = idx + len('"products":')
    depth = 0
    end = start
    for i in range(start, min(start + 500000, len(text))):
        if text[i] == '[': depth += 1
        elif text[i] == ']':
            depth -= 1
            if depth == 0: end = i + 1; break
    try:
        items = json.loads(text[start:end])
        print(f"  Parsed {len(items)} products!")
        if items:
            p = items[0]
            print(f"  First: {p.get('description','?')[:60]}")
            print(f"  Price: {p.get('price')}, Brand: {p.get('brandName')}")
            print(f"  Image: {p.get('image','')[:80]}...")
        break
    except Exception as e:
        print(f"  Parse failed: {e}")

# ── Peek M&S ──
print(f"\n{'=' * 60}")
print("M&S — peeking at __NEXT_DATA__")
print("=" * 60)
r = session.get("https://www.marksandspencer.com/ie/l/women", params={"q": "blue"})
print(f"Status: {r.status_code}, Size: {len(r.text)}")
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    # Walk the tree looking for product-like arrays
    def find_products(d, path="", depth=0):
        if depth > 8: return
        if isinstance(d, list) and len(d) > 2:
            if isinstance(d[0], dict):
                keys = list(d[0].keys())
                if any(k in keys for k in ("name","title","price","productId","url")):
                    print(f"\n  FOUND at {path}: {len(d)} items")
                    print(f"  Keys: {keys[:15]}")
                    print(f"  First item (truncated):")
                    print(f"  {json.dumps(d[0], indent=2)[:600]}")
                    return
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, (dict, list)):
                    find_products(v, f"{path}.{k}", depth + 1)
    find_products(data)
else:
    print("  No __NEXT_DATA__ found")

# ── Peek River Island ──
print(f"\n{'=' * 60}")
print("River Island — peeking at data")
print("=" * 60)
r = session.get("https://www.riverisland.com/ie/c/women", params={"q": "blue"})
print(f"Status: {r.status_code}, Size: {len(r.text)}")
# Check for __NEXT_DATA__
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    find_products(data)
else:
    print("  No __NEXT_DATA__")
    # Look for products in any script
    for i, sm in enumerate(re.finditer(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)):
        text = sm.group(1)
        if '"products"' in text or '"items"' in text:
            if len(text) > 500:
                idx = text.find('"products"')
                if idx < 0: idx = text.find('"items"')
                chunk = text[max(0,idx):idx+1000]
                print(f"\n  Script {i} ({len(text)} chars):")
                print(f"  {chunk[:600]}")
                break
    # Also check HTML cards
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "lxml")
    cards = soup.select('article, [class*="product"], [class*="Product"]')
    if cards:
        c = cards[0]
        print(f"\n  First card: <{c.name} class='{' '.join(c.get('class',[]))}'>")
        print(f"  Inner HTML (first 500 chars):")
        print(f"  {str(c)[:500]}")

print("\nDone!")
