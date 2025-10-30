"""
ClickTok Configuration Settings
"""
import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory Paths
DATA_DIR = BASE_DIR / "data"
PRODUCTS_DIR = DATA_DIR / "products"
VIDEOS_DIR = DATA_DIR / "videos"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"
LOGS_DIR = BASE_DIR / "logs"

# Database
DATABASE_PATH = DATA_DIR / "products.db"

# Video Settings
VIDEO_CONFIG = {
    "resolution": (1080, 1920),  # 9:16 for TikTok
    "fps": 30,
    "duration": 15,  # seconds
    "format": "mp4",
    "codec": "libx264",
    "audio_codec": "aac",
    "bitrate": "8000k"
}

# Text Overlay Settings
TEXT_CONFIG = {
    "font_size": 60,
    "font_color": "white",
    "stroke_color": "black",
    "stroke_width": 2,
    "position": "center",
    "duration": 3  # seconds per text
}

# TikTok Settings
TIKTOK_CONFIG = {
    "max_caption_length": 2200,
    "max_hashtags": 30,
    "upload_timeout": 120,  # seconds
    "headless": False,  # Set True to hide browser
}

# Product Selection Criteria
PRODUCT_FILTERS = {
    "min_commission_rate": 5,  # minimum percentage
    "min_price": 5,  # USD
    "max_price": 500,  # USD
    "min_rating": 4.0,
    "categories": ["Electronics", "Beauty", "Fashion", "Home", "Fitness"]
}

# Hashtag Strategy
HASHTAG_CONFIG = {
    "base_tags": ["#TikTokShop", "#TikTokAffiliate", "#FoundItOnTikTok"],
    "max_hashtags_per_post": 5,
    "trending_check": True
}

# AI Caption Generation (if using OpenAI/Claude)
AI_CONFIG = {
    "provider": "openai",  # "openai" or "anthropic" or "local"
    "model": "gpt-3.5-turbo",  # or "claude-3-haiku-20240307"
    "temperature": 0.7,
    "max_tokens": 150
}

# Automation Safety
SAFETY_CONFIG = {
    "min_delay_between_posts": 3600,  # 1 hour in seconds
    "max_posts_per_day": 10,
    "randomize_timing": True,
    "human_behavior_simulation": True
}

# Logging
LOG_CONFIG = {
    "log_file": LOGS_DIR / "system.log",
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Create directories if they don't exist
for directory in [DATA_DIR, PRODUCTS_DIR, VIDEOS_DIR, ASSETS_DIR,
                  MUSIC_DIR, FONTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
