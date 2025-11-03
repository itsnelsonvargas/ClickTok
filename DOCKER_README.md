# ClickTok Docker Setup Guide

This guide explains how to run ClickTok using Docker, ensuring it works on any computer with 100% consistency.

## Why Docker?

- **Guaranteed deployment**: Works identically on any computer
- **No dependency issues**: All dependencies pre-installed in container
- **Automatic updates**: File changes reflect immediately (hot-reload)
- **Easy setup**: One command to get started
- **Isolation**: Doesn't interfere with your system

## Prerequisites

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop/
   - After installation, ensure Docker is running

2. **Docker Compose** (included with Docker Desktop)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Navigate to ClickTok directory
cd ClickTok

# Build and start the application
docker-compose up --build

# The app will start automatically!
```

### Option 2: Using Docker CLI

```bash
# Build the image
docker build -t clicktok .

# Run the container
docker run -it \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/gui:/app/gui \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  clicktok
```

## Docker Compose Commands

```bash
# Start the application (GUI mode)
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# Start CLI mode
docker-compose run --rm clicktok-cli

# Stop the application
docker-compose down

# Rebuild after Dockerfile changes
docker-compose up --build

# View logs
docker-compose logs -f

# Access container shell
docker-compose exec clicktok bash
```

## Hot-Reload Explained

The Docker setup includes **automatic hot-reload** for file changes:

### What's Mounted (Changes Reflect Immediately):
- ✅ `./src/` - All Python source code
- ✅ `./gui/` - GUI components
- ✅ `./config/` - Configuration files
- ✅ `./main.py` - Entry point
- ✅ `./assets/` - Images, music, logos

### What Changes Require Rebuild:
- ❌ `requirements.txt` - Python dependencies
- ❌ `Dockerfile` - Container configuration

When you change mounted files, just restart the container:
```bash
docker-compose restart
```

## Volume Persistence

Docker volumes ensure your data persists across container restarts:

```yaml
volumes:
  clicktok-data:    # Stores: database, videos, processed data
  clicktok-logs:    # Stores: application logs
```

To view volumes:
```bash
docker volume ls
```

To remove volumes (CAUTION - deletes data):
```bash
docker-compose down -v
```

## Configuration

### 1. Credentials Setup

Before running, configure your credentials:

```bash
# Copy the example file
cp config/credentials.json.example config/credentials.json

# Edit with your actual credentials
# (Use any text editor)
```

Or use the GUI Settings tab after starting.

### 2. Environment Variables

The `.env.example` file contains API keys and settings. Copy and configure:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### 3. Assets

Add your custom assets:
- Logo: Place in `assets/logo.png`
- Music: Add MP3 files to `assets/music/`

These changes reflect immediately without rebuild!

## Running Different Modes

### GUI Mode (Default)
```bash
docker-compose up
```

### CLI Mode
```bash
docker-compose run --rm clicktok-cli
```

### Custom Command
```bash
docker-compose run --rm clicktok python example_usage.py
```

### Interactive Shell
```bash
docker-compose run --rm clicktok bash
```

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"
**Solution**: Ensure Docker Desktop is running
```bash
# Check Docker status
docker ps
```

### Issue: "Port already in use"
**Solution**: Change port in docker-compose.yml
```yaml
ports:
  - "8081:8080"  # Changed from 8080 to 8081
```

### Issue: "Permission denied" on volumes
**Solution**: Fix file permissions
```bash
# Linux/Mac
chmod -R 755 ./src ./gui ./config

# Or run as root
docker-compose run --user root clicktok bash
```

### Issue: Changes not reflecting
**Solution**: Ensure volume mounts are correct
```bash
# Check mounts
docker-compose config

# Restart container
docker-compose restart
```

### Issue: Container keeps restarting
**Solution**: Check logs
```bash
docker-compose logs clicktok
```

### Issue: "No space left on device"
**Solution**: Clean up Docker
```bash
# Remove unused images/containers
docker system prune -a

# Remove unused volumes
docker volume prune
```

## Development Workflow

### Making Code Changes

1. **Edit files** on your host machine (VSCode, PyCharm, etc.)
2. **Changes sync** automatically to container
3. **Restart app** if needed:
   ```bash
   docker-compose restart
   ```

### Adding New Dependencies

1. **Update** `requirements.txt`
2. **Rebuild** the image:
   ```bash
   docker-compose up --build
   ```

### Testing Changes

```bash
# Run tests in container
docker-compose run --rm clicktok pytest

