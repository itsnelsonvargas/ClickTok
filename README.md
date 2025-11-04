# ClickTok - TikTok Affiliate Marketing Automation System

**Professional semi-automated system for generating consistent income through TikTok Shop affiliation with minimal manual work.**

## 🌍 100% Portable - Runs on ANY Computer!

✅ **Docker-based** - No dependency issues
✅ **Cross-platform** - Windows, Mac, Linux
✅ **One command** - `docker-compose up --build`
✅ **Guaranteed** - If it works once, it works everywhere

**Quick Deploy:** See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for instant deployment guide!

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation](#installation)
   - **🐳 [Docker Setup](DOCKER_QUICKSTART.md)** (Recommended - works on any computer!)
5. [Configuration](#configuration)
6. [Usage Guide](#usage-guide)
7. [Workflow](#workflow)
8. [Best Practices](#best-practices)
9. [Safety & TikTok Guidelines](#safety--tiktok-guidelines)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

ClickTok is a semi-automated TikTok affiliate marketing system that:

- **Fetches** trending/high-commission products from TikTok Shop
- **Generates** professional advertising videos automatically
- **Creates** engaging captions and hashtags
- **Posts** to TikTok with semi-automated workflow (manual review before posting)
- **Tracks** performance and affiliate links

### Key Benefits

✅ **Save Time**: Automate 80% of the content creation process
✅ **Consistency**: Post regularly with minimal effort
✅ **Professional**: High-quality videos with text overlays, music, and branding
✅ **Safe**: Manual review before posting to avoid bans
✅ **Trackable**: Monitor all affiliate links and performance

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     ClickTok System                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   GUI/CLI    │◄────►│   Database   │                   │
│  │  Dashboard   │      │   (SQLite)   │                   │
│  └──────┬───────┘      └──────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────┐      │
│  │            Core Modules                          │      │
│  ├─────────────────────────────────────────────────┤      │
│  │                                                  │      │
│  │  1. Product Fetcher                             │      │
│  │     └─► TikTok Shop API / Scraper               │      │
│  │                                                  │      │
│  │  2. Video Creator                                │      │
│  │     └─► MoviePy (images, text, music)           │      │
│  │                                                  │      │
│  │  3. Caption Generator                            │      │
│  │     └─► AI-powered or Template-based            │      │
│  │                                                  │      │
│  │  4. TikTok Uploader                              │      │
│  │     └─► Playwright (semi-automated)             │      │
│  │                                                  │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
ClickTok/
├── config/
│   ├── settings.py              # All configuration settings
│   └── credentials.json         # API keys (DO NOT COMMIT)
│
├── data/
│   ├── products.db              # SQLite database
│   ├── products/                # Downloaded product images
│   └── videos/                  # Generated videos
│
├── src/
│   ├── database.py              # Database operations
│   ├── product_fetcher.py       # Fetch TikTok Shop products
│   ├── video_creator.py         # Video generation
│   ├── caption_generator.py     # Captions & hashtags
│   └── tiktok_uploader.py       # TikTok automation
│
├── gui/
│   └── dashboard.py             # Tkinter GUI
│
├── assets/
│   ├── logo.png                 # Your watermark/logo
│   ├── music/                   # Background music files (.mp3)
│   └── fonts/                   # Custom fonts
│
├── logs/
│   └── system.log               # Activity logs
│
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Features

### 1. Product Selection
- Fetch trending products from TikTok Shop
- Filter by commission rate, price, rating, category
- Manual selection of products to promote
- Store product details in local database

### 2. Video Creation
- **Automated video generation** with:
  - Product images with zoom/pan effects
  - Text overlays (product name, price, CTA)
  - Background music
  - Logo watermark
  - Transitions and effects
- **Multiple templates**: Modern, Minimal, Energetic
- **9:16 aspect ratio** optimized for TikTok
- **Customizable**: Edit text, colors, fonts, music

### 3. Caption & Hashtag Generation
- **AI-powered captions** (OpenAI/Claude) or template-based
- Engaging hooks and CTAs
- **Smart hashtag generation**:
  - Category-based hashtags
  - Trending hashtags
  - Product-specific tags
- Multiple caption variations for A/B testing

### 4. Semi-Automated Posting
- **Playwright browser automation**
- **Manual review** before posting (safe from bans)
- Cookie-based login (stay logged in)
- Auto-fill caption and hashtags
- Safety checks (daily limits, timing)

### 5. Tracking & Analytics
- Track all products and videos
- Store affiliate links
- Monitor video performance
- Dashboard with statistics

---

## Installation

### 🚀 One-Command Installation (Recommended)

**Windows:**
```bash
cd ClickTok
setup.bat
```

**macOS/Linux:**
```bash
cd ClickTok
./setup.sh
```

**Or use Python directly:**
```bash
python setup.py
```

That's it! The setup script will automatically:
- ✅ Install all Python packages
- ✅ Install Playwright browsers
- ✅ Check FFmpeg
- ✅ Create directories
- ✅ Verify installation

**Time required:** 5-10 minutes

### 🐳 Docker Installation (100% Guaranteed)

**The easiest way to run ClickTok on any computer with zero dependency issues!**

```bash
# 1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
# 2. Start Docker Desktop
# 3. Run ClickTok with one command:

docker-compose up --build
```

**Windows users** can simply double-click: `docker-start.bat`

**Mac/Linux users** can run: `./docker-start.sh`

**Why Docker?**
- ✅ **Works on any computer** (Windows, Mac, Linux)
- ✅ **Zero dependency issues** - Everything pre-installed
- ✅ **FFmpeg & Playwright** automatically configured
- ✅ **Hot-reload** - Code changes sync instantly
- ✅ **Isolated** - Doesn't interfere with your system

For complete Docker documentation, see: **[DOCKER_README.md](DOCKER_README.md)**

### 📖 Detailed Installation Guide

For detailed installation instructions, troubleshooting, and alternative methods, see:
- **[INSTALL.md](INSTALL.md)** - Complete installation guide

### Prerequisites

- **Python 3.8+**
- **FFmpeg** (setup script will check and guide you)
- **Internet connection**

### Quick Verify

```bash
python main.py --version
```

If you see `ClickTok 1.0.0`, you're ready to go! 🎉

---

## Configuration

### 1. Edit Credentials

Edit `config/credentials.json`:

```json
{
  "tiktok": {
    "username": "your_tiktok_username",
    "password": "your_password"
  },
  "openai_api_key": "sk-...",  // Optional: for AI captions
  "tiktok_shop_api": {
    "app_key": "...",            // TikTok Shop API credentials
    "app_secret": "...",
    "access_token": "..."
  }
}
```

**⚠️ IMPORTANT**: Add `credentials.json` to `.gitignore` to avoid leaking secrets!

### 2. Add Your Assets

- **Logo**: Place `logo.png` in `assets/`
- **Music**: Add `.mp3` files to `assets/music/`
- **Fonts**: Add custom fonts to `assets/fonts/` (optional)

### 3. Customize Settings

Edit `config/settings.py` to adjust:

- Video duration, resolution, FPS
- Text overlay styles
- Product filters (min commission, price range, categories)
- Safety limits (max posts per day, delays)
- AI provider (OpenAI, Anthropic, or local)

---

## Usage Guide

### Option 1: GUI Dashboard (Recommended)

**Easiest way (Windows):**

Just **double-click** `ClickTok.bat` in the ClickTok folder!

**Or use command line:**

```bash
python main.py
```

**Workflow:**

1. **Dashboard Tab**: View statistics and quick actions
2. **Products Tab**:
   - Click "Fetch Products" to get new products
   - Select products you want to promote
   - Click "Select for Videos"
3. **Videos Tab**:
   - Click "Create Videos" to generate videos
   - Preview generated videos in `data/videos/`
4. **Post Tab**:
   - Click "Post to TikTok"
   - Browser window opens - review and click "Post" manually
   - System tracks the posted video

### Option 2: CLI

For command-line users:

```bash
python main.py --cli
```

### Option 3: Python API

Use ClickTok as a library:

```python
from src.database import Database
from src.product_fetcher import ProductFetcher
from src.video_creator import VideoCreator
from config.settings import *
import json

# Load credentials
with open("config/credentials.json") as f:
    creds = json.load(f)

# Initialize
db = Database(DATABASE_PATH)
fetcher = ProductFetcher(creds, PRODUCT_FILTERS)

# Fetch products
products = fetcher.fetch_trending_products(limit=10)

# Save to database
for product in products:
    db.add_product(product)

# Create video
creator = VideoCreator(VIDEO_CONFIG, ASSETS_DIR)
video_path = VIDEOS_DIR / "demo.mp4"
creator.create_product_video(products[0], video_path)
```

---

## Workflow

### Complete End-to-End Workflow

```
1. FETCH PRODUCTS
   ↓
   [Product Fetcher] → Scrape/API → Filter by criteria
   ↓
   Store in Database (status: pending)

2. MANUAL SELECTION
   ↓
   [User] → Review products → Select winners
   ↓
   Update Database (status: selected)

3. CREATE VIDEOS
   ↓
   [Caption Generator] → Create caption + hashtags
   ↓
   [Video Creator] → Generate video with overlays
   ↓
   Save to data/videos/ (status: created)

4. REVIEW & POST
   ↓
   [User] → Review video locally
   ↓
   [TikTok Uploader] → Open browser → Auto-fill
   ↓
   [User] → Manual review → Click "Post"
   ↓
   Update Database (status: posted)

5. TRACK PERFORMANCE
   ↓
   Monitor views, clicks, conversions
   ↓
   Optimize future content
```

---

## Best Practices

### For Maximum Results

✅ **Post Consistently**: 1-3 videos per day, same times
✅ **Engage**: Respond to comments to boost algorithm
✅ **Test Variations**: Try different templates, captions, hashtags
✅ **High-Quality Products**: Only promote products you'd use yourself
✅ **Trending Audio**: Use trending sounds when possible
✅ **Hook Viewers**: First 2 seconds are critical
✅ **Clear CTA**: Make it obvious how to buy

### Content Tips

- **Short & Punchy**: 7-15 seconds ideal
- **Text Overlays**: Many watch on mute
- **Problem → Solution**: Show how product solves a problem
- **Social Proof**: Mention reviews/ratings
- **Urgency**: "Limited stock", "Sale ends soon"

### Product Selection

- **High Commission**: Aim for 15%+ commission rate
- **Good Reviews**: 4.5+ star rating
- **Problem-Solvers**: Products that solve specific problems
- **Visual Appeal**: Products that look good on camera
- **Broad Appeal**: Mass-market products perform better

---

## Safety & TikTok Guidelines

### Avoiding Bans

🚨 **Critical Rules:**

1. **NEVER use fully automated posting** - Always review manually
2. **Respect daily limits** - Max 10 posts/day (recommended 3-5)
3. **Vary timing** - Don't post at exact same times
4. **Human behavior** - Random delays, varied captions
5. **Follow TikTok TOS** - Don't spam, mislead, or violate guidelines
6. **Disclosure** - Be transparent about affiliate links
7. **Quality over quantity** - Better to post less with high quality

### System Safety Features

✅ **Manual Review**: Final approval before posting
✅ **Daily Limits**: Configurable max posts per day
✅ **Random Delays**: Simulate human behavior
✅ **Cookie Authentication**: Avoid repeated logins
✅ **Logging**: Track all actions for debugging

### TikTok's Automation Detection

TikTok can detect:
- Identical captions/hashtags
- Posting at exact intervals
- Rapid actions (clicking too fast)
- Non-human mouse movements
- VPN/proxy usage

**Our Solution**: Semi-automation with human oversight

### FTC Disclosure Requirements

When posting affiliate content:

✅ Include #ad or #affiliate
✅ Disclose material connections
✅ Be honest about product experience
✅ Don't make false claims

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

```bash
pip install -r requirements.txt
```

#### 2. FFmpeg not found

Install FFmpeg and add to PATH. Verify with:
```bash
ffmpeg -version
```

#### 3. Playwright browser not opening

```bash
playwright install chromium
```

#### 4. TikTok login fails

- Use manual login (recommended)
- Clear cookies and re-login
- Check credentials in `config/credentials.json`
- Avoid automated login (high ban risk)

#### 5. Videos not generating

- Check that `assets/` folder has logo and music
- Verify product images are downloading
- Check logs in `logs/system.log`

#### 6. API errors (TikTok Shop)

- Verify API credentials
- Check API rate limits
- Use demo mode for testing (no API needed)

### Getting Help

- **Check logs**: `logs/system.log`
- **Enable debug mode**: Set `log_level: DEBUG` in settings
- **GitHub Issues**: Report bugs with logs attached

---

## Advanced Features

### Using AI for Captions

**OpenAI:**
```json
{
  "openai_api_key": "sk-..."
}
```

Set in `config/settings.py`:
```python
AI_CONFIG = {
    'provider': 'openai',
    'model': 'gpt-3.5-turbo'
}
```

**Anthropic Claude:**
```json
{
  "anthropic_api_key": "sk-ant-..."
}
```

```python
AI_CONFIG = {
    'provider': 'anthropic',
    'model': 'claude-3-haiku-20240307'
}
```

### Custom Video Templates

Edit `src/video_creator.py` to create custom templates:

```python
def create_custom_template(self, product):
    # Your custom video logic
    pass
```

### Scheduling Posts

Use Python's `schedule` library (already in requirements):

```python
import schedule
import time

def post_job():
    # Your posting logic
    pass

schedule.every().day.at("10:00").do(post_job)
schedule.every().day.at("14:00").do(post_job)
schedule.every().day.at("18:00").do(post_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Legal & Compliance

### Disclaimer

This software is for educational purposes. You are responsible for:

- Complying with TikTok's Terms of Service
- Following FTC disclosure requirements
- Respecting intellectual property rights
- Obtaining necessary rights for music/images
- Following local laws and regulations

### Music Licensing

Use royalty-free music:
- [Epidemic Sound](https://www.epidemicsound.com/)
- [Artlist](https://artlist.io/)
- [YouTube Audio Library](https://www.youtube.com/audiolibrary)

---

## Roadmap

Future enhancements:

- [ ] Direct TikTok Shop API integration
- [ ] Analytics dashboard with graphs
- [ ] A/B testing automation
- [ ] Voiceover generation (ElevenLabs)
- [ ] Multi-account management
- [ ] Instagram Reels support
- [ ] YouTube Shorts support
- [ ] Cloud deployment option

---

## Support

Questions? Suggestions?

- **Documentation**: This README
- **Logs**: Check `logs/system.log`
- **Settings**: Review `config/settings.py`

---

## License

MIT License - See LICENSE file

---

## Acknowledgments

Built with:
- **MoviePy** - Video editing
- **Playwright** - Browser automation
- **Tkinter** - GUI framework
- **SQLite** - Database
- **Python** - Programming language

---

**Happy Affiliate Marketing! 🚀💰**

Remember: Quality content + Consistency + Patience = Success
"# ClickTok" 
