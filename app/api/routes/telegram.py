from fastapi import APIRouter, Request

from app.notifications.telegram import TelegramNotifier

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    message = update.get("message", {})
    text = message.get("text", "")
    chat_id = str(message.get("chat", {}).get("id", ""))
    if not chat_id:
        return {"ok": True}
    notifier = TelegramNotifier()
    if text.startswith("/status"):
        await notifier.send_message(chat_id, "Monitor online. Use /add pelo dashboard para criar alertas detalhados.")
    elif text.startswith("/list"):
        await notifier.send_message(chat_id, "A listagem completa fica disponivel no dashboard em /alerts.")
    elif text.startswith("/add"):
        await notifier.send_message(chat_id, "Envie o produto e preco alvo pelo dashboard ou API POST /alerts.")
    elif text.startswith("/remove"):
        await notifier.send_message(chat_id, "Remova ou pause alertas pelo dashboard ou API PATCH /alerts/{id}.")
    else:
        await notifier.send_message(chat_id, "Comandos: /add, /list, /remove, /status")
    return {"ok": True}

