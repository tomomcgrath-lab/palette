"""
Shared category detection + non-clothing filter.
Guesses a product category from its name, and flags junk to exclude.
"""

# Order matters — more specific keywords first
CATEGORY_KEYWORDS = [
    ("Dresses",   ["dress", "gown", "frock"]),
    ("Jumpsuits", ["jumpsuit", "playsuit", "romper", "unitard", "dungaree"]),
    ("Skirts",    ["skirt"]),
    ("Jeans",     ["jean", "denim"]),
    ("Trousers",  ["trouser", "pant", "chino", "legging", "jogger", "culotte"]),
    ("Shorts",    ["short"]),
    ("Knitwear",  ["jumper", "sweater", "cardigan", "knit", "pullover",
                   "sweatshirt", "hoodie"]),
    ("Coats",     ["coat", "trench", "parka", "puffer", "mac ", "raincoat"]),
    ("Jackets",   ["jacket", "blazer", "gilet", "bomber", "anorak"]),
    ("Tops",      ["top", "shirt", "blouse", "tee", "t-shirt", "cami", "vest",
                   "bodysuit", "tank", "bralet", "corset", "camisole"]),
    ("Loungewear",["pyjama", "pajama", "nightie", "loungewear", "dressing gown",
                   "robe", "lounge"]),
    ("Swimwear",  ["swimsuit", "bikini", "swim", "beachwear", "tankini"]),
    ("Lingerie",  ["bra ", "bra,", "bra-", "briefs", "knickers", "lingerie",
                   "thong", "underwear", "shapewear", "sports bra"]),
    ("Bags",      ["bag", "tote", "clutch", "backpack", "purse", "crossbody",
                   "satchel", "handbag"]),
    ("Shoes",     ["shoe", "boot", "trainer", "sandal", "heel", "loafer",
                   "sneaker", "ballet pump", "court shoe", "espadrille",
                   "slipper", "mule"]),
    ("Accessories",["scarf", "belt", "hat", "glove", "sunglasses", "jewellery",
                    "jewelry", "necklace", "earring", "bracelet", "sock",
                    "tights", "watch", "hair clip", "headband"]),
    ("Co-ords",   ["co-ord", "coord", "2 piece", "two piece", "matching set"]),
]

# Words that mean it's NOT clothing — drop these outright.
# (homeware, beauty, electronics, food, furniture, etc.)
EXCLUDE_KEYWORDS = [
    # homeware / bedding
    "pillow", "pillowcase", "duvet", "cushion", "blanket", "throw",
    "bedding", "sheet set", "towel", "curtain", "rug", "mattress",
    "shed", "storage", "furniture", "sofa", "chair", "table", "lamp",
    "candle", "diffuser", "vase", "mug", "plate", "bowl", "cutlery",
    "kettle", "toaster", "cookware", "saucepan", "frying pan",
    # beauty / grooming
    "perfume", "fragrance", "aftershave", "moisturiser", "moisturizer",
    "serum", "shampoo", "conditioner", "lipstick", "mascara", "foundation",
    "makeup", "make-up", "skincare", "cleanser",
    # tech / misc
    "headphone", "earbud", "charger", "speaker", "television", " tv ",
    "laptop", "tablet", "phone case", "smart watch", "fitbit",
    "toy", "game console", "playstation", "xbox",
    # baby gear (not baby clothes, but gear)
    "pram", "pushchair", "stroller", "cot ", "highchair",
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


def is_clothing(name: str) -> bool:
    """
    Return True if this looks like a fashion item we want to keep.
    Drops homeware, beauty, tech, and anything we can't categorise.
    """
    if not name:
        return False
    n = f" {name.lower()} "
    # Explicit exclusions first
    for kw in EXCLUDE_KEYWORDS:
        if kw in n:
            return False
    # Must land in a real fashion category (not "Other")
    return guess_category(name) != "Other"


ALL_CATEGORIES = [
    "Dresses", "Tops", "Knitwear", "Trousers", "Jeans", "Skirts",
    "Shorts", "Jackets", "Coats", "Jumpsuits", "Co-ords",
    "Loungewear", "Swimwear", "Lingerie", "Shoes", "Bags", "Accessories",
]
