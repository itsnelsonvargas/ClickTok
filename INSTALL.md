# ClickTok Installation Guide

Multiple easy installation methods - choose what works best for you!

---

## 🚀 Quick Install (Recommended)

### **Windows**

Open Command Prompt in the ClickTok folder and run:

```bash
setup.bat
```

OR

```bash
python setup.py
```

### **macOS / Linux**

Open Terminal in the ClickTok folder and run:

```bash
chmod +x setup.sh
./setup.sh
```

OR

```bash
python3 setup.py
```

---

## ✨ What the Setup Does

The automated setup will:

1. ✅ Check Python version (requires 3.8+)
2. ✅ Upgrade pip to latest version
3. ✅ Install all Python packages from requirements.txt
4. ✅ Install Playwright Chromium browser
5. ✅ Check for FFmpeg installation
6. ✅ Create all necessary directories
7. ✅ Create asset placeholders
8. ✅ Verify installation

**Time required**: 5-10 minutes (depending on internet speed)

---

## 📋 Installation Methods

### Method 1: Automated Setup Script (Easiest)

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
./setup.sh
```

**What you'll see:**
```
============================================================
  ClickTok - Automated Setup
============================================================

This script will:
  • Check Python version
  • Install all Python packages
  • Install Playwright browsers
  • Verify FFmpeg installation
  • Create necessary directories
  • Verify installation

Continue? (y/n):
```

Just press `y` and wait for it to complete!

---

### Method 2: Python Setup Script

```bash
python setup.py
```

This runs the same process but directly through Python.

---

### Method 3: Manual Installation

If you prefer to install manually:

**Step 1: Upgrade pip**
```bash
pip install --upgrade pip
```

**Step 2: Install Python packages**
```bash
pip install -r requirements.txt
```

**Step 3: Install Playwright browsers**
```bash
python -m playwright install chromium
```

**Step 4: Verify FFmpeg**
```bash
ffmpeg -version
```

If FFmpeg is not installed:
- **Windows**: `choco install ffmpeg` or download from https://ffmpeg.org
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

---

### Method 4: Automatic on First Run

ClickTok now checks dependencies automatically!

Simply try to run:
```bash
python main.py
```

If dependencies are missing, you'll see:
```
⚠️  MISSING DEPENDENCIES DETECTED

The following packages are not installed:
  • moviepy
  • playwright
  • Pillow

Run automated setup now? (y/n):
```

Type `y` and it will install everything for you!

---

## 🔍 Verifying Installation

After installation, verify everything is working:

```bash
python -c "import moviepy; import playwright; import PIL; print('✅ All packages installed!')"
```

You should see:
```
✅ All packages installed!
```

---

## 📦 What Gets Installed

### Python Packages

| Package | Purpose |
|---------|---------|
| moviepy | Video editing and creation |
| Pillow | Image processing |
| playwright | Browser automation |
| requests | HTTP requests |
| beautifulsoup4 | HTML parsing |
| opencv-python | Video processing |
| pyttsx3 | Text-to-speech |
| customtkinter | Modern GUI |

### Browsers

- **Chromium** (via Playwright) - For TikTok automation

### System Requirements

- **FFmpeg** - Video processing (separate install)

---

## 🐛 Troubleshooting

### "python is not recognized"

**Windows:**
1. Install Python from https://python.org
2. During installation, check "Add Python to PATH"
3. Restart Command Prompt

**Mac/Linux:**
```bash
# Install Python
# Mac:
brew install python3

