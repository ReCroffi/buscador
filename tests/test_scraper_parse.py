from app.scrapers.kabum.scraper import KabumScraper


def test_generic_parser_extracts_offer() -> None:
    html = """
    <article>
      <a href="/produto/rtx-5070-ti-asus-tuf"><h3>RTX 5070 TI ASUS TUF 16GB</h3></a>
      <span class="price">R$ 4.899,90</span>
      <img src="/img.jpg" />
    </article>
    """
    offers = KabumScraper().parse_search(html, "https://www.kabum.com.br/busca/rtx")
    assert len(offers) == 1
    assert offers[0].current_price is not None
    assert offers[0].store_slug == "kabum"

