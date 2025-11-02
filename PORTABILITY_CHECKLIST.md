# ClickTok - Portability Checklist

This checklist ensures ClickTok works when moved to another computer.

## ✅ Pre-Deployment Checklist

### Files to Include
- [x] All Python source files (`src/`, `gui/`, `config/`)
- [x] `requirements.txt` (updated with all packages)
- [x] `setup.py` (installation script)
- [x] `main.py` (entry point)
- [x] `env.example` (credentials template)
- [x] `config/credentials.json.example` (credentials template)
- [x] `INSTALLATION_GUIDE.md` (setup instructions)
- [x] Batch files (`.bat` files for Windows)

### Files to Exclude (Don't Copy)
- [ ] `.env` (contains your personal API keys - create new on new computer)
- [ ] `config/credentials.json` (contains your personal credentials)
- [ ] `data/products.db` (database - will be recreated)
- [ ] `data/products/` (downloaded images - can be recreated)
- [ ] `data/videos/` (generated videos - can be recreated)
- [ ] `logs/` (log files - auto-created)
- [ ] `__pycache__/` (Python cache - auto-created)
- [ ] `*.pyc` (compiled Python files)

### Optional Files (Can Copy)
- [ ] `assets/logo.png` (your logo)
- [ ] `assets/music/*.mp3` (your music files)
- [ ] `assets/fonts/` (custom fonts)

---

## 🚀 On New Computer Setup

### Step 1: Copy Project
Copy the entire ClickTok folder (excluding files above)

### Step 2: Install Dependencies
```bash
python setup.py
```
or
```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Step 3: Configure Credentials
Copy `env.example` to `.env` and edit with your API keys

### Step 4: Run
```bash
python main.py
```

---

## ✅ Verification

After setup, verify:
- [ ] Python packages installed: `pip list` shows all required packages
- [ ] Playwright browser installed: `python -m playwright install chromium`
- [ ] FFmpeg installed: `ffmpeg -version`
- [ ] Credentials configured: `.env` file exists with API keys
- [ ] Application launches: `python main.py` opens GUI

---

## 📝 Notes

- All paths are relative - no hardcoded paths
- Database auto-creates on first run
- All directories auto-create on first run
- Settings are portable - works on any OS (Windows/Mac/Linux)

