# ClickTok - Installation & Setup Guide

## Quick Start (Fresh Installation)

### Step 1: Clone/Copy the Project
1. Copy the entire ClickTok folder to your new computer
2. Make sure Python 3.8+ is installed

### Step 2: Install Dependencies
Run ONE of these commands:

**Windows:**
```bash
python setup.py
```
or
```bash
setup.bat
```

**Mac/Linux:**
```bash
python setup.py
```
or
```bash
./setup.sh
```

**Manual Installation:**
```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Step 3: Configure Credentials

**Option A: Use .env file (Recommended)**
1. Copy `env.example` to `.env`
2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=sk-your-key-here
   GROQ_API_KEY=gsk_your-key-here
   TIKTOK_USERNAME=your_username
   TIKTOK_PASSWORD=your_password
   ```

**Option B: Use GUI Settings**
1. Run the application: `python main.py`
2. Go to Settings tab
3. Enter your credentials
4. Click "Save Settings"

### Step 4: Add Assets (Optional)
- Place your logo in: `assets/logo.png`
- Add music files to: `assets/music/*.mp3`
- See `assets/README.txt` for details

### Step 5: Run ClickTok
```bash
python main.py
```

---

## Required Packages

All packages are listed in `requirements.txt`. Key packages:

### Core (Required)
- `moviepy` - Video editing
- `playwright` - Browser automation
- `Pillow` - Image processing
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

### AI (Optional but Recommended)
- `openai` - OpenAI API for scripts
- `groq` - Groq API for scripts (free tier available)
- `anthropic` - Claude API (optional)

### System Requirements
- **Python**: 3.8+ (3.11 or 3.12 recommended)
- **FFmpeg**: Required for video processing
  - Windows: Download from https://ffmpeg.org/download.html
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

---

## Troubleshooting

### "Module not found" errors
```bash
python -m pip install -r requirements.txt
```

### Playwright browser not found
```bash
python -m playwright install chromium
```

### FFmpeg not found
Install FFmpeg (see System Requirements above)

### OpenAI/Groq not working
1. Check your API key in `.env` file or Settings tab
2. Verify API key is valid
3. Check if you have credits/quota remaining

### Database errors
Delete `data/products.db` and restart (will recreate database)

---

## Verification Checklist

After installation, verify:
- [ ] Python 3.8+ installed
- [ ] All packages installed (`pip list` shows required packages)
- [ ] Playwright browser installed
- [ ] FFmpeg installed (`ffmpeg -version`)
- [ ] Credentials configured (`.env` or Settings tab)
- [ ] Assets folder exists (`assets/` directory)

---

## Portability Notes

✅ **All paths are relative** - Project works on any computer
✅ **No hardcoded paths** - Uses `Path(__file__).parent` for portability
✅ **Database auto-creates** - SQLite database created automatically
✅ **Directories auto-create** - All required folders created on first run

---

## File Structure

```
ClickTok/
├── config/
│   ├── settings.py          # Configuration (editable)
│   └── credentials.json.example  # Template
├── data/                     # Auto-created
│   ├── products.db          # Database
│   ├── products/             # Product images
│   └── videos/               # Generated videos
├── assets/                   # Your assets
│   ├── logo.png             # Required
│   └── music/               # Optional
├── .env                      # Your credentials (create from env.example)
├── requirements.txt         # Python packages
├── setup.py                 # Setup script
└── main.py                  # Entry point
```

---

## Updates

When updating from another computer:
1. Copy entire project folder
2. Run `python setup.py` to ensure all packages are up to date
3. Your `.env` file will be preserved (keep your credentials)

---

## Support

If you encounter issues:
1. Check `logs/system.log` for error details
2. Verify all packages: `pip list`
3. Reinstall if needed: `python setup.py`

