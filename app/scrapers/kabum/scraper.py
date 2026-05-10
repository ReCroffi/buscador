from app.scrapers.base import BaseStoreScraper, PlaywrightFallbackMixin, ScraperConfig


class KabumScraper(PlaywrightFallbackMixin, BaseStoreScraper):
    config = ScraperConfig()
    config.slug = "kabum"
    config.name = "KaBuM!"
    config.base_url = "https://www.kabum.com.br"
    config.search_path = "/busca/{query}"
    config.product_selectors = ("article", "[data-testid='product-card']")
    config.title_selectors = ("span[class*=nameCard]", "[data-testid='product-card-name']", "h3")
    config.price_selectors = ("span[class*=priceCard]", "[data-testid='price']", "[class*=price]")

    async def search(self, query: str, limit: int = 12):
        try:
            return await super().search(query, limit)
        except Exception:
            html = await self.fetch_with_browser(self.build_search_url(query))
            return self.parse_search(html, self.build_search_url(query))[:limit]

    def parse_search(self, html: str, source_url: str):
        return self.generic_parse(html, source_url)

