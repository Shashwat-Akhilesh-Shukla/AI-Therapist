#!/bin/bash
set -e

echo "🚀 Starting AI Therapist Application..."

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Start FastAPI backend
echo "📡 Starting FastAPI backend on port 8000..."
cd /app
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1 &
BACKEND_PID=$!

# Wait a bit for backend to initialize
sleep 3

# Start Next.js frontend
echo "🎨 Starting Next.js frontend on port 3000..."
cd /app/frontend
npm start &
FRONTEND_PID=$!

echo "✅ Both services started successfully!"
echo "   - Backend API: http://0.0.0.0:8000"
echo "   - Frontend: http://0.0.0.0:3000"
echo "   - Health Check: http://0.0.0.0:8000/health"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
