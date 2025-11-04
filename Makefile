# ClickTok Makefile
# Convenient commands for Docker operations
# Usage: make <command>

.PHONY: help build up down restart logs shell cli clean test verify

# Default target - show help
help:
	@echo "ClickTok Docker Commands"
	@echo "========================"
	@echo ""
	@echo "Quick Start:"
	@echo "  make up          - Start ClickTok (GUI mode)"
	@echo "  make build       - Build Docker image"
	@echo "  make down        - Stop ClickTok"
	@echo ""
	@echo "Development:"
	@echo "  make restart     - Restart the application"
	@echo "  make logs        - View application logs"
	@echo "  make shell       - Access container shell"
	@echo "  make cli         - Run in CLI mode"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Remove containers and volumes (⚠️ deletes data)"
	@echo "  make test        - Test Docker setup"
	@echo "  make verify      - Verify installation"
	@echo "  make rebuild     - Rebuild and start (after dependency changes)"
	@echo ""

# Build the Docker image
build:
	@echo "Building ClickTok Docker image..."
	docker-compose build

# Build and start the application
up:
	@echo "Starting ClickTok..."
	docker-compose up

# Build and start in background
up-bg:
	@echo "Starting ClickTok in background..."
	docker-compose up -d

# Rebuild and start (use after changing requirements.txt)
rebuild:
	@echo "Rebuilding and starting ClickTok..."
	docker-compose up --build

# Stop the application
down:
	@echo "Stopping ClickTok..."
	docker-compose down

# Restart the application (use after code changes)
restart:
	@echo "Restarting ClickTok..."
	docker-compose restart

# View logs
logs:
	@echo "Viewing ClickTok logs (Ctrl+C to exit)..."
	docker-compose logs -f

# Access container shell
shell:
	@echo "Opening shell in ClickTok container..."
	docker-compose exec clicktok bash

# Run in CLI mode
cli:
	@echo "Starting ClickTok CLI..."
	docker-compose run --rm clicktok-cli

# Clean up everything (⚠️ WARNING: Deletes all data and volumes)
clean:
	@echo "⚠️  WARNING: This will delete all data and volumes!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Cleaning up..."
	docker-compose down -v
	@echo "Done! All containers and volumes removed."

# Test the Docker setup
test:
	@echo "Testing Docker setup..."
	@echo ""
	@echo "1. Testing Python..."
	docker-compose run --rm clicktok python --version
	@echo ""
	@echo "2. Testing FFmpeg..."
	docker-compose run --rm clicktok ffmpeg -version | head -n 1
	@echo ""
	@echo "3. Testing Python packages..."
	docker-compose run --rm clicktok python -c "import moviepy, playwright, requests, bs4; print('✅ All dependencies OK')"
	@echo ""
	@echo "✅ Docker setup is working correctly!"

# Verify installation
verify:
	@echo "Verifying ClickTok installation..."
	@echo ""
	@echo "Checking Docker..."
	@docker --version || (echo "❌ Docker not found. Install from: https://docker.com" && exit 1)
	@docker-compose --version || (echo "❌ Docker Compose not found" && exit 1)
	@echo "✅ Docker installed"
	@echo ""
	@echo "Checking Docker daemon..."
	@docker info > /dev/null 2>&1 || (echo "❌ Docker is not running. Please start Docker Desktop." && exit 1)
	@echo "✅ Docker is running"
	@echo ""
	@echo "Checking files..."
	@test -f Dockerfile || (echo "❌ Dockerfile not found" && exit 1)
	@test -f docker-compose.yml || (echo "❌ docker-compose.yml not found" && exit 1)
	@echo "✅ All Docker files present"
	@echo ""
	@echo "✅ Everything looks good! Run 'make up' to start."

# Show running containers
ps:
	@echo "ClickTok containers:"
	docker-compose ps

# View Docker stats
stats:
	@echo "Docker resource usage:"
	docker stats --no-stream

# Pull latest changes and rebuild
update:
	@echo "Updating ClickTok..."
	git pull
	docker-compose up --build

# Initialize project (first time setup)
init:
	@echo "Initializing ClickTok..."
	@if [ ! -f config/credentials.json ]; then \
		echo "Creating credentials.json from example..."; \
		cp config/credentials.json.example config/credentials.json; \
		echo "✅ Created config/credentials.json"; \
	else \
		echo "✅ credentials.json already exists"; \
	fi
	@if [ ! -f .env ]; then \
		echo "Creating .env from example..."; \
		cp env.example .env; \
		echo "✅ Created .env file"; \
	else \
		echo "✅ .env already exists"; \
	fi
	@echo ""
	@echo "✅ Initialization complete!"
	@echo "Next: Run 'make up' to start ClickTok"

# Run a custom command in the container
run:
	@docker-compose run --rm clicktok $(cmd)

# Example: make run cmd="python example_usage.py"
