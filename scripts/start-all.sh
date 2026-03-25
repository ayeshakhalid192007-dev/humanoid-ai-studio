#!/bin/bash
# Start All Services Script (Linux/macOS)
# Starts auth server, backend API, and frontend in background

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGS_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGS_DIR"

echo "========================================"
echo "  Physical AI Platform - Start All"
echo "========================================"
echo ""

# ── Prerequisite checks ──────────────────────────────────────────────────────
echo "Checking prerequisites..."

if ! command -v node &>/dev/null; then
  echo "ERROR: Node.js not found. Please install Node.js 18+."
  exit 1
fi
echo "  Node.js: $(node --version)"

if ! command -v python3 &>/dev/null; then
  echo "WARNING: python3 not found. Backend will not start."
  PYTHON_OK=0
else
  echo "  Python: $(python3 --version)"
  PYTHON_OK=1
fi

echo ""

# ── Kill any stale processes on our ports ────────────────────────────────────
for PORT in 3000 3002 8000; do
  PID=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
  if [ -n "$PID" ]; then
    echo "Stopping existing process on port $PORT (PID $PID)..."
    kill "$PID" 2>/dev/null || true
    sleep 1
  fi
done

# ── Auth Server (port 3002) ──────────────────────────────────────────────────
echo "[1/3] Starting Auth Server (port 3002)..."
cd "$PROJECT_ROOT/auth-server"
if [ ! -d "node_modules" ]; then
  echo "  Installing auth server dependencies..."
  npm install
fi
nohup npm run dev > "$LOGS_DIR/auth-server.log" 2>&1 &
AUTH_PID=$!
echo "  Auth Server PID: $AUTH_PID  (logs: logs/auth-server.log)"
sleep 2

# ── Backend API (port 8000) ──────────────────────────────────────────────────
if [ "$PYTHON_OK" -eq 1 ]; then
  echo "[2/3] Starting Backend API (port 8000)..."
  cd "$PROJECT_ROOT/backend"
  # Use venv python if available, fall back to system python3
  PYTHON_BIN="python3"
  if [ -f "$PROJECT_ROOT/backend/venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_ROOT/backend/venv/bin/python"
  fi
  nohup "$PYTHON_BIN" -m uvicorn main:app --host 0.0.0.0 --port 8000 > "$LOGS_DIR/backend.log" 2>&1 &
  BACKEND_PID=$!
  echo "  Backend API PID: $BACKEND_PID  (logs: logs/backend.log)"
  sleep 2
else
  echo "[2/3] Skipping Backend API (python3 not found)."
fi

# ── Frontend / Docusaurus (port 3000) ────────────────────────────────────────
echo "[3/3] Starting Frontend (port 3000)..."
cd "$PROJECT_ROOT/book"
if [ ! -d "node_modules" ]; then
  echo "  Installing frontend dependencies..."
  npm install
fi
nohup npm start > "$LOGS_DIR/book.log" 2>&1 &
BOOK_PID=$!
echo "  Frontend PID: $BOOK_PID  (logs: logs/book.log)"

# ── Wait and verify ──────────────────────────────────────────────────────────
echo ""
echo "Waiting for services to be ready..."
sleep 10

OK=1
for PORT in 3002 8000 3000; do
  if curl -s --max-time 3 "http://localhost:$PORT" > /dev/null 2>&1; then
    echo "  ✓ Port $PORT is responding"
  else
    echo "  ✗ Port $PORT not yet responding (may still be starting)"
    OK=0
  fi
done

echo ""
echo "========================================"
echo "  All services launched!"
echo "========================================"
echo ""
echo "  Frontend:    http://localhost:3000"
echo "  Auth Server: http://localhost:3002"
echo "  Backend API: http://localhost:8000"
echo ""
echo "  Logs: $LOGS_DIR/"
echo ""
echo "To stop all services, run:"
echo "  bash $PROJECT_ROOT/scripts/stop-all.sh"
echo ""
