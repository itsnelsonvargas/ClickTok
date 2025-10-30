#!/bin/bash
# ClickTok - macOS/Linux Setup Script
# One-command installation for Unix systems

# Change to the directory where this script is located
cd "$(dirname "$0")"

echo ""
echo "============================================================"
echo "  ClickTok - Automated Setup for macOS/Linux"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo ""
    echo "Please install Python 3.8+ first:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt install python3"
    echo ""
    exit 1
fi

echo "[OK] Python is installed"
echo ""

# Check if setup.py exists
if [ ! -f "setup.py" ]; then
    echo "[ERROR] setup.py not found in current directory"
    echo "Current directory: $(pwd)"
    echo ""
    exit 1
fi

# Run the Python setup script
echo "Starting installation..."
echo ""
python3 "$(dirname "$0")/setup.py"

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Setup failed. See error messages above."
    exit 1
fi

echo ""
echo "============================================================"
echo "Setup complete! ClickTok is ready to use."
echo ""
echo "To launch: python3 main.py"
echo "============================================================"
echo ""
