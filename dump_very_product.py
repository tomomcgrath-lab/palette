"""Dump a full Very.ie product to see stock + colour fields."""
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
raw = re.sub(r':\s*undefined', ': null', raw)
raw = re.sub(r':\s*NaN', ': null', raw)
data = json.loads(raw)

products = data["queryState"]["queries"][0]["state"]["data"]["products"]
print(f"Total products: {len(products)}\n")

# Full dump of first 2 products
for p in products[:2]:
    print("=" * 60)
    print(json.dumps(p, indent=2, default=str)[:2500])
    print()

print("Done! Paste back to Claude.")
