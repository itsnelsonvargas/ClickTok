#!/bin/bash
# ClickTok Docker Entrypoint Script
# Handles initialization and setup before starting the app

set -e

echo "=========================================="
echo "  ClickTok Docker Container Starting"
echo "=========================================="

# Function to check if directory exists and create if not
ensure_directory() {
    if [ ! -d "$1" ]; then
        echo "Creating directory: $1"
        mkdir -p "$1"
    fi
}

# Create necessary directories
echo "Ensuring directories exist..."
ensure_directory "/app/data"
ensure_directory "/app/data/videos"
ensure_directory "/app/data/database"
ensure_directory "/app/logs"
ensure_directory "/app/config"
ensure_directory "/app/assets"
ensure_directory "/app/assets/music"

# Check if credentials.json exists
if [ ! -f "/app/config/credentials.json" ]; then
    echo "⚠️  Warning: config/credentials.json not found"
    if [ -f "/app/config/credentials.json.example" ]; then
        echo "Creating credentials.json from example..."
        cp /app/config/credentials.json.example /app/config/credentials.json
        echo "✅ Created. Please edit config/credentials.json with your credentials"
    else
        echo "Creating empty credentials.json..."
        echo '{}' > /app/config/credentials.json
    fi
fi

# Check FFmpeg installation
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg installed: $(ffmpeg -version | head -n 1)"
else
    echo "⚠️  FFmpeg not found (required for video creation)"
fi

# Check Playwright browsers
if [ -d "$HOME/.cache/ms-playwright" ]; then
    echo "✅ Playwright browsers installed"
else
    echo "Installing Playwright browsers..."
    playwright install chromium
fi

# Display environment info
echo ""
echo "Environment Information:"
echo "  Python: $(python --version)"
echo "  Working Directory: $(pwd)"
echo "  User: $(whoami)"
echo ""

echo "=========================================="
echo "  Starting ClickTok Application"
echo "=========================================="
echo ""

# Execute the main command
exec "$@"
