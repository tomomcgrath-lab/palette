"""
Palette — Configuration
Colour palette, size mappings, and source definitions.
Add new colours or sources here.
"""

# ──────────────────────────────────────────────
# COLOUR PALETTE
# Each colour has:
#   - name: display name shown in the app
#   - hex: representative hex for the UI swatch
#   - neutral: whether it's a wardrobe neutral
#   - group: visual family for filtering (blues/pinks/purples/greens/earth/whites)
#   - search_terms: list of synonyms to search on retailer sites
#     (more terms = better recall, but may pull in false positives;
#      the scraper cross-checks results against these terms)
# ──────────────────────────────────────────────

COLOURS = [
    # ── Blues ──
    {
        "name": "Charcoal",
        "hex": "#36454F",
        "neutral": True,
        "group": "blues",
        "search_terms": ["charcoal", "dark grey", "dark gray", "anthracite"],
    },
    {
        "name": "Light Navy",
        "hex": "#4E5D73",
        "neutral": True,
        "group": "blues",
        "search_terms": ["light navy", "steel blue", "slate blue", "blue grey"],
    },
    {
        "name": "Charcoal Blue",
        "hex": "#3B4F5C",
        "neutral": True,
        "group": "blues",
        "search_terms": ["charcoal blue", "blue gray", "blue grey", "petrol blue"],
    },
    {
        "name": "Light Periwinkle",
        "hex": "#C5CBE3",
        "neutral": False,
        "group": "blues",
        "search_terms": ["periwinkle", "light periwinkle", "lavender blue", "pale blue"],
    },
    {
        "name": "Sapphire",
        "hex": "#0F52BA",
        "neutral": False,
        "group": "blues",
        "search_terms": ["sapphire", "royal blue", "cobalt", "bright blue"],
    },
    {
        "name": "Sky Blue",
        "hex": "#87CEEB",
        "neutral": False,
        "group": "blues",
        "search_terms": ["sky blue", "baby blue", "light blue", "powder blue"],
    },
    {
        "name": "Bluebell",
        "hex": "#6B7DB3",
        "neutral": False,
        "group": "blues",
        "search_terms": ["bluebell", "cornflower", "cornflower blue", "mid blue"],
    },
    # ── Pinks & Reds ──
    {
        "name": "Rose",
        "hex": "#C98B8B",
        "neutral": False,
        "group": "pinks",
        "search_terms": ["rose", "dusty rose", "old rose", "dusky pink", "muted pink"],
    },
    {
        "name": "Soft Fuchsia",
        "hex": "#C85A8A",
        "neutral": False,
        "group": "pinks",
        "search_terms": ["fuchsia", "hot pink", "magenta", "bright pink"],
    },
    {
        "name": "Geranium",
        "hex": "#D73B3E",
        "neutral": False,
        "group": "pinks",
        "search_terms": ["geranium", "red", "poppy red", "scarlet", "bright red"],
    },
    {
        "name": "Claret",
        "hex": "#7F1734",
        "neutral": False,
        "group": "pinks",
        "search_terms": ["claret", "burgundy", "wine", "maroon", "oxblood", "bordeaux"],
    },
    {
        "name": "Blush Pink",
        "hex": "#F4C2C2",
        "neutral": False,
        "group": "pinks",
        "search_terms": ["blush", "blush pink", "pale pink", "light pink", "pastel pink"],
    },
    # ── Purples ──
    {
        "name": "Orchid",
        "hex": "#DA70D6",
        "neutral": False,
        "group": "purples",
        "search_terms": ["orchid", "pink purple", "violet pink", "bright violet"],
    },
    {
        "name": "Amethyst",
        "hex": "#9966CC",
        "neutral": False,
        "group": "purples",
        "search_terms": ["amethyst", "medium purple", "purple", "violet"],
    },
    {
        "name": "Icy Violet",
        "hex": "#C4B7D4",
        "neutral": False,
        "group": "purples",
        "search_terms": ["icy violet", "light violet", "lilac", "lavender", "pale purple"],
    },
    {
        "name": "Soft Violet",
        "hex": "#9B7DB8",
        "neutral": False,
        "group": "purples",
        "search_terms": ["soft violet", "violet", "mauve", "wisteria"],
    },
    {
        "name": "Purple",
        "hex": "#7B2D8E",
        "neutral": False,
        "group": "purples",
        "search_terms": ["purple", "deep purple", "plum", "imperial purple"],
    },
    {
        "name": "Damson",
        "hex": "#5B2C6F",
        "neutral": True,
        "group": "purples",
        "search_terms": ["damson", "dark purple", "aubergine", "eggplant", "blackberry"],
    },
    # ── Earth tones ──
    {
        "name": "Cocoa",
        "hex": "#6B4226",
        "neutral": True,
        "group": "earth",
        "search_terms": ["cocoa", "chocolate", "dark brown", "brown"],
    },
    {
        "name": "Taupe",
        "hex": "#B3A494",
        "neutral": True,
        "group": "earth",
        "search_terms": ["taupe", "mushroom", "greige", "warm grey"],
    },
    {
        "name": "Stone",
        "hex": "#928E85",
        "neutral": True,
        "group": "earth",
        "search_terms": ["stone", "grey", "gray", "mid grey"],
    },
    {
        "name": "Rose Brown",
        "hex": "#8E6B5A",
        "neutral": True,
        "group": "earth",
        "search_terms": ["rose brown", "mocha", "mink", "dusky brown"],
    },
    {
        "name": "Pewter",
        "hex": "#8E9196",
        "neutral": True,
        "group": "earth",
        "search_terms": ["pewter", "silver grey", "gunmetal", "silver gray"],
    },
    # ── Whites ──
    {
        "name": "Shell",
        "hex": "#F5E6D3",
        "neutral": False,
        "group": "whites",
        "search_terms": ["shell", "cream", "nude", "ecru", "sand"],
    },
    {
        "name": "Ivory",
        "hex": "#FFFFF0",
        "neutral": False,
        "group": "whites",
        "search_terms": ["ivory", "off white", "off-white", "cream white"],
    },
    {
        "name": "Soft White",
        "hex": "#F5F5F0",
        "neutral": False,
        "group": "whites",
        "search_terms": ["white", "soft white", "off white", "bright white"],
    },
    # ── Greens ──
    {
        "name": "Spruce",
        "hex": "#2C5545",
        "neutral": True,
        "group": "greens",
        "search_terms": ["spruce", "forest green", "dark green", "pine green", "bottle green"],
    },
    {
        "name": "Teal",
        "hex": "#008080",
        "neutral": True,
        "group": "greens",
        "search_terms": ["teal", "dark teal", "blue green", "deep teal"],
    },
    {
        "name": "Sage",
        "hex": "#9CAF88",
        "neutral": False,
        "group": "greens",
        "search_terms": ["sage", "sage green", "khaki green", "muted green"],
    },
    {
        "name": "Grey Green",
        "hex": "#7A8B7A",
        "neutral": True,
        "group": "greens",
        "search_terms": ["grey green", "gray green", "olive", "moss", "green grey"],
    },
]

