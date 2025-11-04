# 🚀 ClickTok Quick Deploy - One-Page Guide

**Deploy ClickTok on ANY computer in 3 steps!**

---

## Prerequisites

**Only 1 requirement:** Docker Desktop
- Download: https://www.docker.com/products/docker-desktop/
- Works on: Windows 10/11, macOS 10.15+, Linux

---

## 3-Step Deployment

### Step 1: Get ClickTok

**Option A - Git (Recommended):**
```bash
git clone <your-repo-url>
cd ClickTok
```

**Option B - Copy:**
- Copy entire ClickTok folder to target computer

---

### Step 2: Configure (Optional)

**For Demo Mode:** Skip this step!

**For Production:**
```bash
# Windows
copy config\credentials.json.example config\credentials.json
notepad config\credentials.json

# Mac/Linux
cp config/credentials.json.example config/credentials.json
nano config/credentials.json
```

---

### Step 3: Run

**Windows:**
- Double-click `docker-start.bat`

**Mac/Linux:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

**Or use Docker directly:**
```bash
docker-compose up --build
```

**First run:** 5-10 minutes (downloads everything)
**Next runs:** ~10 seconds

---

## Quick Commands

```bash
docker-compose up              # Start
docker-compose down            # Stop
docker-compose restart         # Restart
docker-compose logs -f         # View logs
docker-compose up --build      # Rebuild
```

---

## With Makefile (Optional)

```bash
make up        # Start
make down      # Stop
make restart   # Restart
make logs      # View logs
make test      # Test setup
make help      # Show all commands
```

---

## Verification

**Run test script:**
```bash
./docker-test.sh       # Mac/Linux
docker-test.bat        # Windows
```

**Manual check:**
```bash
docker --version       # Should show Docker version
docker info            # Should connect to daemon
docker-compose up      # Should start app
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Docker not found | Install Docker Desktop |
| Permission denied | `chmod +x *.sh` (Mac/Linux) |
| Port in use | Change port in `docker-compose.yml` |
| No space | `docker system prune -a` |
| Changes not reflecting | `docker-compose restart` |

---

## File Checklist

**Include these files:**
- ✅ `Dockerfile`
- ✅ `docker-compose.yml`
- ✅ `env.example`
- ✅ `config/credentials.json.example`
- ✅ All source code (`src/`, `gui/`)
- ✅ Scripts (`.bat`, `.sh`)
- ✅ Documentation (`.md` files)

**Exclude these:**
- ❌ `config/credentials.json` (secrets)
- ❌ `.env` (secrets)
- ❌ `data/` (generated data)
- ❌ `__pycache__/`
- ❌ `venv/`

---

## Deployment Methods

### Method 1: Git Clone
```bash
git clone <repo-url>
cd ClickTok
docker-compose up --build
```
**Time:** 5-10 min first run

### Method 2: Folder Copy
1. Copy ClickTok folder
2. Install Docker on target
3. Run `docker-start.bat` or `docker-start.sh`

**Time:** 5-10 min first run

### Method 3: Docker Image
```bash
# Save image
docker save clicktok:latest | gzip > clicktok.tar.gz

# Transfer to target computer

# Load on target
docker load < clicktok.tar.gz
docker-compose up
```
**Time:** Load ~2 min, run ~10 sec

---

## Environment Setup

### Option 1: Demo Mode
```bash
# No configuration needed!
docker-compose up
```

### Option 2: With Credentials
```bash
# Copy example
cp config/credentials.json.example config/credentials.json

# Edit with your keys
# Then run
docker-compose up
```

### Option 3: Environment File
```bash
cp env.example .env
# Edit .env with your keys
docker-compose up
```

---

## What Docker Guarantees

✅ Python 3.11 pre-installed
✅ FFmpeg pre-installed
✅ Playwright browsers pre-installed
✅ All dependencies installed
✅ Works on Windows, Mac, Linux
✅ No conflicts with host system
✅ Data persists across restarts
✅ Hot-reload for code changes

**Result: If it works once, it works everywhere!** 🌍

---

## Support

**Documentation:**
- `DEPLOY_ANYWHERE.md` - Complete deployment guide
- `DOCKER_QUICKSTART.md` - Docker quick start
- `DOCKER_README.md` - Full Docker guide
- `README.md` - Main documentation

**Check logs:**
```bash
docker-compose logs -f
```

**Test setup:**
```bash
./docker-test.sh       # Mac/Linux
docker-test.bat        # Windows
```

---

## Success Checklist

- [ ] Docker installed: `docker --version`
- [ ] Docker running: `docker info`
- [ ] Project files present
- [ ] Build succeeds: `docker-compose build`
- [ ] App starts: `docker-compose up`
- [ ] No errors in logs: `docker-compose logs`
- [ ] Can create test video
- [ ] Data persists after restart

**All checked? Deployment successful!** ✅

---

## Quick Reference

| I want to... | Command |
|-------------|---------|
| Start app | `docker-compose up` |
| Stop app | `docker-compose down` |
| Restart | `docker-compose restart` |
| View logs | `docker-compose logs -f` |
| Rebuild | `docker-compose up --build` |
| Test setup | `./docker-test.sh` |
| CLI mode | `docker-compose run --rm clicktok-cli` |
| Shell access | `docker-compose exec clicktok bash` |

---

**That's it! Print this page for quick reference.** 📄

**Version:** 1.0 | **Status:** ✅ Production Ready
