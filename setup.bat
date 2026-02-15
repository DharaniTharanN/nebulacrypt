@echo off
echo ========================================
echo PDF Encryption System - Setup Script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo [OK] Python and Node.js found
echo.

REM Create virtual environment
if not exist "venv" (
    echo [STEP 1] Creating Python virtual environment...
    python -m venv venv
) else (
    echo [STEP 1] Virtual environment already exists
)

REM Activate and install dependencies
echo [STEP 2] Installing Python dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

REM Create .env if not exists
if not exist ".env" (
    echo [STEP 3] Creating .env file from template...
    copy .env.example .env
    echo [INFO] Please edit .env with your configuration
) else (
    echo [STEP 3] .env file already exists
)

REM Create media directory
if not exist "media\encrypted" (
    echo [STEP 4] Creating media directories...
    mkdir media\encrypted
) else (
    echo [STEP 4] Media directories exist
)

REM Run migrations
echo [STEP 5] Running database migrations...
python manage.py makemigrations accounts
python manage.py makemigrations encryption
python manage.py migrate

REM Install frontend dependencies
echo [STEP 6] Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env with your configuration
echo 2. Start MongoDB (if using local)
echo 3. Run: start_dev.bat
echo.
pause
