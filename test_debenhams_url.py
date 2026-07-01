"""Find the URL format that actually filters Debenhams by search term."""
from playwright.sync_api import sync_playwright

# Try different search URL patterns
URLS = [
    ("path style", "https://www.debenhams.ie/search/blue%20dress"),
    ("query param q", "https://www.debenhams.ie/search?q=blue+dress"),
    ("query param term", "https://www.debenhams.ie/search?searchTerm=blue+dress"),
    ("query param query", "https://www.debenhams.ie/search?query=blue+dress"),
    ("women category", "https://www.debenhams.ie/womens?q=blue"),
    ("path womens dress", "https://www.debenhams.ie/search/womens%20blue%20dress"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        locale="en-IE",
    )
    page = context.new_page()

    for label, url in URLS:
        print(f"\n{'=' * 55}")
        print(f"{label}: {url}")
        print(f"{'=' * 55}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(3500)
            cards = page.query_selector_all('a[href*="/product/"]')
            print(f"  Products found: {len(cards)}")
            # Show first 5 product names to check if they match the search
            for card in cards[:5]:
                text = card.evaluate("e => e.textContent.trim()")[:70]
                print(f"    {text}")
        except Exception as e:
            print(f"  ERROR: {str(e)[:80]}")

    browser.close()

print(f"\n{'=' * 55}")
print("Done! Look for which URL returns BLUE DRESSES specifically.")
print("Paste output back to Claude.")
