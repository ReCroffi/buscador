import asyncio
import random
from abc import ABC, abstractmethod
from collections.abc import Sequence
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import quote_plus, urljoin

import httpx
import structlog
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from app.core.config import settings
from app.schemas.offer import ScrapedOffer

logger = structlog.get_logger(__name__)


class ScraperBlockedError(RuntimeError):
    pass


class ScraperConfig:
    slug: str
    name: str
    base_url: str
    search_path: str
    product_selectors: Sequence[str] = ()
    title_selectors: Sequence[str] = ("h2", "h3", "[data-testid*=title]", "a")
    price_selectors: Sequence[str] = (
        "[data-testid*=price]",
        ".price",
        ".preco",
        ".a-price-whole",
        "[class*=price]",
        "[class*=preco]",
    )
    image_selectors: Sequence[str] = ("img",)


def parse_brl(value: str | None) -> Decimal | None:
    if not value:
        return None
    cleaned = "".join(char for char in value if char.isdigit() or char in ",.")
    if not cleaned:
        return None
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


class BaseStoreScraper(ABC):
    config: ScraperConfig

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client

    @property
    def slug(self) -> str:
        return self.config.slug

    @property
    def name(self) -> str:
        return self.config.name

    def build_search_url(self, query: str) -> str:
        return urljoin(self.config.base_url, self.config.search_path.format(query=quote_plus(query)))

    async def search(self, query: str, limit: int = 12) -> list[ScrapedOffer]:
        url = self.build_search_url(query)
        html = await self.fetch(url)
        offers = self.parse_search(html, url)[:limit]
        logger.info("scraper.search.completed", store=self.slug, count=len(offers), query=query)
        return offers

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ScraperBlockedError)),
        wait=wait_exponential_jitter(initial=1, max=12),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def fetch(self, url: str) -> str:
        headers = self.headers()
        proxies = [str(proxy) for proxy in settings.proxy_urls]
        proxy = random.choice(proxies) if proxies else None
        close_client = self.client is None
        client = self.client or httpx.AsyncClient(
            timeout=settings.scrape_timeout_seconds,
            follow_redirects=True,
            proxy=proxy,
        )
        try:
            response = await client.get(url, headers=headers)
            if response.status_code in {403, 429, 503}:
                raise ScraperBlockedError(f"{self.slug} blocked status={response.status_code}")
            response.raise_for_status()
            return response.text
        finally:
            if close_client:
                await client.aclose()

    def headers(self) -> dict[str, str]:
        return {
            "User-Agent": settings.request_user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.7,en;q=0.6",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    @abstractmethod
    def parse_search(self, html: str, source_url: str) -> list[ScrapedOffer]:
        raise NotImplementedError

    def generic_parse(self, html: str, source_url: str) -> list[ScrapedOffer]:
        soup = BeautifulSoup(html, "html.parser")
        cards: list[Any] = []
        for selector in self.config.product_selectors:
            cards.extend(soup.select(selector))
        if not cards:
            cards = soup.select("article, li, div")

        offers: list[ScrapedOffer] = []
        seen: set[str] = set()
        for index, card in enumerate(cards[:80]):
            title = self.first_text(card, self.config.title_selectors)
            price = self.first_price(card, self.config.price_selectors)
            link = self.first_link(card, source_url)
            if not title or not price or not link:
                continue
            external_id = link.split("?")[0].rstrip("/").split("/")[-1] or f"{self.slug}-{index}"
            if external_id in seen:
                continue
            seen.add(external_id)
            shipping_text = card.get_text(" ", strip=True).lower()
            shipping = Decimal("0.00") if "frete gratis" in shipping_text or "frete grátis" in shipping_text else None
            offers.append(
                ScrapedOffer(
                    external_id=external_id,
                    store_slug=self.slug,
                    store=self.name,
                    title=title,
                    current_price=price,
                    pix_price=price,
                    shipping_price=shipping,
                    total_price=price + (shipping or Decimal("0.00")),
                    availability="available",
                    url=link,
                    image_url=self.first_image(card, source_url),
                    coupon_code=self.extract_coupon(card),
                    discount_percent=self.extract_discount(card),
                )
            )
        return offers

    @staticmethod
    def first_text(card, selectors: Sequence[str]) -> str | None:
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                text = element.get("title") or element.get("aria-label") or element.get_text(" ", strip=True)
                if text and len(text) > 6:
                    return text[:500]
        text = card.get_text(" ", strip=True)
        return text[:500] if len(text) > 12 else None

    @staticmethod
    def first_price(card, selectors: Sequence[str]) -> Decimal | None:
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                price = parse_brl(element.get_text(" ", strip=True))
                if price:
                    return price
        return parse_brl(card.get_text(" ", strip=True))

    @staticmethod
    def first_link(card, source_url: str) -> str | None:
        link = card if getattr(card, "name", "") == "a" else card.select_one("a[href]")
        href = link.get("href") if link else None
        return urljoin(source_url, href) if href else None

    @staticmethod
    def first_image(card, source_url: str) -> str | None:
        img = card.select_one("img")
        if not img:
            return None
        src = img.get("src") or img.get("data-src") or img.get("data-lazy")
        return urljoin(source_url, src) if src else None

    @staticmethod
    def extract_coupon(card) -> str | None:
        text = card.get_text(" ", strip=True)
        lowered = text.lower()
        if "cupom" not in lowered:
            return None
        parts = text.split()
        for part in parts:
            if part.isupper() and 4 <= len(part) <= 16:
                return part
        return "CUPOM"

    @staticmethod
    def extract_discount(card) -> Decimal | None:
        text = card.get_text(" ", strip=True)
        for piece in text.split():
            if "%" in piece:
                return parse_brl(piece)
        return None


class PlaywrightFallbackMixin:
    async def fetch_with_browser(self, url: str) -> str:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=settings.request_user_agent, locale="pt-BR")
            await page.goto(url, wait_until="domcontentloaded", timeout=int(settings.scrape_timeout_seconds * 1000))
            await page.wait_for_timeout(1200)
            html = await page.content()
            await browser.close()
            return html


async def run_scrapers(scrapers: Sequence[BaseStoreScraper], query: str, limit: int) -> list[ScrapedOffer]:
    semaphore = asyncio.Semaphore(settings.scrape_concurrency)

    async def guarded(scraper: BaseStoreScraper) -> list[ScrapedOffer]:
        async with semaphore:
            try:
                return await scraper.search(query, limit)
            except Exception as exc:
                logger.warning("scraper.search.failed", store=scraper.slug, error=str(exc))
                return []

    results = await asyncio.gather(*(guarded(scraper) for scraper in scrapers))
    return [offer for group in results for offer in group]
