"""Check Very.ie fields — handles JS 'undefined' in the JSON."""
import re, json
from curl_cffi import requests

session = requests.Session(impersonate="chrome")
r = session.get("https://www.very.ie/e/q/women-blue.end", timeout=30)
html = r.text

key = "__product_listing_initial_state__"
idx = html.find(key)
eq = html.find("=", idx)
start = html.find("{", eq)
depth = 0; end = start; in_str = False; escape = False
for i in range(start, len(html)):
    c = html[i]
    if escape: escape = False; continue
    if c == "\\": escape = True; continue
    if c == '"': in_str = not in_str
    elif not in_str:
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: end = i+1; break
raw = html[start:end]

# Clean JS-isms that break JSON parsing
raw = re.sub(r':\s*undefined', ': null', raw)
raw = re.sub(r':\s*NaN', ': null', raw)

try:
    data = json.loads(raw)
    print("Parsed successfully!")
    def dig(d, depth=0):
        if depth > 15: return []
        if isinstance(d, list) and d and isinstance(d[0], dict):
            if any(k in d[0] for k in ("product_id","productId","id","name","title","sku")):
                return d
        if isinstance(d, dict):
            for v in d.values():
                if isinstance(v, (dict, list)):
                    res = dig(v, depth+1)
                    if res: return res
        return []
    products = dig(data)
    print(f"\nFound {len(products)} products\n")
    for p in products[:2]:
        print("=" * 55)
        print(f"Name: {str(p.get('name', p.get('title','?')))[:50]}")
        for k in p.keys():
            print(f"    {k}: {str(p[k])[:70]}")
        print()
except Exception as e:
    print(f"Still failing: {e}")
    print(f"Around error: {raw[max(0,100):250]}")

print("Done! Paste back to Claude.")