# Linux:
sudo apt install python3
```

---

### "pip is not recognized"

Try using:
```bash
python -m pip install -r requirements.txt
```

---

### "setup.bat is not recognized"

Make sure you're in the ClickTok folder:
```bash
cd Desktop\ClickTok
setup.bat
```

---

### Installation Takes Forever

This is normal! Installing all packages (especially moviepy with dependencies) can take 5-10 minutes.

**What's happening:**
- Downloading ~500MB of packages
- Installing numpy, scipy, and other large libraries
- Downloading Chromium browser (~150MB)

---

### FFmpeg Not Found

**Windows (Easy Method):**
```bash
# Install Chocolatey first: https://chocolatey.org/install
choco install ffmpeg
```

**Windows (Manual):**
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH
4. Restart Command Prompt

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

---

### Playwright Browser Installation Fails

Try installing manually:
```bash
python -m playwright install chromium --with-deps
```

On Linux, you may need additional dependencies:
```bash
sudo apt-get install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0
```

---

### Permission Denied (Mac/Linux)

If setup.sh won't run:
```bash
chmod +x setup.sh
./setup.sh
```

Or run setup.py directly:
```bash
python3 setup.py
```

---

## 🔄 Reinstalling / Updating

To reinstall or update:

```bash
# Delete old installations (optional)
pip uninstall moviepy playwright -y

# Run setup again
python setup.py
```

---

## 🌐 Offline Installation

If you need to install without internet:

1. Download packages on another computer:
```bash
pip download -r requirements.txt -d packages/
```

2. Transfer the `packages/` folder to the offline computer

3. Install from local folder:
```bash
pip install --no-index --find-links=packages/ -r requirements.txt
```

---

## 🧪 Testing Installation

After installation, run the test script:

```bash
python example_usage.py
```

Select option 5 to verify database and basic functionality.

---

## 📊 Installation Size

**Total disk space required:**
- Python packages: ~500 MB
- Playwright Chromium: ~150 MB
- FFmpeg: ~100 MB
- **Total: ~750 MB**

---

## ⏱️ Installation Time

**Typical installation times:**

| Connection Speed | Time |
|-----------------|------|
| Fast (50+ Mbps) | 3-5 minutes |
| Medium (10-50 Mbps) | 5-10 minutes |
| Slow (<10 Mbps) | 10-20 minutes |

---

## 🎯 Next Steps After Installation

Once installation is complete:

1. **Configure Credentials**
   ```bash
   # Edit this file:
   config/credentials.json
   ```

2. **Add Assets**
   - Logo: `assets/logo.png`
   - Music: `assets/music/*.mp3`

3. **Launch ClickTok**
   ```bash
   python main.py
   ```

4. **Read the Docs**
   - README.md - Full guide
   - QUICK_REFERENCE.md - Cheat sheet
   - SETUP_GUIDE.md - Detailed setup

---

## ✅ Installation Checklist

Use this checklist to ensure everything is ready:

- [ ] Python 3.8+ installed
- [ ] All pip packages installed (`pip list` shows moviepy, playwright, etc.)
- [ ] Playwright browsers installed
- [ ] FFmpeg installed and in PATH
- [ ] ClickTok directories created (data/, assets/, logs/)
- [ ] credentials.json configured
- [ ] Logo added to assets/logo.png
- [ ] Music added to assets/music/
- [ ] Test run successful (`python main.py --version`)

---

## 🆘 Getting Help

If you're stuck:

1. Check the error message carefully
2. Look in `logs/system.log`
3. Try manual installation (Method 3)
4. Search the error message online
5. Make sure Python 3.8+ is installed
6. Ensure you're in the ClickTok directory

---

## 🎉 Installation Complete!

If you see this message after running setup:

```
✅ All dependencies installed successfully!

Next Steps:
1. Edit config/credentials.json
2. Add assets (logo, music)
3. Run: python main.py
```

**You're ready to go! 🚀**

Start earning with TikTok affiliate marketing!

---

## Platform-Specific Notes

### Windows 10/11
- Use Command Prompt or PowerShell
- May need to run as Administrator for FFmpeg
- Antivirus might slow down installation

### macOS
- Use Terminal
- May need Xcode Command Line Tools
- Homebrew recommended for FFmpeg

### Linux (Ubuntu/Debian)
- Use Terminal
- May need `sudo` for some commands
- Install build tools: `sudo apt install build-essential`

### Linux (Other Distros)
- Adjust package manager commands accordingly
- Fedora: Use `dnf` instead of `apt`
- Arch: Use `pacman` instead of `apt`

---

**Happy Installing! 🎊**
