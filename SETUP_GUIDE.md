# ClickTok Setup Guide

Complete step-by-step setup instructions for beginners.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows 10/11, macOS, or Linux
- [ ] Python 3.8 or higher installed
- [ ] Basic command-line knowledge
- [ ] TikTok account with posting privileges
- [ ] 2GB+ free disk space

---

## Step-by-Step Setup

### 1. Verify Python Installation

Open terminal/command prompt and run:

```bash
python --version
```

Should show: `Python 3.8.x` or higher

If not installed, download from: https://www.python.org/downloads/

**Windows users**: Check "Add Python to PATH" during installation!

---

### 2. Install FFmpeg

FFmpeg is required for video processing.

#### Windows:

**Option A: Using Chocolatey (Recommended)**
```bash
choco install ffmpeg
```

**Option B: Manual Installation**
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Open "Environment Variables"
   - Edit "Path"
   - Add `C:\ffmpeg\bin`
4. Restart terminal

#### macOS:

```bash
brew install ffmpeg
```

(If you don't have Homebrew, install from: https://brew.sh/)

#### Linux (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

---

### 3. Navigate to ClickTok Directory

```bash
cd Desktop/ClickTok
```

---

### 4. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### 5. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- moviepy (video editing)
- playwright (browser automation)
- Pillow (image processing)
- requests (HTTP requests)
- And more...

**Note**: This may take 5-10 minutes.

---

### 6. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser for automation.

---

### 7. Configure Credentials

Edit `config/credentials.json`:

```json
{
  "tiktok": {
    "username": "your_actual_tiktok_username",
    "password": "your_actual_password",
    "cookies_file": "data/tiktok_cookies.json"
  },
  "openai_api_key": "YOUR_OPENAI_API_KEY_HERE",
  "anthropic_api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
  "tiktok_shop_api": {
    "app_key": "YOUR_TIKTOK_SHOP_APP_KEY",
    "app_secret": "YOUR_TIKTOK_SHOP_APP_SECRET",
    "access_token": "YOUR_ACCESS_TOKEN"
  }
}
```

**Minimum required:**
- TikTok username and password

**Optional (for enhanced features):**
- OpenAI API key (for AI-generated captions)
- TikTok Shop API credentials (for real product data)

---

### 8. Add Your Assets

#### Logo (Watermark)

Create or find a logo (PNG with transparent background recommended):

```
assets/logo.png
```

Recommended size: 200x200px to 500x500px

#### Background Music

Add royalty-free MP3 files to:

```
assets/music/
```

**Free music sources:**
- YouTube Audio Library
- Pixabay Music
- Free Music Archive

**Important**: Only use royalty-free music to avoid copyright issues!

---

### 9. Test the Installation

Run the test command:

```bash
python main.py --version
```

Should output: `ClickTok 1.0.0`

---

### 10. Launch the Dashboard

```bash
python main.py
```

A window should open with the ClickTok dashboard!

---

## First-Time Workflow

### Step 1: Fetch Demo Products

1. Click **"Dashboard"** tab
2. Click **"Fetch New Products"** button
3. Wait for products to load (demo data will be used initially)

### Step 2: Select Products

1. Go to **"Products"** tab
2. Select products you like (click to select, Ctrl+Click for multiple)
3. Click **"Select for Videos"** button

### Step 3: Create Videos

1. Go to **"Videos"** tab
2. Click **"Create Videos"** button
3. Wait for videos to generate (may take 1-2 minutes each)
4. Videos will be saved to `data/videos/`

### Step 4: Review Videos

Before posting, review the generated videos:

```
data/videos/DEMO_0001_video.mp4
```

Watch them to ensure quality!

### Step 5: Post to TikTok (Manual Review)

1. Go to **"Post to TikTok"** tab
2. Click **"Post Videos"** button
3. A browser window opens with TikTok
4. **First time**: Log in manually to TikTok
5. Review the auto-filled caption and hashtags
6. Make any adjustments
7. Click **"Post"** button in TikTok
8. Press ENTER in the terminal/dashboard

---

## TikTok Shop API Setup (Optional)

To fetch **real** TikTok Shop products (not demo data), you need API access.

### How to Get TikTok Shop API Access:

1. Go to: https://partner.tiktokshop.com/
2. Create a TikTok Shop Seller account
3. Apply for API access in the Partner Portal
4. Once approved, you'll receive:
   - App Key
   - App Secret
   - Access Token

5. Add these to `config/credentials.json`

**Note**: TikTok Shop API access is only available in certain regions and requires an active seller account.

---

## OpenAI API Setup (Optional - For AI Captions)

To use AI-generated captions:

1. Go to: https://platform.openai.com/
2. Create an account
3. Add billing information
4. Create an API key
5. Add to `config/credentials.json`:

```json
{
  "openai_api_key": "sk-proj-..."
}
```

6. Edit `config/settings.py`:

```python
AI_CONFIG = {
    'provider': 'openai',
    'model': 'gpt-3.5-turbo',
    'temperature': 0.7
}
```

**Cost**: GPT-3.5-turbo is very affordable (~$0.001 per caption)

---

## Customization

### Adjust Video Settings

Edit `config/settings.py`:

```python
VIDEO_CONFIG = {
    "resolution": (1080, 1920),  # 9:16 for TikTok
    "fps": 30,                   # Frames per second
    "duration": 15,              # Video length in seconds
}
```

### Change Product Filters

```python
PRODUCT_FILTERS = {
    "min_commission_rate": 10,   # Minimum 10% commission
    "min_price": 10,             # Minimum $10
    "max_price": 200,            # Maximum $200
    "min_rating": 4.0,           # 4+ stars
}
```

### Adjust Safety Limits

```python
SAFETY_CONFIG = {
    "min_delay_between_posts": 3600,  # 1 hour
    "max_posts_per_day": 5,           # Max 5 posts/day
}
```

---

## Troubleshooting

### Issue: "No module named 'moviepy'"

**Solution:**
```bash
pip install moviepy
```

### Issue: "FFmpeg not found"

**Solution:**
- Verify FFmpeg is installed: `ffmpeg -version`
- Ensure it's in your PATH
- Restart terminal after adding to PATH

### Issue: "Permission denied" on macOS/Linux

**Solution:**
```bash
chmod +x main.py
```

### Issue: Playwright browser doesn't open

**Solution:**
```bash
playwright install chromium
```

### Issue: Video creation fails

**Check:**
1. Is FFmpeg installed?
2. Are there files in `assets/music/`?
3. Does `assets/logo.png` exist?
4. Check `logs/system.log` for errors

### Issue: TikTok login fails

**Solution:**
- Use manual login (recommended)
- Clear browser cache
- Try different browser
- Check your TikTok account isn't restricted

---

## Performance Optimization

### For Faster Video Generation:

1. **Use SSD** for data storage
2. **Lower video quality** (720p instead of 1080p)
3. **Shorter videos** (10 seconds instead of 15)
4. **Reduce FPS** (24 instead of 30)

Example:
```python
VIDEO_CONFIG = {
    "resolution": (720, 1280),  # Lower resolution
    "fps": 24,                  # Lower FPS
    "duration": 10,             # Shorter
}
```

---

## Security Best Practices

1. **Never commit credentials** to Git
2. **Use strong passwords** for TikTok account
3. **Enable 2FA** on TikTok (will require manual login)
4. **Don't share API keys**
5. **Regular backups** of your database
6. **Keep software updated**

---

## Next Steps

Once setup is complete:

1. ✅ Read the main [README.md](README.md)
2. ✅ Review [Best Practices](#best-practices) section
3. ✅ Test with demo products first
4. ✅ Create your first real video
5. ✅ Post and track performance
6. ✅ Optimize based on results

---

## Getting Help

If you encounter issues:

1. Check `logs/system.log`
2. Re-read this guide
3. Check Python version (must be 3.8+)
4. Ensure all dependencies are installed
5. Try in a fresh virtual environment

---

**Setup Complete! Ready to start earning through TikTok affiliate marketing! 🚀**
