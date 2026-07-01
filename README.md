# 🎨 Palette

A personal fashion curator that scrapes clothing sites daily, filters by a specific colour palette and size, and presents matching items in a beautiful browsable app.

Built as a gift — one person's colour palette, served fresh every morning.

## How it works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Scraper    │     │  products.   │     │   Frontend   │
│  (Python)    │────▶│   json       │────▶│   (React)    │
│  runs daily  │     │              │     │  static app  │
└──────────────┘     └──────────────┘     └──────────────┘
     │                                          │
     ▼                                          ▼
 ASOS, Very                              She browses here
 (+ more later)                          on her phone
```

1. **Daily scraper** queries each retailer for products in her colour terms
2. Filters by UK Medium (maps to US 6–8, EU 38–40 automatically)
3. Matches results against her 30-colour palette
4. Writes `data/products.json`
5. **Frontend** loads the JSON and presents a filterable, favouritable grid
6. Every card links directly to the product page to buy

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/palette.git
cd palette
pip install -r requirements.txt
```

### 2. Run the scraper locally

```bash
# Scrape all sources
python -m scraper.main

# Scrape only ASOS
python -m scraper.main --source asos

# Dry run (print results, don't save)
python -m scraper.main --dry-run --verbose
```

This creates `data/products.json` and an archived copy in `data/archive/`.

### 3. Deploy the frontend

The frontend is a single React component (`palette-app.jsx`). Deploy it to:

**Option A — Vercel (recommended, free)**
1. Push the repo to GitHub
2. Import to [vercel.com](https://vercel.com)
3. It auto-deploys on every push (including scraper commits)

**Option B — Netlify (also free)**
1. Push to GitHub
2. Import to [netlify.com](https://netlify.com)
3. Same auto-deploy behaviour

**Option C — GitHub Pages**
1. Build the React app: `npm run build`
2. Enable GitHub Pages in repo settings

### 4. Set up daily scraping

**Option A — GitHub Actions (recommended, free)**

Already configured in `.github/workflows/scrape.yml`. It runs at 7am UTC daily and commits results. Just push to GitHub and it works.

To trigger manually: go to Actions tab → "Daily Palette Scrape" → "Run workflow".

**Option B — Cron job on any server**

```bash
# Add to crontab (crontab -e)
0 7 * * * cd /path/to/palette && python -m scraper.main >> /var/log/palette.log 2>&1
```

**Option C — Raspberry Pi**

Same as cron, perfect for a low-power always-on setup.

## Adding a new retailer

1. Create `scraper/sources/yoursite.py`
2. Subclass `BaseScraper` and implement `search_products()`
3. Add the source config to `scraper/config.py` → `SOURCES`
4. Register the scraper in `scraper/sources/__init__.py`

Template:

```python
from scraper.sources.base import BaseScraper, Product

class YourSiteScraper(BaseScraper):
    def search_products(self) -> list[Product]:
        products = []
        # For each colour in COLOURS:
        #   1. Search the site
        #   2. Parse results
        #   3. Filter by size (self.size_matches())
        #   4. Match colour (self.colour_matches())
        #   5. Create Product instances
        return products
```

## Adding or modifying colours

Edit `scraper/config.py` → `COLOURS` list. Each colour needs:

```python
{
    "name": "Coral",              # Display name in the app
    "hex": "#FF6F61",             # Hex for the UI swatch
    "neutral": False,             # Is it a wardrobe neutral?
    "group": "pinks",             # Filter group
    "search_terms": ["coral"],    # What to search on retailer sites
}
```

The `search_terms` are critical — these are the words the scraper actually
sends to each retailer's search. Include synonyms retailers might use
(e.g. "burgundy", "wine", "maroon" for Claret).

## Size configuration

Currently set to **UK Medium women's** (UK 10–12, US 6–8, EU 38–40).

To change, edit `scraper/config.py` → `SIZE_CONFIG`. The scraper checks
each retailer's size values against the acceptable sizes for that
retailer's size schema.

## Colour palette (30 colours)

| Group | Colours |
|-------|---------|
| Blues | Charcoal · Light Navy · Charcoal Blue · Light Periwinkle · Sapphire · Sky Blue · Bluebell |
| Pinks | Rose · Soft Fuchsia · Geranium · Claret · Blush Pink |
| Purples | Orchid · Amethyst · Icy Violet · Soft Violet · Purple · Damson |
| Earth | Cocoa · Taupe · Stone · Rose Brown · Pewter |
| Whites | Shell · Ivory · Soft White |
| Greens | Spruce · Teal · Sage · Grey Green |

## Project structure

```
palette/
├── scraper/
│   ├── config.py              # Colours, sizes, sources
│   ├── main.py                # Runner (entry point)
│   └── sources/
│       ├── __init__.py        # Scraper registry
│       ├── base.py            # Base scraper class
│       ├── asos.py            # ASOS scraper
│       └── very.py            # Very.ie scraper
├── data/
│   ├── products.json          # Latest scrape (generated)
│   └── archive/               # Daily snapshots (generated)
├── palette-app.jsx            # Frontend React app
├── .github/workflows/
│   └── scrape.yml             # Daily GitHub Action
├── requirements.txt
└── README.md
```

## Troubleshooting

**Scraper returns 0 products**
- Retailers may block automated requests. Try increasing `REQUEST_DELAY` in `base.py`.
- The site's API or HTML structure may have changed. Inspect their network requests in DevTools and update the scraper accordingly.
- Run with `--verbose` to see debug output.

**Images not loading in the app**
- Some retailers use lazy-loading image URLs. Check the scraper is extracting the full image URL.
- CORS may block images from some CDNs. The app uses `<img>` tags which generally work cross-origin.

**GitHub Action isn't running**
- Check the Actions tab for errors.
- Ensure the repo has Actions enabled in Settings.
- The schedule cron runs on UTC time.
