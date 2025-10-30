# ClickTok System Architecture

Detailed technical architecture documentation.

---

## System Design Principles

1. **Modularity**: Each component is independent and can be used standalone
2. **Semi-Automation**: Human oversight for critical actions (posting)
3. **Extensibility**: Easy to add new features or integrations
4. **Safety-First**: Built-in limits and manual review to prevent bans
5. **Data-Driven**: All actions logged and tracked in database

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │  GUI Dashboard  │              │   CLI Interface │           │
│  │   (Tkinter)     │              │    (Argparse)   │           │
│  └────────┬────────┘              └────────┬────────┘           │
│           │                                │                     │
│           └────────────────┬───────────────┘                     │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
┌────────────────────────────┼──────────────────────────────────────┐
│                            │      Business Logic Layer            │
├────────────────────────────┼──────────────────────────────────────┤
│                            ▼                                      │
│  ┌──────────────────────────────────────────────────┐            │
│  │              Orchestration & Control              │            │
│  └───────┬───────┬──────────┬──────────┬────────────┘            │
│          │       │          │          │                          │
│   ┌──────▼──┐ ┌─▼──────┐ ┌─▼──────┐ ┌─▼──────────┐              │
│   │ Product │ │ Video  │ │Caption │ │  TikTok    │              │
│   │ Fetcher │ │Creator │ │  Gen   │ │  Uploader  │              │
│   └────┬────┘ └───┬────┘ └───┬────┘ └──────┬─────┘              │
│        │          │           │             │                     │
└────────┼──────────┼───────────┼─────────────┼─────────────────────┘
         │          │           │             │
┌────────┼──────────┼───────────┼─────────────┼─────────────────────┐
│        │          │           │             │    Service Layer     │
├────────┼──────────┼───────────┼─────────────┼─────────────────────┤
│        │          │           │             │                      │
│  ┌─────▼─────┐ ┌─▼─────┐  ┌──▼────┐   ┌────▼─────┐              │
│  │  HTTP     │ │MoviePy│  │ AI    │   │Playwright│              │
│  │ Requests  │ │  +    │  │ APIs  │   │Browser   │              │
│  │           │ │ PIL   │  │(GPT/  │   │Automation│              │
│  │           │ │       │  │Claude)│   │          │              │
│  └─────┬─────┘ └───┬───┘  └───────┘   └──────────┘              │
│        │           │                                              │
└────────┼───────────┼──────────────────────────────────────────────┘
         │           │
┌────────┼───────────┼──────────────────────────────────────────────┐
│        │           │              Data Layer                      │
├────────┼───────────┼──────────────────────────────────────────────┤
│        │           │                                              │
│  ┌─────▼─────┐ ┌───▼───────┐  ┌──────────────┐                  │
│  │  SQLite   │ │ File      │  │  External    │                  │
│  │  Database │ │ System    │  │  APIs        │                  │
│  │           │ │           │  │              │                  │
│  │ Products  │ │ Videos/   │  │ TikTok Shop  │                  │
│  │ Videos    │ │ Images/   │  │ OpenAI       │                  │
│  │ Analytics │ │ Assets    │  │ Anthropic    │                  │
│  └───────────┘ └───────────┘  └──────────────┘                  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Product Fetcher Module

**Purpose**: Fetch and filter products from TikTok Shop

**File**: `src/product_fetcher.py`

**Methods**:
- `fetch_trending_products()` - Get trending products
- `search_products()` - Search by keyword
- `download_product_image()` - Download product images
- `_meets_criteria()` - Filter products by criteria

**Data Flow**:
```
TikTok Shop API
    ↓
HTTP Request
    ↓
JSON Response
    ↓
Parse & Filter
    ↓
Product Objects
    ↓
Database Storage
```

**Dependencies**:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing (if scraping)

**Configuration**:
```python
PRODUCT_FILTERS = {
    "min_commission_rate": 10,
    "min_price": 10,
    "max_price": 200,
    "min_rating": 4.0,
    "categories": ["Electronics", "Beauty"]
}
```

