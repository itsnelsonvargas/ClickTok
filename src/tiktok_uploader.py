"""
TikTok Uploader Module
Semi-automated TikTok video posting using Playwright
"""
import logging
import json
import time
import random
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, Page, Browser, expect
except ImportError:
    logging.warning("Playwright not installed. Run: pip install playwright && playwright install")

logger = logging.getLogger(__name__)


class TikTokUploader:
    """Handles semi-automated video uploads to TikTok"""

    def __init__(self, credentials: Dict, config: Dict):
        self.credentials = credentials
        self.config = config
        self.browser = None
        self.page = None
        self.cookies_file = Path(credentials.get('tiktok', {}).get('cookies_file', 'data/tiktok_cookies.json'))

    def login(self, manual: bool = True) -> bool:
        """
        Login to TikTok

        Args:
            manual: If True, waits for user to manually log in.
                   If False, attempts automated login (not recommended)

        Returns:
            True if login successful
        """
        try:
            logger.info("Starting TikTok login...")

            with sync_playwright() as p:
                # Launch browser
                self.browser = p.chromium.launch(
                    headless=self.config.get('headless', False),
                    slow_mo=100  # Slow down actions to appear more human
                )

                # Create context with realistic settings
                context = self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    locale='en-US',
                    timezone_id='America/New_York'
                )

                # Load cookies if available
                if self.cookies_file.exists():
                    with open(self.cookies_file, 'r') as f:
                        cookies = json.load(f)
                        context.add_cookies(cookies)
                        logger.info("Loaded saved cookies")

                self.page = context.new_page()

                # Navigate to TikTok
                self.page.goto('https://www.tiktok.com/login')
                time.sleep(2)

                if manual:
                    logger.info("=" * 50)
                    logger.info("MANUAL LOGIN REQUIRED")
                    logger.info("Please log in to TikTok in the browser window")
                    logger.info("Press ENTER here after you've logged in...")
                    logger.info("=" * 50)
                    input()

                    # Save cookies for future use
                    cookies = context.cookies()
                    self.cookies_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(self.cookies_file, 'w') as f:
                        json.dump(cookies, f)
                    logger.info("Cookies saved for future sessions")

                else:
                    # Automated login (risky - TikTok has strong bot detection)
                    success = self._automated_login()
                    if not success:
                        logger.error("Automated login failed")
                        return False

                # Verify login
                time.sleep(2)
                if self._is_logged_in():
                    logger.info("Successfully logged in to TikTok")
                    return True
                else:
                    logger.error("Login verification failed")
                    return False

        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return False

    def _automated_login(self) -> bool:
        """
        Automated login (NOT RECOMMENDED - use manual login instead)
        TikTok has strong anti-bot measures
        """
        logger.warning("Automated login is risky and may result in account ban")

        try:
            username = self.credentials.get('tiktok', {}).get('username')
            password = self.credentials.get('tiktok', {}).get('password')

            if not username or not password:
                logger.error("No credentials provided")
                return False

            # Click on "Use phone / email / username"
            self.page.click('text="Use phone / email / username"')
            time.sleep(1)

            # Click on "Log in with email or username"
            self.page.click('text="Log in with email or username"')
            time.sleep(1)

            # Enter credentials
            self.page.fill('input[name="username"]', username)
            self._human_delay()
            self.page.fill('input[type="password"]', password)
            self._human_delay()

            # Click login
            self.page.click('button[type="submit"]')
            time.sleep(5)

            return True

        except Exception as e:
            logger.error(f"Automated login failed: {e}")
            return False

    def _is_logged_in(self) -> bool:
        """Check if currently logged in"""
        try:
            # Check for upload button (only visible when logged in)
            self.page.goto('https://www.tiktok.com/upload')
            time.sleep(2)
            return 'upload' in self.page.url.lower()
        except:
            return False

    def upload_video(
        self,
        video_path: Path,
        caption: str,
        hashtags: str = "",
        manual_review: bool = True
    ) -> Optional[str]:
        """
        Upload video to TikTok (semi-automated)

        Args:
            video_path: Path to video file
            caption: Video caption
            hashtags: Hashtags string
            manual_review: If True, wait for user to click Post manually

        Returns:
            Video URL if successful, None otherwise
        """
        try:
            logger.info(f"Uploading video: {video_path.name}")

            with sync_playwright() as p:
                # Launch browser with saved session
                self.browser = p.chromium.launch(
                    headless=self.config.get('headless', False),
                    slow_mo=100
                )

                context = self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                # Load cookies
                if self.cookies_file.exists():
                    with open(self.cookies_file, 'r') as f:
                        cookies = json.load(f)
                        context.add_cookies(cookies)

                self.page = context.new_page()

                # Navigate to upload page
                self.page.goto('https://www.tiktok.com/upload')
                time.sleep(3)

                # Check if still logged in
                if not self._is_logged_in():
                    logger.error("Not logged in. Please run login() first")
                    return None

                # Upload video file
                logger.info("Selecting video file...")
                file_input = self.page.query_selector('input[type="file"]')
                if file_input:
                    file_input.set_input_files(str(video_path))
                    logger.info("Video file uploaded, processing...")
                    time.sleep(10)  # Wait for video to process
                else:
                    logger.error("Could not find file input")
                    return None

                # Fill caption
                logger.info("Entering caption...")
                full_caption = f"{caption}\n\n{hashtags}" if hashtags else caption

                # TikTok's caption editor (may need adjustment based on UI changes)
                caption_selectors = [
                    'div[contenteditable="true"]',
                    'div.public-DraftEditor-content',
                    'div[data-text="true"]'
                ]

                caption_filled = False
                for selector in caption_selectors:
                    try:
                        caption_box = self.page.query_selector(selector)
                        if caption_box:
                            caption_box.click()
                            self._human_delay()
                            caption_box.fill(full_caption)
                            caption_filled = True
                            logger.info("Caption entered")
                            break
                    except:
                        continue

                if not caption_filled:
                    logger.warning("Could not auto-fill caption. Please enter manually.")

                # Set privacy settings (optional)
                # You might want to check "Allow comments", "Allow duet", etc.

                if manual_review:
                    logger.info("=" * 50)
                    logger.info("REVIEW YOUR POST")
                    logger.info("1. Check the video preview")
                    logger.info("2. Review caption and hashtags")
                    logger.info("3. Adjust any settings")
                    logger.info("4. Click 'Post' when ready")
                    logger.info("5. Then press ENTER here...")
                    logger.info("=" * 50)
                    input()

                else:
                    # Auto-post (risky)
                    logger.info("Attempting to post automatically...")
                    post_button = self.page.query_selector('button:has-text("Post")')
                    if post_button:
                        self._human_delay()
                        post_button.click()
                        logger.info("Post button clicked")
                    else:
                        logger.error("Could not find Post button")
                        return None

                # Wait for post to complete
                logger.info("Waiting for post to complete...")
                time.sleep(10)

                # Try to get video URL
                video_url = self._get_latest_video_url()

                if video_url:
                    logger.info(f"Video posted successfully: {video_url}")
                else:
                    logger.warning("Could not retrieve video URL")
                    video_url = "Posted (URL not captured)"

                self.browser.close()
                return video_url

        except Exception as e:
            logger.error(f"Upload error: {e}", exc_info=True)
            if self.browser:
                self.browser.close()
            return None

    def _get_latest_video_url(self) -> Optional[str]:
        """Try to get the URL of the just-posted video"""
        try:
            # Navigate to profile
            self.page.goto('https://www.tiktok.com/@me')
            time.sleep(3)

            # Get first video link
            video_link = self.page.query_selector('a[href*="/video/"]')
            if video_link:
                url = video_link.get_attribute('href')
                if url:
                    return f"https://www.tiktok.com{url}" if not url.startswith('http') else url

        except Exception as e:
            logger.debug(f"Could not get video URL: {e}")

        return None

    def _human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add random delay to simulate human behavior"""
        delay = random.randint(min_ms, max_ms) / 1000
        time.sleep(delay)

    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
            self.browser = None


class SafetyChecker:
    """Check safety limits before posting"""

    def __init__(self, database, safety_config: Dict):
        self.db = database
        self.config = safety_config

    def can_post(self) -> Tuple[bool, str]:
        """
        Check if it's safe to post now

        Returns:
            (can_post, reason)
        """
        # Check daily post limit
        posts_today = self.db.get_daily_post_count()
        max_posts = self.config.get('max_posts_per_day', 10)

        if posts_today >= max_posts:
            return False, f"Daily limit reached ({posts_today}/{max_posts})"

        # Check minimum delay between posts
        # (You'd need to add this to database)
        # last_post_time = self.db.get_last_post_time()
        # min_delay = self.config.get('min_delay_between_posts', 3600)
        # ...

        return True, "OK to post"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    credentials = {
        'tiktok': {
            'username': 'your_username',
            'password': 'your_password',
            'cookies_file': 'data/tiktok_cookies.json'
        }
    }

    config = {
        'headless': False,
        'upload_timeout': 120
    }

    uploader = TikTokUploader(credentials, config)

    # First time: manual login
    # uploader.login(manual=True)

    # Upload a video
    # video_path = Path("data/videos/demo_video.mp4")
    # caption = "Amazing product! 🔥"
    # hashtags = "#TikTokShop #Affiliate"
    #
    # url = uploader.upload_video(video_path, caption, hashtags, manual_review=True)
    # print(f"Posted: {url}")
