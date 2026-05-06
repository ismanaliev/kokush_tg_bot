@echo off
REM Quick start script for KG Hostel TMA setup
REM This script sets up the project for local development

echo.
echo ========================================
echo KG Hostel TMA - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
) else (
    echo [1/5] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Install Python dependencies
echo [2/5] Installing Python dependencies...
pip install -r requirements.txt

REM Setup frontend
echo [3/5] Setting up frontend...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
    npm install @twa-dev/sdk
)
cd ..

REM Create .env if it doesn't exist
if not exist ".env" (
    echo [4/5] Creating .env file from template...
    copy .env.example .env
    echo.
    echo NOTE: Update .env file with your actual values:
    echo   - API_TOKEN: Your Telegram bot token
    echo   - ADMIN_CHAT_ID: Your admin Telegram ID
    echo   - DATABASE_URL: Your PostgreSQL connection string
    echo   - FRONTEND_URL: Your deployed frontend URL (for production)
)

echo [5/5] Setup complete!
echo.
echo ========================================
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run: python bot.py (Terminal 1)
echo 3. Run: python -m uvicorn backend.main:app --reload (Terminal 2)
echo 4. Run: cd frontend && npm run dev (Terminal 3)
echo.
echo Visit http://localhost:3000 in browser
echo Then test your bot on Telegram
echo ========================================
echo.

pause
