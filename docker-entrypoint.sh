#!/bin/bash
# Docker Entrypoint Script for AI Therapist
# Handles GPU detection and application startup

set -e

echo "=========================================="
echo "AI Therapist Container Startup"
echo "=========================================="
echo ""

# Detect and log GPU status
echo "Detecting GPU configuration..."
python -c "
from backend.gpu_detector import log_gpu_status
log_gpu_status()
" || echo "Warning: GPU detection failed, continuing with defaults"

echo ""
echo "=========================================="
echo "Starting FastAPI Server"
echo "=========================================="
echo ""

# Get port from environment or default to 8000
PORT=${PORT:-8000}

# Start the application
exec uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"
