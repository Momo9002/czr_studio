@echo off
REM ============================================================
REM  CZR Studio — Full Stack Startup (Windows)
REM  Double-click or: .\start_czr.bat
REM ============================================================

echo.
echo  ♞  CZR STUDIO — Starting Services
echo.

cd /d "%~dp0"

REM ── Check .env ─────────────────────────────────────────────
if not exist "api\.env" (
    echo [SETUP] Creating api\.env from example...
    copy api\.env.example api\.env
    echo.
    echo   Edit api\.env and fill in your API keys.
    echo   Then re-run this script.
    pause
    exit /b
)

REM ── Load env ───────────────────────────────────────────────
for /f "usebackq tokens=* delims=" %%a in (`findstr /v "^#" api\.env ^| findstr /v "^$"`) do set "%%a"

REM ── Install dependencies ───────────────────────────────────
echo [1/3] Installing Python dependencies...
python -m pip install -r requirements.txt --quiet

REM ── Start FastAPI server ───────────────────────────────────
echo [2/3] Starting CZR API server on port 8901...
start "CZR API" cmd /k "python -m uvicorn api.main:app --host 0.0.0.0 --port 8901 --reload"
timeout /t 3 /nobreak >nul

REM ── Start Cloudflare Tunnel ────────────────────────────────
echo [3/3] Starting Cloudflare Tunnel...

where cloudflared >nul 2>&1
if errorlevel 1 (
    echo [SETUP] cloudflared not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    echo [OK] cloudflared downloaded.
)

echo.
echo   ============================================================
echo    CZR Studio API starting...
echo.
echo    API:        http://localhost:8901
echo    Tunnel:     https://api.czr.studio
echo.
echo    Webhooks:
echo      Stripe:   https://api.czr.studio/webhook/stripe
echo      WhatsApp: https://api.czr.studio/webhook/whatsapp
echo   ============================================================
echo.

start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8901 run czr-api"

echo.
echo  ✅ All services started. Keep this window open.
pause
