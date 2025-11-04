# 🐳 Docker Quick Start Guide

**Get ClickTok running on ANY computer in 3 simple steps!**

---

## Prerequisites

**Only one requirement:** Docker Desktop

- **Download:** https://www.docker.com/products/docker-desktop/
- **Supported:** Windows 10/11, macOS, Linux
- **Time:** ~10 minutes to install Docker

---

## Quick Start (3 Steps)

### Step 1: Install Docker

1. Download Docker Desktop from the link above
2. Install it (follow the installer prompts)
3. Start Docker Desktop
4. Wait for the Docker whale icon to appear in your system tray

### Step 2: Get ClickTok

```bash
# If you have git
git clone <your-repository-url>
cd ClickTok

# Or just download and extract the ClickTok folder
```

### Step 3: Run ClickTok

**Windows:** Double-click `docker-start.bat`

**Mac/Linux:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

**Or use Docker Compose directly:**
```bash
docker-compose up --build
```

**That's it!** 🎉

---

## What Happens Behind the Scenes?

When you run the command:

1. ✅ Docker downloads Python 3.11
2. ✅ Installs FFmpeg for video processing
3. ✅ Installs Playwright browsers
4. ✅ Installs all Python packages
5. ✅ Sets up the environment
6. ✅ Starts ClickTok

**First time:** 5-10 minutes (downloads everything)
**Next times:** ~10 seconds (everything cached)

---

## Common Commands

```bash
# Start ClickTok
docker-compose up

# Start in background
docker-compose up -d

# Stop ClickTok
docker-compose down

# View logs
docker-compose logs -f

# Restart after code changes
docker-compose restart

# Rebuild after changing requirements.txt
docker-compose up --build

# Run CLI mode
docker-compose run --rm clicktok-cli

# Access container shell
docker-compose exec clicktok bash
```

---

## Using the Makefile (Optional)

If you have `make` installed:

```bash
make up       # Start ClickTok
make down     # Stop ClickTok
make restart  # Restart
make logs     # View logs
make help     # See all commands
```

---

## Configuration

### Option 1: Use Example Credentials (Demo Mode)

No configuration needed! The app will use example credentials.

### Option 2: Add Your Credentials

1. Copy the example file:
   ```bash
   # Windows
   copy config\credentials.json.example config\credentials.json

   # Mac/Linux
   cp config/credentials.json.example config/credentials.json
   ```

2. Edit `config/credentials.json` with your actual API keys

3. Restart: `docker-compose restart`

### Option 3: Use GUI Settings

1. Start ClickTok with Docker
2. Go to the Settings tab in the GUI
3. Enter your credentials
4. They're automatically saved to `config/credentials.json`

---

## Hot-Reload Feature

**Edit code without rebuilding!**

When you edit files in these directories:
- `src/` - Python source code
- `gui/` - GUI components
- `config/` - Configuration
- `assets/` - Images, music, logos
- `main.py` - Entry point

**Just restart:**
```bash
docker-compose restart
```

No rebuild needed! ⚡

---

## Troubleshooting

### "Cannot connect to Docker daemon"

**Problem:** Docker is not running

**Solution:**
1. Start Docker Desktop
2. Wait for the whale icon in system tray
3. Try again

### "Port already in use"

**Problem:** Port 8080 is already taken

**Solution:**
Edit `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Changed from 8080 to 8081
```

### "No space left on device"

**Problem:** Docker is using too much disk space

**Solution:**
```bash
# Clean up unused images/containers
docker system prune -a

# Clean up volumes (⚠️ deletes data)
docker volume prune
```

### Changes not reflecting

**Problem:** Code changes not showing up

**Solution:**
```bash
# Restart container
docker-compose restart

# Or for dependency changes
docker-compose up --build
```

### Build fails

**Problem:** Docker build error

**Solution:**
1. Check your internet connection
2. Check Docker has enough disk space
3. View logs: `docker-compose logs`
4. Try rebuilding: `docker-compose build --no-cache`

---

## Verify Installation

Run the test script:

**Windows:** Double-click `docker-test.bat`

**Mac/Linux:**
```bash
chmod +x docker-test.sh
./docker-test.sh
```

This will check:
- ✅ Docker installed
- ✅ Docker running
- ✅ All files present
- ✅ Image builds correctly
- ✅ Dependencies installed

---

## File Locations

### Inside the Container:
- `/app/` - Application code
- `/app/data/` - Database and videos
- `/app/logs/` - Application logs
- `/app/config/` - Configuration files

### On Your Computer:
- `./src/` - Source code (synced to container)
- `./data/` - Data files (persistent)
- `./logs/` - Log files (persistent)
- `./config/` - Config files (synced to container)

---

## Production Deployment

### Option 1: Copy ClickTok Folder

1. Copy the entire ClickTok folder to another computer
2. Install Docker on that computer
3. Run `docker-compose up --build`
4. Done!

### Option 2: Docker Hub

```bash
# On your computer
docker tag clicktok yourusername/clicktok:latest
docker push yourusername/clicktok:latest

# On production server
docker pull yourusername/clicktok:latest
docker-compose up -d
```

### Option 3: Save/Transfer Image

```bash
# Save image to file
docker save clicktok:latest | gzip > clicktok.tar.gz

# Transfer file to another computer (USB, cloud, etc.)

# On the other computer
docker load < clicktok.tar.gz
docker-compose up -d
```

---

## Next Steps

1. **Start the app:**
   ```bash
   docker-compose up
   ```

2. **Open the GUI** and explore the features

3. **Configure your credentials** in Settings tab

4. **Test video generation** with demo products

5. **Read full docs:**
   - `DOCKER_README.md` - Complete Docker guide
   - `README.md` - Application documentation
   - `QUICK_START.md` - General quick start

---

## Why Docker Works Everywhere

Docker ensures 100% consistency because:

1. **Same Python version** on every computer (3.11)
2. **Same FFmpeg version** - no manual installation
3. **Same Playwright version** with browsers
4. **Same dependencies** - locked versions
5. **Same environment** - identical setup
6. **Isolated** - no conflicts with your system

**Result:** If it works on your computer, it works everywhere! ✅

---

## Support

**Need help?**

1. Check troubleshooting section above
2. View logs: `docker-compose logs -f`
3. Test setup: `./docker-test.sh` or `docker-test.bat`
4. Read full docs: `DOCKER_README.md`

**Still stuck?**

- Check Docker status: `docker info`
- Check disk space: `docker system df`
- Rebuild from scratch: `docker-compose build --no-cache`

---

## Summary

**To run ClickTok on ANY computer:**

1. ✅ Install Docker Desktop
2. ✅ Download ClickTok folder
3. ✅ Run `docker-compose up --build`

**That's it!** No Python installation, no FFmpeg setup, no dependency issues.

**Everything just works.** 🎉

---

**Quick Reference Card**

| I want to...          | Command                           |
|----------------------|-----------------------------------|
| Start ClickTok       | `docker-compose up`              |
| Stop ClickTok        | `docker-compose down`            |
| Restart              | `docker-compose restart`         |
| View logs            | `docker-compose logs -f`         |
| CLI mode             | `docker-compose run --rm clicktok-cli` |
| Update code          | Edit files → `docker-compose restart` |
| Add dependencies     | Edit requirements.txt → `docker-compose up --build` |
| Clean everything     | `docker-compose down -v`         |

---

**Version:** 1.0
**Last Updated:** November 2024
**Status:** ✅ Production Ready
