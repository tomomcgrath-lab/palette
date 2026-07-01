"""Map Very.ie JSON structure to locate products."""
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

# Walk the whole tree and report any list of dicts, with their keys
def walk(d, path=""):
    if isinstance(d, dict):
        for k, v in d.items():
            walk(v, f"{path}.{k}")
    elif isinstance(d, list):
        if d and isinstance(d[0], dict):
            keys = list(d[0].keys())
            # Only report lists that look product-ish or sizeable
            if len(d) >= 2:
                print(f"{path}  [{len(d)} items]")
                print(f"    keys: {keys[:20]}")
        for i, item in enumerate(d[:2]):
            walk(item, f"{path}[{i}]")

walk(data)
print("\nDone! Paste back to Claude.")
