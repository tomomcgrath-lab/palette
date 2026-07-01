"""
Shared category detection.
Guesses a product category from its name/title.
Used by all scrapers so the frontend can filter by category.
"""

# Order matters — more specific keywords first
CATEGORY_KEYWORDS = [
    ("Dresses",   ["dress", "gown", "frock"]),
    ("Jumpsuits", ["jumpsuit", "playsuit", "romper", "unitard"]),
    ("Skirts",    ["skirt"]),
    ("Jeans",     ["jean", "denim"]),
    ("Trousers",  ["trouser", "pant", "chino", "legging", "jogger", "culotte"]),
    ("Shorts",    ["short"]),
    ("Knitwear",  ["jumper", "sweater", "cardigan", "knit", "pullover", "sweatshirt", "hoodie"]),
    ("Coats",     ["coat", "trench", "parka", "puffer", "mac ", "raincoat"]),
    ("Jackets",   ["jacket", "blazer", "gilet", "bomber", "anorak"]),
    ("Tops",      ["top", "shirt", "blouse", "tee", "t-shirt", "cami", "vest",
                   "bodysuit", "tank", "bralet", "corset", "camisole"]),
    ("Loungewear",["pyjama", "pajama", "nightie", "loungewear", "dressing gown",
                   "robe", "lounge"]),
    ("Swimwear",  ["swimsuit", "bikini", "swim", "beachwear", "tankini"]),
    ("Lingerie",  ["bra ", "bra,", "briefs", "knickers", "lingerie", "thong",
                   "underwear", "shapewear"]),
    ("Bags",      ["bag", "tote", "clutch", "backpack", "purse", "crossbody",
                   "satchel", "handbag"]),
    ("Shoes",     ["shoe", "boot", "trainer", "sandal", "heel", "loafer", "sneaker",
                   "flat", "pump", "slipper", "mule", "court shoe", "espadrille"]),
    ("Accessories",["scarf", "belt", "hat", "glove", "sunglasses", "jewellery",
                    "jewelry", "necklace", "earring", "bracelet", "sock", "tights",
                    "watch", "hair", "headband"]),
    ("Co-ords",   ["co-ord", "coord", "2 piece", "two piece", "set ", " set",
                   "matching set"]),
]


def guess_category(name: str) -> str:
    """Guess a product category from its name. Returns 'Other' if unknown."""
    if not name:
        return "Other"
    n = f" {name.lower()} "
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in n:
                return category
    return "Other"


# All categories in display order (for the frontend)
ALL_CATEGORIES = [
    "Dresses", "Tops", "Knitwear", "Trousers", "Jeans", "Skirts",
    "Shorts", "Jackets", "Coats", "Jumpsuits", "Co-ords",
    "Loungewear", "Swimwear", "Shoes", "Bags", "Accessories", "Other",
]
