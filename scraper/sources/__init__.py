"""Source Registry — all scrapers."""
from scraper.sources.asos import AsosScraper
from scraper.sources.very import VeryScraper
from scraper.sources.shopify import ShopifyScraper
from scraper.sources.marksandspencer import MarksAndSpencerScraper
from scraper.sources.riverisland import RiverIslandScraper
from scraper.sources.sezane import SezaneScraper
from scraper.sources.johnlewis import JohnLewisScraper
from scraper.sources.debenhams import DebenhamsScraper

SCRAPERS = {
    "asos": AsosScraper,
    "very": VeryScraper,
    "mintvelvet": ShopifyScraper,
    "nobodyschild": ShopifyScraper,
    "marksandspencer": MarksAndSpencerScraper,
    "riverisland": RiverIslandScraper,
    "sezane": SezaneScraper,
    "debenhams": DebenhamsScraper,
    "johnlewis": JohnLewisScraper,
}