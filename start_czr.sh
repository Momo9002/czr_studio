#!/bin/bash
# ============================================================
#  CZR Studio — Full Stack Startup
#  Starts: FastAPI server + Cloudflare Tunnel (api.czr.studio)
# ============================================================

set -e

echo ""
echo "♞  CZR STUDIO — Starting Services"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ── 1. Check .env ────────────────────────────────────────────
if [ ! -f "api/.env" ]; then
    echo "[SETUP] Creating api/.env from example..."
    cp api/.env.example api/.env
    echo ""
    echo "  ⚠️  Edit api/.env and fill in your API keys:"
    echo "     GOOGLE_API_KEY, STRIPE_SECRET_KEY, WA_ACCESS_TOKEN, etc."
    echo ""
    echo "Then re-run this script."
    exit 1
fi

# Load env vars
export $(grep -v '^#' api/.env | grep -v '^$' | xargs)

# ── 2. Install dependencies ──────────────────────────────────
echo "[1/3] Installing Python dependencies..."
pip install -r requirements.txt --quiet 2>/dev/null || python3 -m pip install -r requirements.txt --quiet

# ── 3. Start FastAPI server ──────────────────────────────────
echo "[2/3] Starting CZR API server on port 8901..."
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
    if [ -f "./cloudflared" ]; then
        CLOUDFLARED="./cloudflared"
    else
        echo "  cloudflared not found — installing..."
        curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
        chmod +x cloudflared
        echo "  ✅ cloudflared installed"
        CLOUDFLARED="./cloudflared"
    fi
else
    CLOUDFLARED="cloudflared"
fi

echo ""
echo "  ============================================================"
echo "   CZR Studio API starting..."
echo ""
echo "   API:        http://localhost:8901"
echo "   Tunnel:     https://api.czr.studio"
echo ""
echo "   Webhooks:"
echo "     Stripe:   https://api.czr.studio/webhook/stripe"
echo "     WhatsApp: https://api.czr.studio/webhook/whatsapp"
echo "  ============================================================"
echo ""

# Try named tunnel first, fall back to quick tunnel
if $CLOUDFLARED tunnel list 2>/dev/null | grep -q "czr-api"; then
    echo "  Using named tunnel: czr-api → api.czr.studio"
    $CLOUDFLARED tunnel --url http://localhost:8901 run czr-api
else
    echo "  Using quick tunnel (random URL — set up named tunnel for api.czr.studio)"
    echo "  Run these commands once to set up permanently:"
    echo "    $CLOUDFLARED tunnel login"
    echo "    $CLOUDFLARED tunnel create czr-api"
    echo "    $CLOUDFLARED tunnel route dns czr-api api.czr.studio"
    echo ""
    $CLOUDFLARED tunnel --url http://localhost:8901
fi