---

### 2. Video Creator Module

**Purpose**: Generate professional TikTok videos

**File**: `src/video_creator.py`

**Key Methods**:
- `create_product_video()` - Main video creation
- `_create_background()` - Background layer
- `_create_product_clip()` - Product image with effects
- `_create_text_overlays()` - Text animations
- `_add_watermark()` - Logo overlay
- `_add_background_music()` - Audio layer

**Video Composition Layers**:
```
Layer 5: Logo/Watermark (top-left, 70% opacity)
Layer 4: Call-to-Action Text (bottom, animated)
Layer 3: Price Text (center-bottom, pulsing)
Layer 2: Product Name (top, static)
Layer 1: Product Image (center, zooming)
Layer 0: Background (gradient/solid color)
───────────────────────────────────────────
Audio: Background Music (30% volume)
```

**Video Pipeline**:
```
Product Data
    ↓
Generate Caption → Caption Generator
    ↓
Load Product Image
    ↓
Create Background Layer
    ↓
Add Product Image (with zoom effect)
    ↓
Add Text Overlays (name, price, CTA)
    ↓
Add Logo Watermark
    ↓
Composite All Layers
    ↓
Add Background Music
    ↓
Apply Transitions (fade in/out)
    ↓
Render to MP4
    ↓
Save to data/videos/
```

**Dependencies**:
- `moviepy` - Video editing
- `Pillow` - Image processing
- `numpy` - Array operations

**Configuration**:
```python
VIDEO_CONFIG = {
    "resolution": (1080, 1920),  # 9:16
    "fps": 30,
    "duration": 15,
    "format": "mp4",
    "codec": "libx264"
}
```

---

### 3. Caption Generator Module

**Purpose**: Create engaging captions and hashtags

**File**: `src/caption_generator.py`

**Modes**:

1. **AI Mode** (OpenAI/Anthropic):
   ```
   Product Data
       ↓
   Construct Prompt
       ↓
   API Request
       ↓
   AI-Generated Caption
   ```

2. **Template Mode** (Fallback):
   ```
   Product Data
       ↓
   Select Random Template
       ↓
   Fill Placeholders
       ↓
   Template Caption
   ```

**Hashtag Generation Logic**:
```
Base Tags (#TikTokShop, #Affiliate)
    +
Category Tags (#Electronics, #Tech)
    +
Product Keywords (#Wireless, #Earbuds)
    +
Trending Tags (#Viral, #FYP)
    +
Price-Based Tags (#BudgetFriendly)
    ↓
Deduplicate & Limit
    ↓
5-10 Hashtags
```

**Dependencies**:
- `openai` (optional) - OpenAI API
- `anthropic` (optional) - Claude API

---

### 4. TikTok Uploader Module

**Purpose**: Semi-automated video posting

**File**: `src/tiktok_uploader.py`

**Workflow**:
```
Initialize Playwright
    ↓
Launch Chromium Browser
    ↓
Load Saved Cookies (if exist)
    ↓
Navigate to tiktok.com/upload
    ↓
Check Login Status
    ↓
    ├─ Not Logged In → Manual Login → Save Cookies
    └─ Logged In → Continue
    ↓
Upload Video File
    ↓
Wait for Processing
    ↓
Auto-Fill Caption
    ↓
Auto-Fill Hashtags
    ↓
⚠️ MANUAL REVIEW (user clicks Post)
    ↓
Capture Video URL
    ↓
Update Database
```

**Safety Features**:
- Cookie-based authentication (avoid re-login)
- Random delays (simulate human behavior)
- Manual review before posting
- Daily post limits
- Timing randomization

**Dependencies**:
- `playwright` - Browser automation

---

### 5. Database Module

**Purpose**: Persistent data storage and tracking

**File**: `src/database.py`

**Schema**:

