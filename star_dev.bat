@echo off
chcp 65001 >nul

echo =========================================
echo    Starting CPAS Development Environment...
echo =========================================

REM Lock working directory to batch file location
cd /d "%~dp0"

REM 1. Start Python FastAPI Server (Port 8000)
echo [1/3] Starting Python FastAPI (Port 8000)...
start "Python-FastAPI" cmd /k "cd python_api && python -m uvicorn main:app --reload"

REM 2. Start Laravel Server (Port 8001)
echo [2/3] Starting Laravel Backend (Port 8001)...
start "Laravel-Backend" cmd /k "php artisan serve --port 8001"

REM 3. Start Vite Frontend (Port 5173)
echo [3/3] Starting Vite Frontend (Port 5173)...
start "Vite-Frontend" cmd /k "npm run dev"

REM Wait 5 seconds using ping (avoids timeout redirection errors)
echo Waiting for servers to warm up...
ping 127.0.0.1 -n 6 >nul

REM 4. Open Browser
echo Opening browser...
start http://127.0.0.1:8001/index

echo =========================================
echo    All services launched successfully!
echo =========================================
pause
