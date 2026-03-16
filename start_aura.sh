#!/bin/bash
# ============================================================
#  Aura Web Studio — Full Stack Startup (Linux/Mac version)
#  Run on the PC via SSH: bash start_aura.sh
# ============================================================

set -e

echo ""
echo "◈  AURA WEB STUDIO — Starting Services"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ── 1. Check .env ────────────────────────────────────────────
if [ ! -f "api/.env" ]; then
    echo "[SETUP] Creating api/.env from example..."
    cp api/.env.example api/.env
    echo ""
    echo "  ⚠️  Edit api/.env and fill in your API keys:"
    echo "     GOOGLE_API_KEY, TELNYX_API_KEY, TELNYX_MESSAGING_PROFILE_ID"
    echo "     MOMO_TELEGRAM_TOKEN, MOMO_CHAT_ID"
    echo ""
    echo "Then re-run this script."
    exit 1
fi

# Load env vars
export $(grep -v '^#' api/.env | xargs)

# ── 2. Install dependencies ──────────────────────────────────
echo "[1/3] Installing Python dependencies..."
python -m pip install -r requirements.txt --quiet

# ── 3. Start FastAPI server ──────────────────────────────────
echo "[2/3] Starting Aura API server on port 8901..."
uvicorn api.main:app --host 0.0.0.0 --port 8901 --reload &
API_PID=$!
echo "  ✅ API server PID: $API_PID"
sleep 2

# ── 4. Check health ──────────────────────────────────────────
if curl -s http://localhost:8901/health | grep -q "ok"; then
    echo "  ✅ API healthy"
else
    echo "  ❌ API not responding on port 8901"
    kill $API_PID 2>/dev/null
    exit 1
fi

# ── 5. Start Cloudflare Tunnel ───────────────────────────────
echo "[3/3] Starting Cloudflare Tunnel..."

if ! command -v cloudflared &>/dev/null; then
    echo "  cloudflared not found — installing..."
    # Windows (WSL) or Linux
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
    chmod +x cloudflared
    echo "  ✅ cloudflared installed"
    CLOUDFLARED="./cloudflared"
else
    CLOUDFLARED="cloudflared"
fi

echo ""
echo "  ============================================================"
echo "   Watch for a line like:"
echo "     https://xxxx-xxxx.trycloudflare.com"
echo "   Copy that URL → paste in Telnyx portal as webhook URL:"
echo "     https://xxxx-xxxx.trycloudflare.com/webhook/whatsapp"
echo "  ============================================================"
echo ""

$CLOUDFLARED tunnel --url http://localhost:8901
