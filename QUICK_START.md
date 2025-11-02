# 🚀 ClickTok - Quick Start Guide

## How to Run ClickTok

### ✅ **Method 1: Double-Click (Easiest!)**

Simply double-click:
- **`ClickTok.bat`** → Launches GUI Dashboard (Recommended)
- **`ClickTok-CLI.bat`** → Launches Command-Line Interface

---

### ✅ **Method 2: Command Line**

Open Command Prompt / Terminal in the ClickTok folder and run:

```bash
# GUI Mode (default)
python main.py

# CLI Mode
python main.py --cli
```

---

## 🔧 First Time Setup (One-Time Only)

**If this is your first time running ClickTok:**

### Option A: Auto-Setup (Easiest)
Just run `ClickTok.bat` - it will automatically install dependencies if needed!

### Option B: Manual Setup
1. Double-click **`setup.bat`** (Windows) or run `./setup.sh` (Mac/Linux)
2. Wait 5-10 minutes for installation
3. Then run **`ClickTok.bat`**

---

## 📋 Prerequisites Check

Make sure you have:
- ✅ **Python 3.8+** installed
- ✅ **Internet connection** (for first-time setup)
- ✅ **Credentials configured** (see Configuration section below)

---

## ⚙️ Configuration (Before First Run)

### 1. Set Up Credentials

**Option A: Use .env file (Recommended)**
1. Copy `env.example` to `.env`
2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=sk-your-key-here
   GROQ_API_KEY=gsk_your-key-here
   TIKTOK_USERNAME=your_username
   TIKTOK_PASSWORD=your_password
   ```

**Option B: Use credentials.json**
Create `config/credentials.json`:

```json
{
  "openai_api_key": "your-openai-key",
  "groq_api_key": "your-groq-key",
  "anthropic_api_key": "your-anthropic-key",
  "elevenlabs_api_key": "your-elevenlabs-key",
  "tiktok_username": "your-tiktok-username",
  "tiktok_password": "your-tiktok-password"
}
```

### 2. Verify Settings

Settings are already optimized for Philippines market:
- Price range: $2-30 USD (PHP 112-1,680)
- Focus categories: Beauty, Fashion, Home
- Posting schedule: 3-5 posts/day
- Timezone: Asia/Manila

---

## 🎯 Basic Workflow

Once ClickTok is running:

### 1. **Dashboard Tab**
- View statistics
- Quick actions

### 2. **Settings Tab**
- Configure API keys
- Test API connections
- View TikTok account stats

### 3. **Products Tab**
- Click **"Fetch New Products"**
- Browser opens → Navigate to TikTok Shop manually if needed
- Products will be extracted and saved

### 4. **Videos Tab**
- Select products
- Click **"Create Videos"**
- Videos generated automatically

### 5. **Post to TikTok Tab**
- Click **"Post to TikTok"**
- Review video
- Manually click "Post" button (safety feature)

---

## 🌐 Philippines-Specific Workflow

Since you don't have TikTok Shop access:

### Product Discovery:
1. Click **"Fetch New Products"**
2. Browser opens → Navigate to TikTok Shop manually
3. Wait for 30 seconds during login if needed
4. Navigate to product pages you want to promote
5. Script will extract products from current page
6. Products saved to database

### Alternative: Use TikTok Search
- The scraper will also try searching TikTok for product videos
- It extracts product links from video descriptions
- Works even without Shop access!

---

## 📊 Daily Routine (3 Hours/Day)

### Morning (1 Hour):
- Batch create 20-30 videos (use automation)
- Enough for the week

### Evening (30 Minutes):
- Post 3-5 videos at optimal times (6-9 PM PHT)
- Engage with comments

### End of Day (30 Minutes):
- Review metrics
- Plan next day's products

---

## 🎯 Your Goals & Metrics

**Target: PHP 10,000/month**

### Month 1:
- 3-4 posts/day = ~100 posts/month
- Expected: PHP 1,200/month

### Month 2:
- 4-5 posts/day = ~135 posts/month
- Expected: PHP 3,825/month

### Month 3+:
- 5 posts/day = ~150 posts/month
- Expected: PHP 10,000/month ✅

---

## 🐛 Troubleshooting

### Problem: "Module not found"
**Solution:** Run `setup.bat` first to install dependencies

### Problem: Browser opens but doesn't extract products
**Solution:** 
- Make sure you're logged into TikTok
- Navigate to a product page manually
- Wait for script to detect and extract

### Problem: "Python not recognized"
**Solution:** 
- Install Python from https://python.org
- Check "Add Python to PATH" during installation

### Problem: GUI doesn't open
**Solution:**
- Check `logs/system.log` for errors
- Run from Command Prompt to see error messages

---

## 📁 Important Files

- **`ClickTok.bat`** - Launch GUI (double-click this!)
- **`setup.bat`** - Install dependencies (first time only)
- **`main.py`** - Main application
- **`config/settings.py`** - All settings (already optimized for PH)
- **`config/credentials.json`** - Your API keys
- **`.env`** - Environment variables (alternative to credentials.json)
- **`strategy.txt`** - Complete Philippines market strategy
- **`logs/system.log`** - Error logs if something goes wrong

---

## 🎬 Quick Test Run

Want to test everything works?

1. **Launch ClickTok:**
   ```bash
   python main.py
   ```

2. **Go to Settings Tab:**
   - Test your API keys (green circles = working)

3. **Go to Products Tab:**
   - Click "Fetch New Products"
   - Browser opens → Navigate to TikTok Shop
   - Wait for products to load

4. **Go to Videos Tab:**
   - Select a product
   - Click "Create Videos"
   - Check `data/videos/` folder for generated video

5. **Go to Post Tab:**
   - Click "Post to TikTok"
   - Review video
   - Click "Post" when ready

---

## 📚 More Documentation

- **`strategy.txt`** - Complete Philippines market strategy guide
- **`README.md`** - Full technical documentation
- **`AI_AGENT_GUIDE.md`** - For developers/AI assistants
- **`HOW_TO_RUN.txt`** - Detailed run instructions
- **`INSTALL.md`** - Installation troubleshooting

---

## ✅ Checklist Before Starting

- [ ] Python 3.8+ installed
- [ ] Ran `setup.bat` or `ClickTok.bat` (auto-setup)
- [ ] Credentials configured in `.env` or `config/credentials.json`
- [ ] TikTok account credentials ready
- [ ] Internet connection active
- [ ] Read `strategy.txt` for Philippines market strategy

---

## 🚀 Ready to Start?

**Just double-click: `ClickTok.bat`**

That's it! The GUI will open and you can start automating your TikTok affiliate marketing. 💰

---

**Need Help?** Check `logs/system.log` for errors or see `INSTALL.md` for troubleshooting.

