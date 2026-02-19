@echo off
REM Start All Services Script (Batch)
REM Starts auth server, backend API, and frontend

echo ========================================
echo   Physical AI Platform - Start All
echo ========================================
echo.

set PROJECT_ROOT=%~dp0..

echo Starting services in separate windows...
echo.

REM Start Auth Server (Port 3001)
echo [1/3] Starting Auth Server (port 3001)...
cd /d "%PROJECT_ROOT%\auth-server"
if not exist "node_modules" (
    echo   Installing auth server dependencies...
    call npm install
)
start "Auth Server" cmd /k "npm run dev"

timeout /t 3 /nobreak > nul

REM Start Backend API (Port 8000)
echo [2/3] Starting Backend API (port 8000)...
cd /d "%PROJECT_ROOT%\backend"
start "Backend API" cmd /k "python -m uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

REM Start Frontend (Port 3000)
echo [3/3] Starting Frontend (port 3000)...
cd /d "%PROJECT_ROOT%\book"
if not exist "node_modules" (
    echo   Installing frontend dependencies...
    call npm install
)
start "Frontend" cmd /k "npm start"

echo.
echo ========================================
echo   All services starting!
echo ========================================
echo.
echo Services:
echo   - Frontend:    http://localhost:3000
echo   - Auth Server: http://localhost:3001
echo   - Backend API: http://localhost:8000
echo.
echo Close each terminal window to stop services.
pause
