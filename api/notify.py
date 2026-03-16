"""
Notify Amaury via Momo (Telegram) when a new lead is captured.
"""
import os
import httpx


async def notify_amaury(lead: dict):
    """Send a Telegram message to Amaury via Momo bot."""
    token = os.environ.get("MOMO_TELEGRAM_TOKEN", "")
    chat_id = os.environ.get("MOMO_CHAT_ID", "")

    if not token or not chat_id:
        print("⚠️  MOMO_TELEGRAM_TOKEN or MOMO_CHAT_ID not set — skipping Telegram notify")
        return

    name = lead.get("name", "Unknown")
    email = lead.get("email", "—")
    phone = lead.get("phone", "—")
    brief = lead.get("brief", "—")[:300]

    message = (
        f"🔥 *New Aura Lead!*\n\n"
        f"👤 *Name:* {name}\n"
        f"📧 *Email:* {email}\n"
        f"📱 *Phone:* {phone}\n\n"
        f"💡 *Brief:*\n{brief}\n\n"
        f"→ _Reply within 2 hours_ 🚀"
    )

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
        if resp.status_code == 200:
            print(f"📬 Telegram notification sent to Amaury")
        else:
            print(f"❌ Telegram notify error: {resp.status_code}")
