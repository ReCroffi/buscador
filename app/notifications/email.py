import smtplib
from decimal import Decimal
from email.message import EmailMessage

import anyio
import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = structlog.get_logger(__name__)
env = Environment(loader=FileSystemLoader("app/templates"), autoescape=select_autoescape())


class EmailNotifier:
    async def send_price_alert(
        self,
        to_email: str,
        product: str,
        store: str,
        current_price: Decimal,
        target_price: Decimal,
        url: str,
    ) -> None:
        if not settings.smtp_host or not settings.smtp_from_email:
            logger.warning("email.disabled")
            return
        html = env.get_template("emails/price_alert.html").render(
            product=product, store=store, current_price=current_price, target_price=target_price, url=url
        )
        message = EmailMessage()
        message["Subject"] = f"Preco baixou: {product}"
        message["From"] = str(settings.smtp_from_email)
        message["To"] = to_email
        message.set_content(f"Preco baixou para R$ {current_price}. Link: {url}")
        message.add_alternative(html, subtype="html")
        await anyio.to_thread.run_sync(self._send, message)

    @staticmethod
    def _send(message: EmailMessage) -> None:
        if settings.smtp_host is None:
            return
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_tls:
                smtp.starttls()
            if settings.smtp_user and settings.smtp_password:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
