@echo off
echo Starting PDF Encryption System...
echo.

REM Start Backend
echo [1/2] Starting Django Backend on port 8000...
start "Django Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python manage.py runserver"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Frontend
echo [2/2] Starting React Frontend on port 5173...
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo Servers Starting...
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Admin:    http://localhost:8000/admin
echo.
echo Press any key to exit (servers will keep running)
pause >nul
