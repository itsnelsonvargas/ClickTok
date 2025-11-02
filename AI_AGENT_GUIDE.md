# ClickTok - Complete AI Agent Guide

**Purpose:** This document provides a comprehensive overview of the ClickTok project for AI agents (like Cursor, Claude AI) to understand the entire codebase structure, architecture, workflows, and implementation details.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [File Structure](#file-structure)
6. [Key Dependencies](#key-dependencies)
7. [Configuration System](#configuration-system)
8. [Current State & Known Issues](#current-state--known-issues)
9. [Improvement Opportunities](#improvement-opportunities)
10. [Quick Start Guide](#quick-start-guide)

---

## 🎯 Project Overview

### What is ClickTok?

**ClickTok** is a **semi-automated TikTok affiliate marketing system** designed to generate income through TikTok Shop affiliate programs. The system automates 80% of the content creation workflow while maintaining manual oversight for safety.

### Core Value Proposition

- **Automates**: Product discovery, video creation, caption generation
- **Assists**: TikTok posting with manual review (prevents bans)
- **Tracks**: All products, videos, and performance metrics
- **Safely**: Built-in limits and human oversight

### Project Goals

1. **Generate consistent income** through TikTok affiliate marketing
2. **Save time** by automating repetitive tasks
3. **Maintain safety** through semi-automation (avoid TikTok bans)
4. **Track performance** with comprehensive analytics

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐              ┌──────────────┐           │
│  │ GUI Dashboard │              │  CLI Interface│           │
│  │  (Tkinter)    │              │   (Argparse) │           │
│  └──────┬───────┘              └──────┬───────┘           │
│         │                              │                    │
│         └────────────┬─────────────────┘                    │
│                      │                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────────┐
│                      │     Business Logic Layer             │
├──────────────────────┼───────────────────────────────────────┤
│                      ▼                                       │
│  ┌──────────────────────────────────────────┐               │
│  │         Core Modules                     │               │
│  ├──────────────────────────────────────────┤               │
│  │                                          │               │
│  │  1. Database (SQLite)                    │               │
│  │     └─► Stores products, videos, stats  │               │
│  │                                          │               │
│  │  2. Product Fetcher                     │               │
│  │     └─► TikTok Shop API / Demo Mode     │               │
│  │                                          │               │
│  │  3. Video Creator                       │               │
│  │     └─► MoviePy (images, text, music)    │               │
│  │                                          │               │
│  │  4. Caption Generator                   │               │
│  │     └─► AI (OpenAI/Claude) or Templates│               │
│  │                                          │               │
│  │  5. TikTok Uploader                     │               │
│  │     └─► Playwright (semi-automated)     │               │
│  │                                          │               │
│  └──────────────────────────────────────────┘               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Language**: Python 3.8+
- **GUI Framework**: Tkinter (built-in)
- **Video Processing**: MoviePy, Pillow, FFmpeg
- **Browser Automation**: Playwright
- **Database**: SQLite3
- **AI Integration**: OpenAI API, Anthropic Claude (optional)

---

## 🔧 Core Components

### 1. Database Module (`src/database.py`)

**Purpose**: Centralized data storage and management

**Key Features**:
- SQLite database with 4 tables: `products`, `videos`, `analytics`, `settings`
- Product lifecycle tracking (pending → selected → video_created)
- Video tracking with status (created → posted)
- Analytics aggregation for statistics

**Key Methods**:
```python
Database.add_product(product_data) -> int           # Add new product
Database.get_products(status=None) -> List[Dict]   # Get products (filtered)
Database.add_video(video_data) -> int              # Store video metadata
Database.update_video_post(video_id, url)          # Mark as posted
Database.get_stats() -> Dict                       # Aggregate statistics
Database.get_daily_post_count() -> int             # Safety check
```

**Database Schema**:
- `products`: product_id, name, price, commission_rate, status, etc.
- `videos`: product_id, video_path, caption, hashtags, status, tiktok_url
- `analytics`: video_id, views, likes, comments, revenue (future)
- `settings`: key-value configuration storage

---

### 2. Product Fetcher Module (`src/product_fetcher.py`)

**Purpose**: Fetch trending/high-commission products from TikTok Shop

**Current Implementation**:
- ✅ **Demo Mode**: Generates sample products (default)
- ⚠️ **API Mode**: Placeholder for TikTok Shop API (requires credentials)

**Key Methods**:
```python
ProductFetcher.fetch_trending_products(limit=20) -> List[Dict]
ProductFetcher._generate_demo_products(limit)      # Demo mode
ProductFetcher._fetch_via_api(limit)               # API mode (needs setup)
ProductFetcher._meets_criteria() -> bool           # Filter check
ProductFetcher.download_product_image(url, path)   # Image download
```

**Product Data Structure**:
```python
{
    'product_id': str,
    'name': str,
    'price': float,
    'commission_rate': float,      # percentage
    'commission_amount': float,     # calculated
    'category': str,
    'rating': float,
    'image_url': str,
    'affiliate_link': str,
    'status': 'pending' | 'selected' | 'video_created'
}
```

**Filters** (from `config/settings.py`):
- Minimum commission rate: 5%
- Price range: $5-$500
- Minimum rating: 4.0
- Categories: Electronics, Beauty, Fashion, Home, Fitness

---

### 3. Video Creator Module (`src/video_creator.py`)

**Purpose**: Generate TikTok-ready videos (9:16, 1080x1920)

**Technology**: MoviePy (video editing), Pillow (image processing)

**Video Composition Layers** (bottom to top):
1. **Background**: Gradient/solid color (template-based)
2. **Product Image**: Centered with zoom effect
3. **Text Overlays**: 
   - Product name (top)
   - Price (center-bottom, pulsing)
   - Commission earnings (below price)
   - Call-to-action (bottom, last 4 seconds)
4. **Logo Watermark**: Top-left corner (70% opacity)
5. **Background Music**: Random from `assets/music/*.mp3`

**Templates**:
- `modern`: Dark blue background
- `minimal`: White background
- `energetic`: Vibrant pink background

**Key Methods**:
```python
VideoCreator.create_product_video(product, output_path, template) -> bool
VideoCreator._create_background(template) -> ColorClip
VideoCreator._create_product_clip(product, template) -> ImageClip
VideoCreator._create_text_overlays(product, template) -> List[TextClip]
VideoCreator._add_watermark() -> ImageClip | None
VideoCreator._add_background_music(video) -> CompositeVideoClip
```

**Video Specifications**:
- Resolution: 1080x1920 (9:16 TikTok format)
- FPS: 30
- Duration: 15 seconds (configurable)
- Format: MP4 (H.264 codec, AAC audio)

**Dependencies**: Requires FFmpeg installed on system

---

### 4. Caption Generator Module (`src/caption_generator.py`)

**Purpose**: Generate engaging captions and hashtags

**Modes**:
1. **AI Mode**: Uses OpenAI GPT-3.5 or Claude Haiku (if API keys configured)
2. **Template Mode**: Fallback using pre-built templates

**Caption Strategy**:
- Hook viewers in first line
- Highlight main benefit
- Create urgency
- Clear call-to-action
- Emoji usage
- Under 150 characters

**Hashtag Generation**:
- Base tags: #TikTokShop, #TikTokAffiliate, #FoundItOnTikTok
- Category tags: #Electronics, #Beauty, etc.
- Product keywords from name
- Trending tags: #Viral, #FYP, #ForYou
- Price-based: #BudgetFriendly or #LuxuryFinds

**Key Methods**:
```python
CaptionGenerator.generate_caption(product) -> str
CaptionGenerator.generate_hashtags(product, count=5) -> List[str]
CaptionGenerator.create_full_post(product) -> Tuple[str, str]  # (caption, hashtags)
CaptionGenerator.create_multiple_variations(product, count=3)  # A/B testing
```

---

### 5. TikTok Uploader Module (`src/tiktok_uploader.py`)

**Purpose**: Semi-automated video posting to TikTok

**Technology**: Playwright (browser automation)

**Workflow**:
1. Launch Chromium browser (visible mode recommended)
2. Load saved cookies (if available)
3. Navigate to `tiktok.com/upload`
4. Check login status → manual login if needed
5. Upload video file
6. Auto-fill caption and hashtags
7. ⚠️ **WAIT FOR MANUAL REVIEW** (user clicks Post)
8. Capture video URL
9. Save cookies for future sessions

**Safety Features**:
- Cookie-based authentication (avoid repeated logins)
- Random delays (`_human_delay()`)
- Manual review step (prevents bans)
- Daily post limits (from `SAFETY_CONFIG`)
- Slow-motion mode (100ms delays)

**Key Methods**:
```python
TikTokUploader.login(manual=True) -> bool
TikTokUploader.upload_video(video_path, caption, hashtags, manual_review=True) -> str | None
TikTokUploader._is_logged_in() -> bool
SafetyChecker.can_post() -> Tuple[bool, str]
```

**Known Limitations**:
- TikTok UI changes frequently → selectors may break
- Requires manual intervention (by design, for safety)
- Cookie expiration (~30 days) → re-login needed

---

### 6. GUI Dashboard (`gui/dashboard.py`)

**Purpose**: User-friendly interface for all operations

**Technology**: Tkinter (Python's built-in GUI)

**Tabs**:
1. **Dashboard**: Statistics and quick actions
2. **Products**: View/manage products, select for videos
3. **Videos**: View created videos, track status
4. **Post to TikTok**: Posting interface with activity log
5. **Settings**: Configure credentials (TikTok, API keys)

**Key Features**:
- Real-time statistics display
- Product selection (multi-select)
- Video creation queue
- Settings management UI
- Activity logging

---

## 🔄 Data Flow

### Complete Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. PRODUCT DISCOVERY                                    │
└─────────────────────────────────────────────────────────┘
User clicks "Fetch Products"
    ↓
ProductFetcher.fetch_trending_products()
    ├─ Demo Mode → _generate_demo_products()
    └─ API Mode → _fetch_via_api() (if credentials exist)
    ↓
Filter by criteria (commission, price, rating)
    ↓
Database.add_product() → status: 'pending'
    ↓
Display in Products Tab (GUI)

┌─────────────────────────────────────────────────────────┐
│ 2. PRODUCT SELECTION                                    │
└─────────────────────────────────────────────────────────┘
User selects products (multi-select)
    ↓
Database.update_product_status() → status: 'selected'

┌─────────────────────────────────────────────────────────┐
│ 3. VIDEO CREATION                                       │
└─────────────────────────────────────────────────────────┘
User clicks "Create Videos"
    ↓
For each selected product:
    ├─ CaptionGenerator.create_full_post()
    │   └─ Generate caption + hashtags
    │
    ├─ VideoCreator.create_product_video()
    │   ├─ Load/download product image
    │   ├─ Create background
    │   ├─ Add product image with effects
    │   ├─ Add text overlays
    │   ├─ Add logo watermark
    │   ├─ Add background music
    │   └─ Render to MP4
    │
    └─ Database.add_video() → status: 'created'
        ↓
Save to data/videos/{product_id}_video.mp4

┌─────────────────────────────────────────────────────────┐
│ 4. POSTING TO TIKTOK                                    │
└─────────────────────────────────────────────────────────┘
User clicks "Post to TikTok"
    ↓
Safety Check (daily limit, timing)
    ↓
TikTokUploader.upload_video()
    ├─ Launch browser (Playwright)
    ├─ Login (if needed) → save cookies
    ├─ Navigate to upload page
    ├─ Upload video file
    ├─ Auto-fill caption
    ├─ Auto-fill hashtags
    └─ ⚠️ WAIT FOR USER → Manual Post Click
        ↓
Database.update_video_post() → status: 'posted', tiktok_url
    ↓
Display success message

┌─────────────────────────────────────────────────────────┐
│ 5. ANALYTICS (Future)                                    │
└─────────────────────────────────────────────────────────┘
Fetch video stats from TikTok API
    ↓
Database.add_analytics()
    ↓
Update Dashboard statistics
```

---

## 📁 File Structure

```
ClickTok/
├── main.py                      # Entry point (auto-setup, GUI/CLI launcher)
├── setup.py                     # One-command installation script
│
├── config/
│   ├── settings.py              # All configuration (paths, filters, AI, etc.)
│   └── credentials.json         # API keys (NOT in git, user creates)
│
├── src/                         # Core modules
│   ├── database.py              # SQLite database operations
│   ├── product_fetcher.py       # TikTok Shop product fetching
│   ├── video_creator.py         # Video generation (MoviePy)
│   ├── caption_generator.py     # Caption/hashtag generation
│   └── tiktok_uploader.py       # Browser automation (Playwright)
│
├── gui/
│   └── dashboard.py             # Tkinter GUI application
│
├── data/                        # Generated data
│   ├── products.db              # SQLite database
│   ├── products/                 # Downloaded product images
│   ├── videos/                   # Generated video files
│   └── tiktok_cookies.json      # Saved browser cookies
│
├── assets/                      # User-provided assets
│   ├── logo.png                 # Watermark logo
│   ├── music/                    # Background music (*.mp3)
│   └── fonts/                    # Custom fonts (optional)
│
├── logs/
│   └── system.log               # Application logs
│
├── requirements.txt             # Python dependencies
├── README.md                     # User documentation
├── ARCHITECTURE.md               # Technical architecture docs
└── AI_AGENT_GUIDE.md            # This file
```

---

## 🔑 Key Dependencies

### Required Packages

```python
# Core
requests>=2.31.0                 # HTTP requests
beautifulsoup4>=4.12.0          # HTML parsing
lxml>=4.9.0                     # XML/HTML parsing

# Video Processing
moviepy>=1.0.3,<2.0.0           # Video editing (critical!)
Pillow>=10.0.0                  # Image processing
opencv-python>=4.8.0             # Image/video utilities
imageio>=2.33.0                  # Image I/O
imageio-ffmpeg>=0.4.9            # FFmpeg wrapper

# Browser Automation
playwright>=1.40.0               # Browser automation
selenium>=4.15.0                 # Alternative browser automation

# AI (Optional)
openai>=1.0.0                    # OpenAI API
anthropic>=0.7.0                 # Claude API

# GUI
customtkinter>=5.2.0             # Modern Tkinter (optional)

# Utilities
python-dotenv>=1.0.0             # Environment variables
schedule>=1.2.0                  # Task scheduling
pandas>=2.0.0                    # Data manipulation
numpy>=1.24.0                    # Numerical operations
```

### System Requirements

- **Python**: 3.8+ (3.11 or 3.12 recommended, 3.13 works but newer)
- **FFmpeg**: Required for video processing (must be in PATH)
- **Playwright Browsers**: Chromium (installed via `playwright install`)

### Requirements Management

**Auto-Update Script**: `update_requirements.py`
- Automatically syncs `requirements.txt` with installed packages
- Maintains version constraints for critical packages
- Usage: `python update_requirements.py`
- See `SETUP_GUIDE.md` for details

**Smart Installation**: `install_and_setup.py`
- One-command setup with automatic requirements sync
- Usage: `python install_and_setup.py --sync`
- Better than original `setup.py` for keeping requirements updated

---

## ⚙️ Configuration System

### Configuration Files

#### 1. `config/settings.py`

**Main Configuration File** - All settings centralized here:

```python
# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
ASSETS_DIR = BASE_DIR / "assets"

# Video Settings
VIDEO_CONFIG = {
    "resolution": (1080, 1920),  # 9:16 for TikTok
    "fps": 30,
    "duration": 15,
    "codec": "libx264"
}

# Product Filters
PRODUCT_FILTERS = {
    "min_commission_rate": 5,     # percentage
    "min_price": 5,
    "max_price": 500,
    "min_rating": 4.0,
    "categories": ["Electronics", "Beauty", ...]
}

# AI Configuration
AI_CONFIG = {
    "provider": "openai",        # "openai" | "anthropic" | "local"
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
}

# Safety Limits
SAFETY_CONFIG = {
    "max_posts_per_day": 10,
    "min_delay_between_posts": 3600  # 1 hour
}
```

#### 2. `config/credentials.json`

**User-Created File** (not in git):

```json
{
  "tiktok": {
    "username": "your_username",
    "password": "your_password",
    "cookies_file": "data/tiktok_cookies.json"
  },
  "openai_api_key": "sk-...",
  "anthropic_api_key": "sk-ant-...",
  "tiktok_shop_api": {
    "app_key": "...",
    "app_secret": "...",
    "access_token": "..."
  }
}
```

**Note**: This file must be created by the user. The GUI Settings tab can help create it.

---

## ⚠️ Current State & Known Issues

### ✅ What Works

1. **Demo Mode**: Fully functional with sample products
2. **Video Creation**: Working with MoviePy (requires FFmpeg)
3. **Caption Generation**: Template mode works, AI mode needs API keys
4. **Database**: SQLite operations fully functional
5. **GUI**: All tabs and features working
6. **Setup Script**: Auto-installation working

### ⚠️ Known Issues / Limitations

1. **TikTok Shop API**: Not implemented (demo mode only)
   - Need official TikTok Shop API credentials
   - API documentation: https://partner.tiktokshop.com/
   - Current: Uses `_generate_demo_products()`

2. **TikTok Uploader**: Selectors may break
   - TikTok changes UI frequently
   - Selectors in `tiktok_uploader.py` may need updates
   - Manual intervention required (by design)

3. **AI Caption Generation**: Requires API keys
   - OpenAI: Needs `openai_api_key` in credentials
   - Anthropic: Needs `anthropic_api_key` in credentials
   - Falls back to templates if not configured

4. **FFmpeg Dependency**: Not auto-installed
   - Must be installed manually by user
   - `setup.py` checks but doesn't install

5. **MoviePy Compatibility**: Version 1.x required
   - MoviePy 2.x has breaking changes
   - Pinned to `<2.0.0` in requirements

---

## 🚀 Improvement Opportunities

### High Priority

1. **Error Handling**: Add try-catch blocks in GUI operations
2. **Logging**: More detailed logging for debugging
3. **Credentials Template**: Create `credentials.json.example`
4. **Video Preview**: Add preview window in GUI before posting
5. **Batch Operations**: Improve batch video creation with progress bar

### Medium Priority

1. **Real TikTok Shop Integration**: Implement actual API calls
2. **Analytics Dashboard**: Add charts/graphs for performance
3. **Scheduling**: Built-in post scheduling
4. **Multiple Accounts**: Support multiple TikTok accounts
5. **Video Templates**: More template options

### Low Priority / Future

1. **Cloud Deployment**: Docker containerization
2. **Mobile App**: React Native companion app
3. **Multi-Platform**: Instagram Reels, YouTube Shorts support
4. **Voiceovers**: ElevenLabs integration for voiceovers
5. **A/B Testing**: Automated caption/video testing

---

## 🎬 Quick Start Guide

### For AI Agents

If you need to understand or modify ClickTok, follow this workflow:

1. **Read Entry Point**: `main.py`
   - Auto-dependency checking
   - GUI/CLI launcher
   - Error handling

2. **Understand Core Modules** (in order):
   - `src/database.py` → Data structure
   - `config/settings.py` → Configuration
   - `src/product_fetcher.py` → Product data
   - `src/video_creator.py` → Video pipeline
   - `src/caption_generator.py` → Content generation
   - `src/tiktok_uploader.py` → Posting workflow

3. **GUI Flow**: `gui/dashboard.py`
   - Tab structure
   - Event handlers
   - Threading for long operations

4. **Testing**:
   - Run `python main.py` → GUI
   - Run `python main.py --cli` → CLI
   - Check `logs/system.log` for errors

### For Users

1. Run `python setup.py` or `setup.bat`
2. Create `config/credentials.json` (or use GUI Settings tab)
3. Add logo to `assets/logo.png`
4. Add music to `assets/music/*.mp3`
5. Run `python main.py`

---

## 📝 Code Patterns & Conventions

### Error Handling Pattern

```python
try:
    # Operation
    result = some_function()
    logger.info("Success")
    return result
except SpecificException as e:
    logger.error(f"Error: {e}", exc_info=True)
    return None  # or False
```

### Database Pattern

```python
conn = self.connect()
cursor = conn.cursor()
try:
    cursor.execute("SQL", (params,))
    conn.commit()
    return cursor.lastrowid
except sqlite3.IntegrityError:
    logger.warning("Already exists")
    return -1
```

### Threading Pattern (GUI)

```python
def long_operation(self):
    def task():
        try:
            # Long-running work
            result = do_work()
            # Update UI in main thread
            self.root.after(0, lambda: self.update_ui(result))
        except Exception as e:
            self.root.after(0, lambda: show_error(e))
    threading.Thread(target=task, daemon=True).start()
```

---

## 🔍 Debugging Tips

1. **Check Logs**: `logs/system.log`
2. **Enable Debug Mode**: Set `LOG_CONFIG['log_level'] = 'DEBUG'`
3. **GUI Logging**: Check "Post to TikTok" tab activity log
4. **Video Issues**: Verify FFmpeg installation (`ffmpeg -version`)
5. **Playwright Issues**: Run `python -m playwright install chromium`
6. **Database Issues**: Check `data/products.db` with SQLite browser

---

## 📚 Additional Resources

- **User Documentation**: `README.md`
- **Architecture Details**: `ARCHITECTURE.md`
- **Installation Guide**: `INSTALL.md`
- **Quick Reference**: `QUICK_REFERENCE.md`

---

## 🎯 Summary for AI Agents

**ClickTok is a Python-based TikTok affiliate marketing automation system that:**

1. **Fetches products** from TikTok Shop (demo mode currently)
2. **Creates videos** automatically using MoviePy (product images + text + music)
3. **Generates captions** using AI or templates
4. **Posts to TikTok** with manual review (Playwright automation)
5. **Tracks everything** in SQLite database

**Key Files to Modify**:
- `src/product_fetcher.py` → Add real TikTok Shop API integration
- `src/video_creator.py` → Add new video templates
- `src/caption_generator.py` → Improve AI prompts
- `src/tiktok_uploader.py` → Update selectors if TikTok UI changes
- `config/settings.py` → Adjust configuration

**Current Status**: ✅ Functional in demo mode, needs TikTok Shop API for production

---

**Last Updated**: 2024
**Version**: 1.0.0
**Maintainer**: See README.md

