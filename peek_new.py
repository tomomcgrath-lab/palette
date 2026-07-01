"""Peek at actual product fields for all new sources."""
import re, json, time
from curl_cffi import requests
from bs4 import BeautifulSoup

session = requests.Session(impersonate="chrome")

def show_first_product(name, url, extract_fn):
    print(f"\n{'=' * 60}")
    print(f"{name}")
    print(f"{'=' * 60}")
    try:
        resp = session.get(url, timeout=20)
        if resp.status_code != 200:
            print(f"  Status {resp.status_code}")
            return
        products = extract_fn(resp.text)
        if products:
            print(f"  Found {len(products)} products")
            p = products[0]
            if isinstance(p, dict):
                print(f"  Keys: {list(p.keys())[:15]}")
                print(f"  First product:")
                print(f"  {json.dumps(p, indent=2, default=str)[:800]}")
            else:
                print(f"  Type: {type(p)}")
                print(f"  {str(p)[:400]}")
        else:
            print("  No products found")
    except Exception as e:
        print(f"  ERROR: {e}")
    time.sleep(2)

# ── John Lewis ──
def extract_jl(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m: return []
    data = json.loads(m.group(1))
    try:
        return data["props"]["pageProps"]["productListingData"]["products"]
    except: pass
    return []

show_first_product("JOHN LEWIS",
    "https://www.johnlewis.com/search?search-term=blue+dress", extract_jl)

# ── Next.ie ──
def extract_next(html):
    m = re.search(r'ssrClientSettings\.plp\s*=\s*\{_STATE_:\s*(\{.*?\})\s*\}\s*;', html, re.DOTALL)
    if not m:
        m = re.search(r'ssrClientSettings\.plp\s*=\s*(\{.*?\})\s*;?\s*$', html, re.MULTILINE | re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            # dig for products
            def dig(d, depth=0):
                if depth > 10: return []
                if isinstance(d, list) and d and isinstance(d[0], dict):
                    if any(k in d[0] for k in ("id","name","title","price","Style")):
                        return d
                if isinstance(d, dict):
                    for v in d.values():
                        r = dig(v, depth+1)
                        if r: return r
                return []
            return dig(data)
        except:
            pass
    # Try broader approach
    for sm in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        text = sm.group(1)
        if 'ssrClientSettings' in text and '"products"' in text and len(text) > 10000:
            # Find products array
            idx = text.find('"products"')
            if idx > 0:
                chunk = text[idx:idx+3000]
                print(f"  Raw chunk around 'products': {chunk[:500]}...")
                break
    return []

show_first_product("NEXT.IE",
    "https://www.next.ie/en/search?w=blue+women", extract_next)

# ── Reiss ──
show_first_product("REISS",
    "https://www.reiss.com/search?q=blue", extract_next)  # same platform

# ── Debenhams ──
def extract_debenhams(html):
    m = re.search(r'window\.__remixContext\s*=\s*(\{.*?\});?\s*$', html, re.MULTILINE | re.DOTALL)
    if not m:
        m = re.search(r'__remixContext\s*=\s*(\{.+?\})\s*;', html, re.DOTALL)
    if m:
        try:
            raw = m.group(1)
            # This might be huge, try to parse
            data = json.loads(raw)
            def dig(d, depth=0):
                if depth > 12: return []
                if isinstance(d, list) and d and isinstance(d[0], dict):
                    if any(k in d[0] for k in ("id","name","title","price","productId")):
                        return d
                if isinstance(d, dict):
                    for k, v in d.items():
                        if isinstance(v, (dict, list)):
                            r = dig(v, depth+1)
                            if r: return r
                return []
            return dig(data)
        except Exception as e:
            print(f"  Remix parse error: {e}")
    return []

show_first_product("DEBENHAMS",
    "https://www.debenhams.ie/search/blue", extract_debenhams)

# ── H&M ──
def extract_hm(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m: return []
    try:
        data = json.loads(m.group(1))
        def dig(d, depth=0):
            if depth > 12: return []
            if isinstance(d, list) and len(d) > 3 and isinstance(d[0], dict):
                if any(k in d[0] for k in ("id","name","title","price","articleCode")):
                    return d
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, (dict, list)):
                        r = dig(v, depth+1)
                        if r: return r
            return []
        return dig(data)
    except:
        return []

show_first_product("H&M",
    "https://www2.hm.com/en_ie/ladies/shop-by-colour/blue.html", extract_hm)

# ── Brown Thomas ──
def extract_bt(html):
    soup = BeautifulSoup(html, "lxml")
    products = []
    tiles = soup.select('.grid-tile, .js-component-product-tile, [class*="product-tile"]')
    for tile in tiles[:3]:
        name_el = tile.select_one('[class*="product-name"], [class*="title"], h3, h2, a[class*="name"]')
        price_el = tile.select_one('[class*="price"], [class*="Price"]')
        link = tile.select_one('a[href]')
        img = tile.select_one('img[src], img[data-src]')

        name = name_el.get_text(strip=True) if name_el else ""
        price_text = price_el.get_text(strip=True) if price_el else ""
        href = link.get("href","") if link else ""
        img_src = (img.get("src") or img.get("data-src") or "") if img else ""

        if name:
            products.append({"name": name, "price": price_text, "url": href,
                           "image": img_src[:100], "tag": tile.name,
                           "classes": " ".join(tile.get("class",[]))[:80]})
    return products

show_first_product("BROWN THOMAS",
    "https://www.brownthomas.com/search?q=blue&lang=en_IE", extract_bt)

# ── Zara ──
def extract_zara(html):
    # Try __INITIAL_STATE__ or similar
    for pat in [r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
                r'"products"\s*:\s*(\[.*?\])',
                r'"productGroups"\s*:\s*(\[.*?\])']:
        m = re.search(pat, html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                if isinstance(data, list): return data[:3]
                if isinstance(data, dict):
                    def dig(d, depth=0):
                        if depth > 10: return []
                        if isinstance(d, list) and d and isinstance(d[0], dict):
                            return d[:3]
                        if isinstance(d, dict):
                            for v in d.values():
                                r = dig(v, depth+1)
                                if r: return r
                        return []
                    return dig(data)
            except:
                continue
    return []

show_first_product("ZARA",
    "https://www.zara.com/ie/en/search?searchTerm=blue", extract_zara)

print(f"\n{'=' * 60}")
print("Done!")
