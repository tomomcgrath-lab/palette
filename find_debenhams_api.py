"""
Watch Debenhams' network traffic to find the API that returns search results.
This intercepts the background requests the page makes.
"""
import json
from playwright.sync_api import sync_playwright

captured = []

def handle_response(response):
    url = response.url
    # Look for API-like requests returning JSON
    if any(x in url.lower() for x in ["search", "product", "api", "catalog", "query", "graphql"]):
        ct = response.headers.get("content-type", "")
        if "json" in ct:
            captured.append({
                "url": url,
                "status": response.status,
                "type": ct,
            })

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        locale="en-IE",
    )
    page = context.new_page()
    page.on("response", handle_response)

    print("Loading Debenhams search for 'blue dress'...")
    page.goto("https://www.debenhams.ie/search/blue%20dress",
              wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)

    print(f"\nCaptured {len(captured)} JSON API requests:\n")
    for c in captured:
        print(f"  [{c['status']}] {c['url'][:120]}")

    # Try to fetch the most promising one and peek at structure
    print(f"\n{'=' * 55}")
    print("Now checking which returns product data...")
    for c in captured:
        if "search" in c["url"].lower() or "product" in c["url"].lower():
            try:
                # Re-fetch via the page context
                resp = page.request.get(c["url"])
                if resp.ok:
                    data = resp.json()
                    text = json.dumps(data)
                    if "price" in text.lower() and ("name" in text.lower() or "title" in text.lower()):
                        print(f"\n  PROMISING: {c['url'][:100]}")
                        print(f"  Keys: {list(data.keys())[:15] if isinstance(data, dict) else 'array'}")
                        print(f"  Preview: {text[:600]}")
            except Exception as e:
                pass

    browser.close()

print(f"\n{'=' * 55}")
print("Done! Paste output back to Claude.")