```sql
-- Products Table
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_id TEXT UNIQUE,
    name TEXT,
    price REAL,
    commission_rate REAL,
    commission_amount REAL,
    category TEXT,
    rating REAL,
    image_url TEXT,
    affiliate_link TEXT,
    date_added TIMESTAMP,
    status TEXT  -- 'pending', 'selected', 'video_created'
);

-- Videos Table
CREATE TABLE videos (
    id INTEGER PRIMARY KEY,
    product_id TEXT,
    video_path TEXT,
    caption TEXT,
    hashtags TEXT,
    tiktok_url TEXT,
    views INTEGER,
    likes INTEGER,
    date_created TIMESTAMP,
    date_posted TIMESTAMP,
    status TEXT,  -- 'created', 'posted', 'deleted'
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Analytics Table
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY,
    video_id INTEGER,
    date TIMESTAMP,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    revenue REAL,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);
```

**Key Methods**:
- `add_product()` - Store new product
- `get_products()` - Retrieve products
- `add_video()` - Store generated video
- `update_video_post()` - Update after posting
- `get_stats()` - Aggregate statistics

---

## Data Flow

### Complete User Journey

```
┌─────────────────────────────────────────────────────┐
│ 1. DISCOVERY PHASE                                  │
└─────────────────────────────────────────────────────┘
        │
        ▼
User Clicks "Fetch Products"
        │
        ▼
Product Fetcher → TikTok Shop API → Parse Response
        │
        ▼
Filter by Criteria (commission, price, rating)
        │
        ▼
Store in Database (status: 'pending')
        │
        ▼
Display in Products Table

┌─────────────────────────────────────────────────────┐
│ 2. SELECTION PHASE                                  │
└─────────────────────────────────────────────────────┘
        │
        ▼
User Reviews Products in GUI
        │
        ▼
User Selects Products
        │
        ▼
Update Database (status: 'selected')

┌─────────────────────────────────────────────────────┐
│ 3. CREATION PHASE                                   │
└─────────────────────────────────────────────────────┘
        │
        ▼
User Clicks "Create Videos"
        │
        ▼
For Each Selected Product:
    │
    ├─► Caption Generator → Generate Caption & Hashtags
    │
    ├─► Video Creator → Generate Video
    │       │
    │       ├─ Load Product Image
    │       ├─ Create Layers
    │       ├─ Add Music
    │       └─ Render MP4
    │
    └─► Database → Store Video Record (status: 'created')
        │
        ▼
Display in Videos Table

┌─────────────────────────────────────────────────────┐
│ 4. POSTING PHASE                                    │
└─────────────────────────────────────────────────────┘
        │
        ▼
User Clicks "Post to TikTok"
        │
        ▼
Safety Check:
    │
    ├─ Daily limit reached? → Error
    ├─ Too soon since last post? → Error
    └─ OK → Continue
        │
        ▼
For Each Video:
    │
    ├─► TikTok Uploader → Launch Browser
    │       │
    │       ├─ Login (if needed)
    │       ├─ Navigate to Upload
    │       ├─ Select Video File
    │       ├─ Auto-fill Caption
    │       ├─ Auto-fill Hashtags
    │       └─ ⚠️ WAIT FOR USER TO CLICK "POST"
    │
    └─► Database → Update (status: 'posted', tiktok_url)
        │
        ▼
Show Success Message

┌─────────────────────────────────────────────────────┐
│ 5. ANALYTICS PHASE                                  │
└─────────────────────────────────────────────────────┘
        │
        ▼
(Future) Fetch Video Stats from TikTok
        │
        ▼
Update Analytics Table
        │
        ▼
Display in Dashboard
```

---

## Security Architecture

### Credential Management

```
credentials.json (gitignored)
    │
    ├─► Encrypted at rest? (Future enhancement)
    │
    ├─► Loaded into memory
    │
    ├─► Passed to modules as needed
    │
    └─► Never logged or displayed
```

### Cookie Management

