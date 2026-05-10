from app.scrapers.base import BaseStoreScraper, ScraperConfig


class AmazonScraper(BaseStoreScraper):
    config = ScraperConfig()
    config.slug = "amazon"
    config.name = "Amazon"
    config.base_url = "https://www.amazon.com.br"
    config.search_path = "/s?k={query}"
    config.product_selectors = (
        "div[data-component-type='s-search-result']",
        "[data-asin][data-component-type]",
    )
    config.title_selectors = ("h2 span", "h2 a", "[data-cy='title-recipe'] span")
    config.price_selectors = (".a-price .a-offscreen", ".a-price-whole")

    def parse_search(self, html: str, source_url: str):
        return self.generic_parse(html, source_url)

