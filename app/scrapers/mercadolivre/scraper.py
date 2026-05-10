from app.scrapers.base import BaseStoreScraper, ScraperConfig


class MercadoLivreScraper(BaseStoreScraper):
    config = ScraperConfig()
    config.slug = "mercadolivre"
    config.name = "Mercado Livre"
    config.base_url = "https://lista.mercadolivre.com.br"
    config.search_path = "/{query}"
    config.product_selectors = (".ui-search-result__wrapper", ".ui-search-layout__item")
    config.title_selectors = (".poly-component__title", ".ui-search-item__title", "h2")
    config.price_selectors = (".andes-money-amount__fraction", ".price-tag-fraction")

    def parse_search(self, html: str, source_url: str):
        return self.generic_parse(html, source_url)

