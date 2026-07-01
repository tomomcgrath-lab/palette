"""Quick look at what ASOS product data actually looks like."""
import re, json
from curl_cffi import requests

r = requests.get("https://www.asos.com/search/",
                  params={"q": "women blue dress"}, impersonate="chrome")
print(f"Page size: {len(r.text)} bytes")

# Find the big script with product data
for i, m in enumerate(re.finditer(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)):
    text = m.group(1)
    if '"products"' not in text or len(text) < 1000:
        continue
    print(f"\nScript block {i}: {len(text)} chars")

    # Show a chunk around "products"
    idx = text.find('"products"')
    if idx >= 0:
        # Get 2000 chars starting from "products"
        chunk = text[idx:idx+2000]
        print(f"\nRaw text around 'products' key:\n{chunk[:1500]}")
        break
