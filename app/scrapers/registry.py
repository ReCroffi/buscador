from app.scrapers.amazon.scraper import AmazonScraper
from app.scrapers.generic.scraper import GenericStoreScraper
from app.scrapers.kabum.scraper import KabumScraper
from app.scrapers.mercadolivre.scraper import MercadoLivreScraper


def get_scrapers(store_slugs: list[str] | None = None):
    scrapers = [
        AmazonScraper(),
        MercadoLivreScraper(),
        KabumScraper(),
        GenericStoreScraper("pichau", "Pichau", "https://www.pichau.com.br", "/search?q={query}"),
        GenericStoreScraper("terabyte", "Terabyte", "https://www.terabyteshop.com.br", "/busca?str={query}"),
        GenericStoreScraper("magazineluiza", "Magazine Luiza", "https://www.magazineluiza.com.br", "/busca/{query}/"),
        GenericStoreScraper("casasbahia", "Casas Bahia", "https://www.casasbahia.com.br", "/{query}/b"),
        GenericStoreScraper("americanas", "Americanas", "https://www.americanas.com.br", "/busca/{query}"),
        GenericStoreScraper("aliexpress", "AliExpress", "https://pt.aliexpress.com", "/w/wholesale-{query}.html"),
        GenericStoreScraper("shopee", "Shopee", "https://shopee.com.br", "/search?keyword={query}"),
        GenericStoreScraper("carrefour", "Carrefour", "https://www.carrefour.com.br", "/busca/{query}"),
        GenericStoreScraper("fastshop", "Fast Shop", "https://www.fastshop.com.br", "/web/s/?q={query}"),
    ]
    if store_slugs:
        allowed = set(store_slugs)
        return [scraper for scraper in scrapers if scraper.slug in allowed]
    return scrapers


STORE_SEED = [
    {"slug": scraper.slug, "name": scraper.name, "base_url": scraper.config.base_url}
    for scraper in get_scrapers()
]

