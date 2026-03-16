"""
Aura Web Studio — WhatsApp Onboarding Agent
FastAPI webhook for Telnyx WhatsApp messages.

How this works:
1. Client messages your Telnyx WhatsApp number
2. Telnyx POSTs to POST /webhook/whatsapp on this server
3. AuraOnboardingAgent (Gemini) responds and qualifies the lead
4. When lead is captured → saves to leads.db + notifies Amaury via Telegram (Momo)

Setup:
- Set env vars: GOOGLE_API_KEY, TELNYX_API_KEY, MOMO_TELEGRAM_TOKEN, MOMO_CHAT_ID
- Run: uvicorn api.main:app --host 0.0.0.0 --port 8901 --reload
- Expose via ngrok or Cloudflare Tunnel, set webhook URL in Telnyx portal
"""

from pathlib import Path
from dotenv import load_dotenv

# Load .env from api/ directory
load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import os

from api.whatsapp import handle_inbound_message
from api.leads import init_db

app = FastAPI(title="Aura Web Studio API", version="1.0")

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Aura API started — leads DB ready")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "aura-web-studio-api"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Telnyx WhatsApp inbound webhook.
    Telnyx sends a JSON payload when a message arrives on your number.
    """
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    # Process in background so Telnyx gets 200 immediately (required)
    background_tasks.add_task(handle_inbound_message, payload)
    return JSONResponse(status_code=200, content={"received": True})

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8901, reload=True)
