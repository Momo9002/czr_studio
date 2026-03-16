"""
WhatsApp conversation handler — Aura onboarding AI agent via Telnyx.
Uses google.genai (new SDK).
"""
import os
import json
import re
import httpx
from google import genai
from google.genai import types as genai_types
from api.leads import save_lead
from api.notify import notify_amaury

# In-memory conversation history keyed by sender phone number
_conversations: dict[str, list] = {}

SYSTEM_PROMPT = """
You are the onboarding agent for Aura Web Studio — a boutique AI-powered web agency
that delivers haute couture websites in 48 hours. You are the first point of contact.

Your mission: have a warm, natural conversation that qualifies the lead and captures
their contact details + project brief.

Tone: confident, warm, editorial. Think luxury concierge. NOT a chatbot.
Language: match the user's language (French if they write French, English by default).

Flow:
1. Greet warmly, ask what brings them here
2. Understand their business and what kind of site they need (2-3 exchanges max)
3. Ask about timeline and budget signal ("do you have a rough budget in mind?")
4. Once you understand the project, say you'd like to prepare a tailored brief
   and ask: "Could I get your name and email to put this together for you?"
5. Once you have name + email: confirm, say Amaury will follow up within 2 hours,
   and output this special tag on its own line (the system will detect and save it):
   [LEAD_CAPTURED] {"name": "...", "email": "...", "brief": "..."}

Rules:
- Max 2-3 sentences per reply. WhatsApp messages must be SHORT.
- Never mention you're an AI unless directly asked. If asked, say:
  "I'm the Aura agent — here to make the briefing process effortless."
- Never quote prices until you understand the project. When asked:
  "Our packages start from €999 — but once I understand your project,
  I can point you to the right fit."
- Always make the next step feel easy and obvious.
"""


async def handle_inbound_message(payload: dict):
    """Process inbound Telnyx WhatsApp webhook."""
    try:
        data = payload.get("data", {})
        event_type = data.get("event_type", "")

        if event_type != "message.received":
            return

        attrs = data.get("payload", {})
        from_number = attrs.get("from", {}).get("phone_number", "")
        message_text = attrs.get("text", "")
        to_number = attrs.get("to", [{}])[0].get("phone_number", "")

        if not from_number or not message_text:
            return

        print(f"📩 Inbound WA from {from_number}: {message_text[:60]}")

        history = _conversations.get(from_number, [])

        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

        contents = list(history) + [
            genai_types.Content(role="user", parts=[genai_types.Part(text=message_text)])
        ]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        reply_text = response.text.strip()

        # Update history
        history.append(genai_types.Content(role="user", parts=[genai_types.Part(text=message_text)]))
        history.append(genai_types.Content(role="model", parts=[genai_types.Part(text=reply_text)]))
        _conversations[from_number] = history

        # Detect lead capture
        if "[LEAD_CAPTURED]" in reply_text:
            await _handle_lead_capture(reply_text, from_number)
            reply_text = reply_text.split("[LEAD_CAPTURED]")[0].strip()

        await send_whatsapp_reply(from_number, to_number, reply_text)

    except Exception as e:
        print(f"❌ WhatsApp handler error: {e}")


async def _handle_lead_capture(text: str, phone: str):
    """Extract and save lead when agent captures it."""
    try:
        match = re.search(r'\[LEAD_CAPTURED\]\s*(\{.*?\})', text, re.DOTALL)
        if not match:
            return
        data = json.loads(match.group(1))
        data["phone"] = phone
        data["source"] = "whatsapp"
        save_lead(data)
        await notify_amaury(data)
        print(f"✅ Lead captured: {data.get('name')} — {data.get('email')}")
    except Exception as e:
        print(f"❌ Lead capture error: {e}")


async def send_whatsapp_reply(to: str, from_number: str, text: str):
    """Send a WhatsApp message via Telnyx API."""
    api_key = os.environ.get("TELNYX_API_KEY", "")
    if not api_key:
        print("⚠️  TELNYX_API_KEY not set — skipping reply send")
        return

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.telnyx.com/v2/messages",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_number,
                "to": to,
                "text": text,
                "messaging_profile_id": os.environ.get("TELNYX_MESSAGING_PROFILE_ID", ""),
            },
            timeout=10,
        )
        if resp.status_code not in (200, 202):
            print(f"❌ Telnyx send error {resp.status_code}: {resp.text[:200]}")
        else:
            print(f"📤 Reply sent to {to}")
