#!/bin/bash
# Conditional PyTorch Installation Script
# Installs CUDA-enabled PyTorch if GPU is available, otherwise CPU-only version

set -e

echo "=========================================="
echo "PyTorch Installation Script"
echo "=========================================="
echo ""

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected"
    nvidia-smi --query-gpu=name --format=csv,noheader || true
    echo ""
    echo "Installing PyTorch with CUDA 11.8 support..."
    pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu118
    echo "✓ PyTorch (CUDA) installed successfully"
else
    echo "ℹ No NVIDIA GPU detected"
    echo ""
    echo "Installing PyTorch (CPU-only)..."
    pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu
    echo "✓ PyTorch (CPU) installed successfully"
fi

echo ""
echo "Verifying PyTorch installation..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

echo ""
echo "=========================================="
echo "PyTorch installation complete!"
echo "=========================================="