# Quick lookup: colour name → colour dict
COLOUR_MAP = {c["name"]: c for c in COLOURS}

# Flat set of all search terms (lowercased) for quick matching
ALL_SEARCH_TERMS = {}
for c in COLOURS:
    for term in c["search_terms"]:
        ALL_SEARCH_TERMS[term.lower()] = c["name"]


def match_colour(product_colour_text: str) -> str | None:
    """
    Given a colour string from a retailer (e.g. 'Dark Navy Blue'),
    return the palette colour name it matches, or None.
    Uses fuzzy substring matching against all search terms.
    """
    text = product_colour_text.lower().strip()
    # Direct match first
    if text in ALL_SEARCH_TERMS:
        return ALL_SEARCH_TERMS[text]
    # Substring match — check if any search term appears in the product colour
    for term, colour_name in ALL_SEARCH_TERMS.items():
        if term in text or text in term:
            return colour_name
    return None


# ──────────────────────────────────────────────
# SIZE MAPPING
# UK Medium women's = UK 10-12
# Each source maps differently; define acceptable size values per source.
# ──────────────────────────────────────────────

SIZE_CONFIG = {
    "target_uk": "M",
    "target_uk_numeric": [10, 12],
    "mappings": {
        "uk": ["M", "10", "12", "10-12"],
        "us": ["S", "M", "6", "8", "6-8"],
        "eu": ["38", "40", "S", "M"],
        "au": ["10", "12", "M"],
    },
}


# ──────────────────────────────────────────────
# SOURCE DEFINITIONS
# Add new retailers here. Each source needs a matching
# scraper module in scraper/sources/.
# ──────────────────────────────────────────────

SOURCES = {
    "asos": {
        "name": "ASOS",
        "base_url": "https://www.asos.com",
        "currency": "EUR",
        "enabled": True,
        "size_schema": "uk",
    },
    "very": {
        "name": "Very",
        "base_url": "https://www.very.ie",
        "currency": "EUR",
        "enabled": True,
        "size_schema": "uk",
    },
    "mintvelvet": {
        "name": "Mint Velvet",
        "base_url": "https://mintvelvet.com/en-ie",
        "currency": "EUR",
        "enabled": True,
        "size_schema": "uk",
    },
    "nobodyschild": {
        "name": "Nobody's Child",
        "base_url": "https://www.nobodyschild.com/en-ie",
        "currency": "EUR",
        "enabled": True,
        "size_schema": "uk",
    },
    "marksandspencer": {
        "name": "M&S",
        "base_url": "https://www.marksandspencer.com/ie",
        "currency": "EUR",
        "enabled": False,  # TODO: search page doesn't filter by query
        "size_schema": "uk",
    },
    "riverisland": {
        "name": "River Island",
        "base_url": "https://www.riverisland.com/ie",
        "currency": "EUR",
        "enabled": False,
        "size_schema": "uk",
    },
    "sezane": {
        "name": "Sézane",
        "base_url": "https://www.sezane.com/us-en",
        "currency": "EUR",
        "enabled": False,  # TODO: needs Playwright (full JS rendering)
        "size_schema": "us",
    },
"johnlewis": {
        "name": "John Lewis",
        "base_url": "https://www.johnlewis.com",
        "currency": "GBP",
        "enabled": True,
        "size_schema": "uk",
    },
}


# ──────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────

OUTPUT_DIR = "data"
OUTPUT_FILE = "products.json"
MAX_PRODUCTS_PER_SOURCE = 200  # cap to keep the JSON manageable