```
TikTok Login
    ↓
Browser Cookies
    ↓
Save to tiktok_cookies.json
    ↓
Reuse in future sessions
    ↓
(Expires after ~30 days)
```

### API Key Security

- Never commit to Git (.gitignore)
- Environment variables (alternative)
- Encrypted storage (future)

---

## Error Handling

### Error Propagation

```
Component Error
    ↓
Log to system.log
    ↓
Return False/None
    ↓
Caller checks return value
    ↓
Display user-friendly error
    ↓
Continue with next item (don't crash)
```

### Retry Logic

```
API Request Failed
    ↓
Retry with exponential backoff
    ↓
    ├─ Success → Continue
    └─ Max retries → Log error & skip
```

---

## Performance Considerations

### Video Rendering Optimization

- **Use lower resolution for faster rendering** (720p vs 1080p)
- **Limit FPS** (24 instead of 30)
- **Shorter videos** (10s instead of 15s)
- **Pre-process images** (resize once, reuse)
- **Background processing** (threads for video creation)

### Database Optimization

- **Indexes** on frequently queried fields
- **Batch inserts** for multiple products
- **Connection pooling** for concurrent access

### Memory Management

- **Close video clips** after rendering
- **Clear temp files** after use
- **Limit concurrent video generation**

---

## Extensibility Points

### Adding New Video Templates

```python
# src/video_creator.py

def create_custom_template(self, product):
    # Your template logic
    pass

# Register template
TEMPLATES = {
    'modern': self._create_modern_template,
    'minimal': self._create_minimal_template,
    'custom': self.create_custom_template
}
```

### Adding New AI Providers

```python
# src/caption_generator.py

def _init_custom_ai(self):
    # Initialize your AI provider
    pass

# Use in generate_caption()
if provider == 'custom':
    return self._generate_custom_ai_caption(product)
```

### Adding New Data Sources

```python
# src/product_fetcher.py

def fetch_from_custom_source(self):
    # Fetch from your source
    products = []
    # ... fetch logic
    return self._parse_custom_products(products)
```

---

## Testing Strategy

### Unit Tests (Future)

```python
# tests/test_product_fetcher.py
def test_fetch_products():
    fetcher = ProductFetcher(credentials, filters)
    products = fetcher.fetch_trending_products(limit=5)
    assert len(products) <= 5
    assert all('product_id' in p for p in products)
```

### Integration Tests

```python
# tests/test_workflow.py
def test_full_workflow():
    # Fetch → Create → Post pipeline
    pass
```

---

## Deployment Options

### Local (Current)

```
Windows/Mac/Linux Desktop
    ↓
Python + Dependencies
    ↓
SQLite Database
    ↓
Local File Storage
```

### Cloud (Future)

```
AWS EC2 / DigitalOcean
    ↓
Headless Browser (Playwright)
    ↓
S3 Storage (Videos)
    ↓
RDS (Database)
    ↓
Scheduled Jobs (Cron)
```

---

## Monitoring & Logging

### Log Levels

```
DEBUG   → Detailed debugging info
INFO    → General information
WARNING → Potential issues
ERROR   → Error occurred but continued
CRITICAL→ System failure
```

### What Gets Logged

- All API requests/responses
- Video creation steps
- Database operations
- TikTok upload attempts
- Errors and exceptions

### Log File Rotation (Future)

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/system.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

---

## Future Enhancements

### Phase 2
- [ ] Multi-account support
- [ ] Advanced analytics dashboard
- [ ] A/B testing automation
- [ ] Scheduled posting

### Phase 3
- [ ] Instagram Reels integration
- [ ] YouTube Shorts integration
- [ ] Cloud deployment
- [ ] Mobile app

### Phase 4
- [ ] AI-powered optimization
- [ ] Automated product discovery
- [ ] Revenue tracking
- [ ] Team collaboration features

---

**This architecture is designed to be simple, extensible, and safe for affiliate marketing at scale.**
