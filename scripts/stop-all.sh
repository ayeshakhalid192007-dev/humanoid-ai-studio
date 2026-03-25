#!/bin/bash
# Stop All Services Script (Linux/macOS)

echo "Stopping Physical AI Platform services..."

for PORT in 3000 3002 8000; do
  PID=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
  if [ -n "$PID" ]; then
    echo "  Stopping port $PORT (PID $PID)"
    kill "$PID" 2>/dev/null || true
  else
    echo "  Port $PORT: not running"
  fi
done

echo "Done."
