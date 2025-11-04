# ✅ ClickTok Deployment Checklist

**Print this page and check off items as you go!**

---

## 📦 Pre-Deployment (Source Computer)

### Validate Project

- [ ] Run validation script
  ```bash
  ./validate-deploy.sh       # Mac/Linux
  validate-deploy.bat        # Windows
  ```

- [ ] All tests pass
- [ ] No errors reported

### Verify Files

- [ ] `Dockerfile` present
- [ ] `docker-compose.yml` present
- [ ] `requirements.txt` present
- [ ] `main.py` present
- [ ] All documentation present (`.md` files)
- [ ] Scripts present (`.sh` and `.bat` files)

### Check Security

- [ ] `config/credentials.json` has placeholder values only
- [ ] `.env` not present OR has placeholder values
- [ ] No real API keys in code
- [ ] `.gitignore` includes secrets
- [ ] Git status clean (no uncommitted changes)

### Test Locally

- [ ] `docker-compose build` succeeds
- [ ] `docker-compose up` starts application
- [ ] No errors in logs
- [ ] Can access GUI/CLI
- [ ] Can create test video
- [ ] Data persists after restart

---

## 🚀 Deployment (Choose Method)

### Method 1: Git Clone ⭐ Recommended

- [ ] Push all changes: `git push`
- [ ] On target: `git clone <repo-url>`
- [ ] On target: `cd ClickTok`
- [ ] On target: `docker-compose up --build`

### Method 2: Folder Transfer

- [ ] Copy entire ClickTok folder
- [ ] Transfer via USB/cloud/network
- [ ] On target: Navigate to folder
- [ ] On target: Run `docker-start.bat` or `./docker-start.sh`

### Method 3: Docker Image

- [ ] Build: `docker-compose build`
- [ ] Save: `docker save clicktok:latest | gzip > clicktok.tar.gz`
- [ ] Transfer `clicktok.tar.gz` to target
- [ ] On target: `docker load < clicktok.tar.gz`
- [ ] On target: `docker-compose up`

---

## 🖥️ Target Computer Setup

### Install Docker

- [ ] Download Docker Desktop from https://docker.com
- [ ] Install Docker Desktop
- [ ] Start Docker Desktop
- [ ] Wait for Docker to be ready (whale icon)

### Verify Docker

- [ ] Run: `docker --version` (shows version)
- [ ] Run: `docker info` (no errors)
- [ ] Run: `docker-compose --version` (shows version)

---

## ⚙️ Configuration (Target Computer)

### Option 1: Demo Mode (Skip Configuration)

- [ ] No configuration needed
- [ ] App will use example credentials

### Option 2: Configure Credentials

- [ ] Copy example file:
  ```bash
  # Windows
  copy config\credentials.json.example config\credentials.json

  # Mac/Linux
  cp config/credentials.json.example config/credentials.json
  ```

- [ ] Edit `config/credentials.json` with your API keys
- [ ] Save file

### Option 3: Environment File

- [ ] Copy `env.example` to `.env`
- [ ] Edit `.env` with your API keys
- [ ] Save file

---

## 🎯 Run Application (Target Computer)

### Start ClickTok

**Windows:**
- [ ] Double-click `docker-start.bat`
- [ ] Select option 1 (GUI) or 2 (CLI)
- [ ] Wait for first-time setup (5-10 minutes)

**Mac/Linux:**
- [ ] Make executable: `chmod +x docker-start.sh`
- [ ] Run: `./docker-start.sh`
- [ ] Select option
- [ ] Wait for first-time setup (5-10 minutes)

**Or use Docker directly:**
- [ ] Run: `docker-compose up --build`
- [ ] Wait for first-time setup (5-10 minutes)

---

## ✅ Verification (Target Computer)

### Basic Tests

- [ ] Application starts without errors
- [ ] No error messages in terminal
- [ ] GUI/CLI accessible
- [ ] Can navigate interface

### Functional Tests

- [ ] Can create a test video
- [ ] Video saves correctly
- [ ] Settings can be changed
- [ ] Database works

### Persistence Tests

- [ ] Stop application: `docker-compose down`
- [ ] Restart: `docker-compose up`
- [ ] Data still exists
- [ ] No data loss

### Hot-Reload Test

- [ ] Edit a file in `src/`
- [ ] Run: `docker-compose restart`
- [ ] Changes reflected in application

---

## 🐛 Troubleshooting

### If Docker Not Found

- [ ] Install Docker Desktop
- [ ] Start Docker Desktop
- [ ] Try again

### If Build Fails

- [ ] Check internet connection
- [ ] Run: `docker-compose build --no-cache`
- [ ] Check logs for specific error

### If Port In Use

- [ ] Edit `docker-compose.yml`
- [ ] Change `8080:8080` to `8081:8080`
- [ ] Restart: `docker-compose up`

### If Changes Not Reflecting

- [ ] Run: `docker-compose restart`
- [ ] If still not working: `docker-compose up --build`

### If No Space Left

- [ ] Clean Docker: `docker system prune -a`
- [ ] Remove old volumes: `docker volume prune`
- [ ] Try again

---

## 📊 Success Criteria

**Deployment is successful when ALL are checked:**

- [ ] ✅ Docker installed and running
- [ ] ✅ Application starts: `docker-compose up`
- [ ] ✅ No errors in logs: `docker-compose logs`
- [ ] ✅ GUI or CLI accessible
- [ ] ✅ Can perform main tasks (create video, etc.)
- [ ] ✅ Data persists after restart
- [ ] ✅ Configuration works (if configured)
- [ ] ✅ Performance acceptable

**All checked? SUCCESS!** 🎉

---

## 📞 Quick Reference

### Essential Commands

```bash
# Start
docker-compose up

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Rebuild
docker-compose up --build
```

### With Makefile

```bash
make up       # Start
make down     # Stop
make restart  # Restart
make logs     # Logs
make test     # Test
make help     # All commands
```

---

## 🎓 Next Steps After Deployment

- [ ] Configure production credentials
- [ ] Test all features
- [ ] Set up backup schedule
- [ ] Document custom configurations
- [ ] Train users (if applicable)
- [ ] Monitor logs regularly
- [ ] Update as needed

---

## 📚 Documentation

**Read these for help:**

- `QUICK_DEPLOY.md` - One-page guide
- `DEPLOY_ANYWHERE.md` - Complete deployment
- `DOCKER_QUICKSTART.md` - Docker basics
- `DOCKER_README.md` - Full Docker guide
- `README.md` - Main documentation

---

## ✨ Final Check

**Before marking complete, verify:**

- [ ] Application runs on target computer
- [ ] All features work
- [ ] No errors
- [ ] Data persists
- [ ] Configuration correct
- [ ] Documentation accessible
- [ ] Team trained (if applicable)

**All checked? Deployment complete!** ✅

---

**Date Deployed:** _______________

**Deployed By:** _______________

**Target Computer:** _______________

**Status:** [ ] Success  [ ] Issues (see notes below)

**Notes:**
```
_________________________________________
_________________________________________
_________________________________________
_________________________________________
_________________________________________
```

---

**Version:** 1.0
**Print this page for easy reference!** 📄
