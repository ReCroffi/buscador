from app.scrapers.base import BaseStoreScraper, ScraperConfig


class GenericStoreScraper(BaseStoreScraper):
    def __init__(self, slug: str, name: str, base_url: str, search_path: str) -> None:
        super().__init__()
        self.config = ScraperConfig()
        self.config.slug = slug
        self.config.name = name
        self.config.base_url = base_url
        self.config.search_path = search_path
        self.config.product_selectors = (
            "article",
            "[data-testid*=product]",
            "[class*=product]",
            "[class*=card]",
            "li",
        )

    def parse_search(self, html: str, source_url: str):
        return self.generic_parse(html, source_url)

