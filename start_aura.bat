@echo off
REM ============================================================
REM  Aura Web Studio — Full Stack Startup
REM  Run this on the PC to start everything.
REM  Double-click or: .\start_aura.bat
REM ============================================================

echo.
echo  ◈  AURA WEB STUDIO — Starting Services
echo.

REM ── 1. Check for .env ──────────────────────────────────────
if not exist "api\.env" (
    echo [SETUP] Creating api\.env from example...
    copy api\.env.example api\.env
    echo.
    echo  ^^! Edit api\.env and fill in your API keys before continuing.
    echo     GOOGLE_API_KEY, TELNYX_API_KEY, TELNYX_MESSAGING_PROFILE_ID
    echo     MOMO_TELEGRAM_TOKEN, MOMO_CHAT_ID
    echo.
    pause
)

REM ── 2. Load env vars ───────────────────────────────────────
for /f "usebackq tokens=1,2 delims==" %%A in ("api\.env") do (
    if not "%%A"=="" if not "%%A:~0,1%"=="#" set %%A=%%B
)

REM ── 3. Install dependencies ────────────────────────────────
echo [1/3] Installing Python dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is installed.
    pause & exit /b 1
)

REM ── 4. Start FastAPI server in background ──────────────────
echo [2/3] Starting Aura API server on port 8901...
start "Aura API" cmd /k "python -m uvicorn api.main:app --host 0.0.0.0 --port 8901 --reload"
timeout /t 3 /nobreak >nul

REM ── 5. Start Cloudflare Tunnel ─────────────────────────────
echo [3/3] Starting Cloudflare Tunnel...

where cloudflared >nul 2>&1
if errorlevel 1 (
    echo [SETUP] cloudflared not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    echo [OK] cloudflared downloaded.
)

echo.
echo  ============================================================
echo   Cloudflare Tunnel starting...
echo   Watch for a line like:
echo     https://xxxx-xxxx.trycloudflare.com
echo   Copy that URL into Telnyx Messaging > Webhooks
echo  ============================================================
echo.

start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8901"

echo.
echo  ◈  All services started. Check the two windows above.
echo  ◈  Paste the trycloudflare.com URL into Telnyx webhook settings.
echo.
pause
