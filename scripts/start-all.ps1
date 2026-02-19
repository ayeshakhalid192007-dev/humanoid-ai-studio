# Start All Services Script (PowerShell)
# Starts auth server, backend API, and frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Physical AI Platform - Start All" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Check Node.js
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Host "ERROR: Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host "  Node.js: $nodeVersion" -ForegroundColor Green

# Check Python
$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Host "WARNING: Python not found. Backend will not start." -ForegroundColor Yellow
} else {
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start Auth Server (Port 3002)
Write-Host "[1/3] Starting Auth Server (port 3002)..." -ForegroundColor Cyan
$authPath = Join-Path $ProjectRoot "auth-server"
if (-not (Test-Path (Join-Path $authPath "node_modules"))) {
    Write-Host "  Installing auth server dependencies..." -ForegroundColor Gray
    Push-Location $authPath
    npm install
    Pop-Location
}
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd /d `"$authPath`" && npm run dev" -WindowStyle Minimized
Write-Host "  Auth Server starting..." -ForegroundColor Green

Start-Sleep -Seconds 2

# Start Backend API (Port 8000)
Write-Host "[2/3] Starting Backend API (port 8000)..." -ForegroundColor Cyan
$backendPath = Join-Path $ProjectRoot "backend"
if ($pythonVersion) {
    Start-Process -FilePath "cmd" -ArgumentList "/c", "cd /d `"$backendPath`" && python -m uvicorn main:app --reload --port 8000" -WindowStyle Minimized
    Write-Host "  Backend API starting..." -ForegroundColor Green
} else {
    Write-Host "  Backend API skipped (Python not found)" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# Start Frontend (Port 3000)
Write-Host "[3/3] Starting Frontend (port 3000)..." -ForegroundColor Cyan
$frontendPath = Join-Path $ProjectRoot "book"
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "  Installing frontend dependencies..." -ForegroundColor Gray
    Push-Location $frontendPath
    npm install
    Pop-Location
}
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd /d `"$frontendPath`" && npm start" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All services starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  - Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "  - Auth Server: http://localhost:3002" -ForegroundColor White
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop services." -ForegroundColor Gray