# Or access shell and run commands
docker-compose run --rm clicktok bash
python -m pytest
```

## Production Deployment

### Option 1: Docker Hub

```bash
# Build and tag
docker build -t yourusername/clicktok:latest .

# Push to Docker Hub
docker push yourusername/clicktok:latest

# On production server
docker pull yourusername/clicktok:latest
docker-compose up -d
```

### Option 2: Save/Load Image

```bash
# Save image to file
docker save clicktok:latest | gzip > clicktok-image.tar.gz

# Transfer to another computer
# Then load:
docker load < clicktok-image.tar.gz
docker-compose up
```

## File Structure (Docker-related)

```
ClickTok/
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Multi-container orchestration
├── .dockerignore             # Files to exclude from build
├── DOCKER_README.md          # This file
├── .env.example              # Environment variables template
├── config/
│   ├── credentials.json      # Your credentials (mounted)
│   └── settings.py           # App settings (mounted)
├── src/                      # Source code (mounted - hot reload)
├── gui/                      # GUI code (mounted - hot reload)
├── data/                     # Data volume (persisted)
├── logs/                     # Logs volume (persisted)
└── assets/                   # Assets (mounted - hot reload)
```

## Advanced Configuration

### Custom Docker Compose Override

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'
services:
  clicktok:
    environment:
      - DEBUG=true
    volumes:
      - ./custom-assets:/app/custom-assets
```

### Multi-stage Builds (Optimization)

For production, consider multi-stage builds to reduce image size:

```dockerfile
# Build stage
FROM python:3.11-slim AS builder
# ... build steps

# Production stage
FROM python:3.11-slim
COPY --from=builder /app /app
```

### GPU Support (Future)

For AI video processing with GPU:

```yaml
services:
  clicktok:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Security Best Practices

1. **Never commit** `config/credentials.json` or `.env`
2. **Use secrets** for production:
   ```bash
   docker secret create tiktok_password password.txt
   ```
3. **Run as non-root** (already configured in Dockerfile)
4. **Scan images** for vulnerabilities:
   ```bash
   docker scan clicktok:latest
   ```

## Performance Tips

1. **Use BuildKit** for faster builds:
   ```bash
   DOCKER_BUILDKIT=1 docker-compose build
   ```

2. **Cache dependencies** (already optimized in Dockerfile)

3. **Limit resources** if needed:
   ```yaml
   services:
     clicktok:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 4G
   ```

## 100% Deployment Guarantee

This Docker setup guarantees deployment because:

1. ✅ **FFmpeg pre-installed** - No manual installation needed
2. ✅ **Playwright browsers** - Chromium pre-installed
3. ✅ **All Python dependencies** - Locked versions in requirements.txt
4. ✅ **System dependencies** - All required libraries included
5. ✅ **Hot-reload enabled** - Changes sync automatically
6. ✅ **Data persistence** - Volumes preserve your work
7. ✅ **Isolated environment** - No conflicts with host system

## Continuous Integration (CI/CD)

### GitHub Actions Example

```yaml
name: Build Docker Image

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t clicktok .
      - name: Test
        run: docker run clicktok python -m pytest
```

## Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify Docker installation: `docker --version`
3. Check Docker disk space: `docker system df`
4. Review container status: `docker-compose ps`

## Summary

**To run ClickTok on any computer:**

```bash
# 1. Install Docker
# 2. Clone/copy ClickTok folder
# 3. Configure credentials
cp config/credentials.json.example config/credentials.json
# Edit credentials.json

# 4. Run!
docker-compose up --build

# Done! ✅
```

**That's it!** Docker handles everything else automatically.

---

## Quick Reference

| Task | Command |
|------|---------|
| Start app | `docker-compose up` |
| Stop app | `docker-compose down` |
| Rebuild | `docker-compose up --build` |
| View logs | `docker-compose logs -f` |
| CLI mode | `docker-compose run --rm clicktok-cli` |
| Shell access | `docker-compose exec clicktok bash` |
| Restart | `docker-compose restart` |
| Clean up | `docker-compose down -v` |

---

**Version**: 1.0
**Last Updated**: November 2024
**Tested On**: Docker 24.0+, Docker Compose 2.20+
