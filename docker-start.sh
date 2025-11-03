#!/bin/bash
# ClickTok Docker Quick Start Script for Linux/Mac

set -e

echo "=========================================="
echo "  ClickTok Docker Quick Start"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo ""
    echo "Please start Docker and try again."
    exit 1
fi

echo "[OK] Docker is running"
echo ""

# Check if credentials.json exists
if [ ! -f "config/credentials.json" ]; then
    echo "[WARNING] config/credentials.json not found"
    if [ -f "config/credentials.json.example" ]; then
        echo "Creating credentials.json from example..."
        cp config/credentials.json.example config/credentials.json
        echo "[OK] Created. You can edit it later in the GUI."
    fi
    echo ""
fi

# Ask user which mode to run
echo "Select mode:"
echo "  1. GUI Mode (Default)"
echo "  2. CLI Mode"
echo "  3. Rebuild and Start (if you changed dependencies)"
echo "  4. Stop and Clean Up"
echo ""
read -p "Enter choice (1-4, default 1): " mode

mode=${mode:-1}

case $mode in
    1)
        echo ""
        echo "Starting ClickTok in GUI mode..."
        echo ""
        docker-compose up
        ;;
    2)
        echo ""
        echo "Starting ClickTok in CLI mode..."
        echo ""
        docker-compose run --rm clicktok-cli
        ;;
    3)
        echo ""
        echo "Rebuilding and starting ClickTok..."
        echo "This may take a few minutes..."
        echo ""
        docker-compose up --build
        ;;
    4)
        echo ""
        echo "Stopping and cleaning up..."
        docker-compose down
        echo ""
        echo "Done! Containers stopped."
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
