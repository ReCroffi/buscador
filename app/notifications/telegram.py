from decimal import Decimal

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TelegramNotifier:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or settings.telegram_bot_token

    async def send_message(self, chat_id: str, text: str) -> None:
        if not self.token:
            logger.warning("telegram.disabled")
            return
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False},
            )
            response.raise_for_status()

    async def send_price_alert(
        self,
        chat_id: str,
        product: str,
        store: str,
        current_price: Decimal,
        target_price: Decimal,
        url: str,
    ) -> None:
        text = (
            "<b>PRECO BAIXOU!</b>\n\n"
            f"Produto: {product}\n"
            f"Loja: {store}\n"
            f"Preco atual: R$ {current_price:,.2f}\n"
            f"Meta: R$ {target_price:,.2f}\n\n"
            f"Link: {url}"
        )
        await self.send_message(chat_id, text)

