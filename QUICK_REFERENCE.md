# ClickTok Quick Reference

Fast reference guide for common tasks and commands.

---

## Installation (Quick)

**One Command (Recommended):**
```bash
cd ClickTok
setup.bat         # Windows
./setup.sh        # Mac/Linux
python setup.py   # Any OS
```

**Or manual:**
```bash
pip install -r requirements.txt
python -m playwright install chromium
python main.py
```

---

## Common Commands

### Launch GUI

**Easiest (Windows):**
```bash
Double-click: ClickTok.bat
```

**Command line:**
```bash
python main.py
```

### Launch CLI

**Easiest (Windows):**
```bash
Double-click: ClickTok-CLI.bat
```

**Command line:**
```bash
python main.py --cli
```

### Check Version
```bash
python main.py --version
```

---

## File Locations

| What | Where |
|------|-------|
| Products Database | `data/products.db` |
| Generated Videos | `data/videos/` |
| Product Images | `data/products/` |
| Configuration | `config/settings.py` |
| Credentials | `config/credentials.json` |
| Logs | `logs/system.log` |
| Assets (Logo/Music) | `assets/` |

---

## Workflow Cheatsheet

```
1. Fetch Products    → Dashboard → "Fetch New Products"
2. Select Products   → Products Tab → Select → "Select for Videos"
3. Create Videos     → Videos Tab → "Create Videos"
4. Review Videos     → Open data/videos/ folder
5. Post to TikTok    → Post Tab → "Post Videos" → Review → Post
```

---

## Configuration Quick Edits

### Change Video Duration
`config/settings.py`:
```python
VIDEO_CONFIG = {
    "duration": 10,  # 10 seconds instead of 15
}
```

### Change Daily Post Limit
```python
SAFETY_CONFIG = {
    "max_posts_per_day": 5,  # Max 5 posts/day
}
```

### Change Commission Filter
```python
PRODUCT_FILTERS = {
    "min_commission_rate": 15,  # Min 15% commission
}
```

### Enable AI Captions
```python
AI_CONFIG = {
    "provider": "openai",  # or "anthropic"
    "model": "gpt-3.5-turbo"
}
```

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| FFmpeg not found | Install FFmpeg, add to PATH |
| Browser doesn't open | `playwright install chromium` |
| Login fails | Use manual login, clear cookies |
| Video creation fails | Check assets/, logs/system.log |
| Slow rendering | Lower resolution, FPS, duration |

---

## Database Queries

Open database: `sqlite3 data/products.db`

### View All Products
```sql
SELECT product_id, name, price, commission_rate, status FROM products;
```

### View All Videos
```sql
SELECT id, product_id, status, date_created FROM videos;
```

### Get Statistics
```sql
SELECT
    COUNT(*) as total_products,
    (SELECT COUNT(*) FROM videos) as total_videos,
    (SELECT COUNT(*) FROM videos WHERE status='posted') as posted_videos
FROM products;
```

---

## API Usage Examples

### Fetch Products Programmatically

```python
from src.product_fetcher import ProductFetcher
import json

with open("config/credentials.json") as f:
    creds = json.load(f)

filters = {"min_commission_rate": 10}
fetcher = ProductFetcher(creds, filters)
products = fetcher.fetch_trending_products(limit=10)

for p in products:
    print(f"{p['name']} - ${p['price']}")
```

### Create Single Video

```python
from src.video_creator import VideoCreator
from config.settings import VIDEO_CONFIG, ASSETS_DIR, VIDEOS_DIR

product = {
    'product_id': 'TEST_001',
    'name': 'Test Product',
    'price': 29.99,
    'commission_rate': 15.0,
    'commission_amount': 4.50,
    'rating': 4.5
}

creator = VideoCreator(VIDEO_CONFIG, ASSETS_DIR)
output_path = VIDEOS_DIR / "test_video.mp4"
creator.create_product_video(product, output_path)
```

### Generate Caption

```python
from src.caption_generator import CaptionGenerator
from config.settings import AI_CONFIG, HASHTAG_CONFIG

product = {'name': 'Wireless Earbuds', 'price': 49.99, ...}
generator = CaptionGenerator(AI_CONFIG, HASHTAG_CONFIG, {})
caption, hashtags = generator.create_full_post(product)

print(caption)
print(hashtags)
```

---

## Environment Variables (Alternative to credentials.json)

```bash
# .env file
TIKTOK_USERNAME=your_username
TIKTOK_PASSWORD=your_password
OPENAI_API_KEY=sk-...
```

```python
# Use in code
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('TIKTOK_USERNAME')
```

---

## Keyboard Shortcuts (GUI)

| Action | Shortcut |
|--------|----------|
| Refresh | F5 |
| Close Window | Alt+F4 (Windows), Cmd+Q (Mac) |

---

## Video Templates

Change template in `src/video_creator.py`:

```python
# Modern: Dark background, professional
creator.create_product_video(product, path, template="modern")

# Minimal: White background, clean
creator.create_product_video(product, path, template="minimal")

# Energetic: Vibrant colors, dynamic
creator.create_product_video(product, path, template="energetic")
```

---

## Caption Templates

Located in `src/caption_generator.py`:

```python
templates = [
    "🔥 OMG! You NEED this {name}! Only ${price}! {cta}",
    "✨ Best {category} product I've found! {name} for just ${price}! {cta}",
    # Add your own templates here
]
```

---

## Backup & Restore

### Backup Database
```bash
cp data/products.db data/products_backup_$(date +%Y%m%d).db
```

### Restore Database
```bash
cp data/products_backup_20240101.db data/products.db
```

---

## Performance Benchmarks

Typical performance on mid-range PC:

| Task | Time |
|------|------|
| Fetch 20 products | 5-10 seconds |
| Generate 1 video | 30-60 seconds |
| Post to TikTok | 30-60 seconds (manual) |
| Database query | <1 second |

---

## Best Practices Checklist

- [ ] Post 3-5 times per day (not more)
- [ ] Vary posting times
- [ ] Always review videos before posting
- [ ] Use trending hashtags
- [ ] Respond to comments
- [ ] Track what works
- [ ] Test different templates
- [ ] Update music regularly
- [ ] Monitor affiliate clicks
- [ ] Stay compliant with TikTok TOS

---

## Safety Limits

**Default Settings:**
- Max posts per day: 10
- Min delay between posts: 1 hour
- Manual review: ALWAYS enabled

**Recommended Settings:**
- Max posts per day: 3-5
- Min delay: 2-3 hours
- Vary posting times: Yes

---

## Getting Help

1. Check `logs/system.log`
2. Read [README.md](README.md)
3. Review [SETUP_GUIDE.md](SETUP_GUIDE.md)
4. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

---

## Useful Links

- TikTok Shop Partner: https://partner.tiktokshop.com/
- TikTok Creator Portal: https://www.tiktok.com/creators/
- OpenAI API: https://platform.openai.com/
- Anthropic API: https://console.anthropic.com/
- MoviePy Docs: https://zulko.github.io/moviepy/
- Playwright Docs: https://playwright.dev/python/

---

## Version History

- **v1.0.0** (Initial Release)
  - Product fetching
  - Video creation
  - Caption generation
  - Semi-automated posting
  - GUI dashboard
  - Database tracking

---

**Keep this file bookmarked for quick reference! 🔖**
