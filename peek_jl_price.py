"""Peek at John Lewis price structure."""
import re, json
from curl_cffi import requests

r = requests.get("https://www.johnlewis.com/search",
                 params={"search-term": "women blue dress"}, impersonate="chrome")
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
data = json.loads(m.group(1))
products = data["props"]["pageProps"]["productListingData"]["products"]

p = products[0]
print("Full first product JSON:")
print(json.dumps(p, indent=2, default=str)[:2000])
