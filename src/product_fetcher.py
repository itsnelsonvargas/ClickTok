"""
Product Fetcher Module
Fetches trending/high-commission products from TikTok Shop
"""
import requests
import json
import time
import logging
import re
from typing import List, Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import random

try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    logging.warning("Playwright not installed. Run: pip install playwright && playwright install")

logger = logging.getLogger(__name__)


class ProductFetcher:
    """Handles fetching products from TikTok Shop"""

    def __init__(self, credentials: Dict, filters: Dict):
        self.credentials = credentials
        self.filters = filters
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_trending_products(self, limit: int = 20, use_scraping: bool = True, on_product_found=None) -> List[Dict]:
        """
        Fetch trending/highest bought products from TikTok Shop
        
        SIMPLIFIED VERSION - Just click Fetch and get products!
        
        Args:
            limit: Maximum number of products to fetch
            use_scraping: If True, use web scraping when API unavailable (default: True)
            on_product_found: Callback function(product_dict) called when each product is found (for real-time display)
        
        Methods (in priority order):
        1. Official API (if credentials available)
        2. Smart Scraping - Auto-navigates to trending products (SIMPLIFIED!)
        3. Demo data (fallback only)
        """
        logger.info(f"Fetching up to {limit} highest bought products...")

        # Method 1: Official API (Recommended if available)
        if self._has_api_credentials():
            products = self._fetch_via_api(limit, on_product_found=on_product_found)
            if products:
                return products
            logger.warning("API fetch returned no products, falling back to scraping...")

        # Method 2: Smart Auto-Scraping (NEW - No manual navigation needed!)
        if use_scraping:
            logger.info("🔍 Auto-fetching highest bought products...")
            products = self._fetch_highest_bought_auto(limit, on_product_found=on_product_found)
            if products:
                logger.info(f"✅ Successfully fetched {len(products)} products!")
                return products
            logger.warning("Auto-scraping returned no products, trying manual scraping...")
            
            # Fallback to manual scraping
            products = self._fetch_via_scraping(limit, on_product_found=on_product_found)
            if products:
                return products

        # Method 3: Demo data (Fallback)
        logger.warning("Using demo products (scraping failed - try manual entry instead)")
        return self._generate_demo_products(limit, on_product_found=on_product_found)
    

    def _has_api_credentials(self) -> bool:
        """Check if API credentials are configured"""
        api_config = self.credentials.get('tiktok_shop_api', {})
        return bool(
            api_config.get('app_key') and
            api_config.get('app_secret') and
            api_config.get('access_token')
        )

    def _fetch_via_api(self, limit: int, on_product_found=None) -> List[Dict]:
        """
        Fetch products using official TikTok Shop API
        Documentation: https://partner.tiktokshop.com/doc/page/262
        """
        api_config = self.credentials.get('tiktok_shop_api', {})

        # API endpoint (example - check official docs)
        base_url = "https://open-api.tiktokglobalshop.com"
        endpoint = f"{base_url}/product/202309/products/search"

        params = {
            'app_key': api_config['app_key'],
            'access_token': api_config['access_token'],
            'page_size': limit,
            'sort_by': 'sales',  # or 'price', 'rating'
            'timestamp': int(time.time())
        }

        # Add signature (required by TikTok Shop API)
        # params['sign'] = self._generate_signature(params, api_config['app_secret'])

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 0:
                products = data.get('data', {}).get('products', [])
                return self._parse_api_products(products)
            else:
                logger.error(f"API Error: {data.get('message')}")
                return []

        except Exception as e:
            logger.error(f"Error fetching products via API: {e}")
            return []

    def _parse_api_products(self, raw_products: List[Dict]) -> List[Dict]:
        """Parse and filter products from API response"""
        products = []

        for item in raw_products:
            # Calculate commission
            price = float(item.get('price', 0))
            commission_rate = float(item.get('commission_rate', 0))
            commission_amount = price * (commission_rate / 100)

            # Apply filters
            if not self._meets_criteria(price, commission_rate, item.get('rating', 0)):
                continue

            product = {
                'product_id': item.get('product_id'),
                'name': item.get('product_name'),
                'description': item.get('description', ''),
                'price': price,
                'commission_rate': commission_rate,
                'commission_amount': commission_amount,
                'category': item.get('category_name', 'General'),
                'rating': item.get('rating', 0),
                'image_url': item.get('images', [{}])[0].get('url', ''),
                'affiliate_link': self._generate_affiliate_link(item.get('product_id')),
                'product_url': item.get('product_url', ''),
            }
            products.append(product)

        logger.info(f"Parsed {len(products)} products that meet criteria")
        return products

    def _generate_demo_products(self, limit: int, on_product_found=None) -> List[Dict]:
        """
        Generate demo products for testing
        Replace this with real API integration
        """
        categories = self.filters.get('categories', ['Electronics', 'Beauty', 'Fashion'])
        demo_products = []

        product_names = [
            "Wireless Bluetooth Earbuds Pro",
            "LED Makeup Mirror with Lights",
            "Portable Phone Charger 20000mAh",
            "Smart Watch Fitness Tracker",
            "Hair Straightener Brush",
            "Water Bottle with Time Marker",
            "Phone Ring Light for TikTok",
            "Resistance Bands Set",
            "Face Roller Jade Stone",
            "Laptop Stand Adjustable",
        ]

        for i in range(min(limit, len(product_names))):
            price = random.uniform(15, 150)
            commission_rate = random.uniform(8, 25)

            product = {
                'product_id': f'DEMO_{i+1:04d}',
                'name': product_names[i],
                'description': f'High-quality {product_names[i].lower()} with excellent reviews!',
                'price': round(price, 2),
                'commission_rate': round(commission_rate, 2),
                'commission_amount': round(price * commission_rate / 100, 2),
                'category': random.choice(categories),
                'rating': round(random.uniform(4.0, 5.0), 1),
                'image_url': f'https://via.placeholder.com/400x400?text={product_names[i][:20]}',
                'affiliate_link': f'https://tiktok.com/shop/product/{i+1}?affiliate=demo',
                'product_url': f'https://tiktok.com/shop/product/{i+1}',
            }
            demo_products.append(product)
            
            # Call callback if provided (for real-time display)
            if on_product_found:
                try:
                    on_product_found(product)
                except:
                    pass

        logger.info(f"Generated {len(demo_products)} demo products")
        return demo_products

    def _meets_criteria(self, price: float, commission_rate: float, rating: float) -> bool:
        """Check if product meets filtering criteria"""
        filters = self.filters

        if price < filters.get('min_price', 0):
            return False
        if price > filters.get('max_price', 1000):
            return False
        if commission_rate < filters.get('min_commission_rate', 0):
            return False
        if rating < filters.get('min_rating', 0):
            return False

        return True

    def _generate_affiliate_link(self, product_id: str) -> str:
        """Generate affiliate link for a product"""
        # This would use your TikTok affiliate ID
        # Example format (check TikTok's actual format)
        affiliate_id = self.credentials.get('tiktok', {}).get('affiliate_id', 'YOUR_ID')
        return f"https://www.tiktok.com/shop/product/{product_id}?affiliate={affiliate_id}"

    def download_product_image(self, image_url: str, save_path: Path) -> bool:
        """Download product image"""
        try:
            response = self.session.get(image_url, timeout=30)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded image to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return False

    def _fetch_highest_bought_auto(self, limit: int = 20, on_product_found=None) -> List[Dict]:
        """
        AUTOMATIC FETCH - No manual navigation needed!
        Searches TikTok for highest bought/trending products automatically
        Products are displayed in real-time via callback
        """
        try:
            from playwright.sync_api import sync_playwright
            
            logger.info("=" * 70)
            logger.info("🚀 AUTO-FETCHING HIGHEST BOUGHT PRODUCTS")
            logger.info("=" * 70)
            logger.info("Browser will open automatically...")
            logger.info("Products will appear in table as they're found! 📊")
            logger.info("=" * 70)
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, slow_mo=200)
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                )
                
                # Load cookies if available
                cookies_file = Path('data/tiktok_cookies.json')
                if cookies_file.exists():
                    try:
                        with open(cookies_file, 'r') as f:
                            cookies = json.load(f)
                            if cookies:
                                context.add_cookies(cookies)
                                logger.info("✅ Loaded saved cookies")
                    except:
                        pass
                
                page = context.new_page()
                products = []
                
                # Strategy: Search TikTok for trending product videos
                search_queries = [
                    "highest sold product tiktok shop",
                    "best selling item philippines",
                    "trending product philippines"
                ]
                
                for query in search_queries:
                    try:
                        logger.info(f"🔍 Searching: '{query}'...")
                        search_url = f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}"
                        
                        page.goto(search_url, wait_until='domcontentloaded', timeout=20000)
                        time.sleep(4)
                        
                        # Check if login required
                        if 'login' in page.url.lower():
                            logger.warning("⚠️  Login required. Waiting 30 seconds...")
                            time.sleep(30)
                            page.reload()
                            time.sleep(3)
                        
                        # Scroll to load videos
                        logger.info("📜 Loading videos...")
                        for i in range(5):
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(1.5)
                        
                        time.sleep(2)
                        
                        # Extract products - WITH REAL-TIME CALLBACK
                        extracted = self._extract_products_from_search_page(
                            page, 
                            limit - len(products),
                            on_product_found=on_product_found
                        )
                        
                        if extracted:
                            products.extend(extracted)
                            logger.info(f"✅ Found {len(extracted)} products")
                            # Note: Callback is already called in _extract_products_from_search_page
                        
                        if len(products) >= limit:
                            break
                            
                    except Exception as e:
                        logger.debug(f"Search '{query}' failed: {e}")
                        continue
                
                # Save cookies
                try:
                    cookies = context.cookies()
                    if cookies:
                        cookies_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(cookies_file, 'w') as f:
                            json.dump(cookies, f)
                except:
                    pass
                
                browser.close()
                
                if products:
                    products = self._sort_by_sales(products)
                    products = products[:limit]
                    logger.info(f"✅ Successfully fetched {len(products)} products!")
                
                return products
                
        except ImportError:
            logger.error("Playwright not installed!")
            return []
        except Exception as e:
            logger.error(f"Auto-fetch error: {e}", exc_info=True)
            return []
    
    def _extract_products_from_search_page(self, page: Page, limit: int, on_product_found=None) -> List[Dict]:
        """Extract products from TikTok search results - with real-time callback"""
        products = []
        
        try:
            # Find video links that might contain products
            video_links = page.query_selector_all('a[href*="/video/"]')
            logger.info(f"Found {len(video_links)} video links, analyzing for products...")
            
            for idx, video_link in enumerate(video_links[:min(20, limit * 3)]):
                try:
                    href = video_link.get_attribute('href')
                    if not href:
                        continue
                    
                    if href.startswith('/'):
                        href = f'https://www.tiktok.com{href}'
                    
                    # Check if video mentions products
                    try:
                        parent_text = video_link.evaluate('(el) => el.closest("div")?.textContent || ""')
                        if any(word in parent_text.lower() for word in ['shop', 'product', 'buy', 'sell', 'price', 'php', '$', '₱']):
                            product = self._extract_product_from_video_link(href, parent_text)
                            if product:
                                # Call callback FIRST (before filtering) so user sees all found products
                                if on_product_found:
                                    try:
                                        logger.info(f"  🔔 Calling callback for: {product['name']}")
                                        on_product_found(product)
                                    except Exception as e:
                                        logger.error(f"  ❌ Callback error: {e}", exc_info=True)
                                
                                # Then check if product meets criteria for adding to results
                                if self._meets_criteria(
                                    product.get('price', 0),
                                    product.get('commission_rate', 0),
                                    product.get('rating', 0)
                                ):
                                    products.append(product)
                                    logger.info(f"  ✅ Added product {len(products)}: {product['name']}")
                                else:
                                    logger.debug(f"  ⚠️ Product {product['name']} doesn't meet criteria")
                    except Exception as e:
                        logger.debug(f"Error checking video link: {e}")
                        continue
                        
                except Exception as e:
                    logger.debug(f"Error processing video: {e}")
                    continue
                
                if len(products) >= limit:
                    logger.info(f"Reached limit of {limit} products!")
                    break
            
        except Exception as e:
            logger.debug(f"Error extracting: {e}")
        
        return products[:limit]
    
    def _extract_product_from_video_link(self, video_url: str, context_text: str) -> Optional[Dict]:
        """Extract product info from video link"""
        try:
            import re
            
            # Extract product name
            name_match = re.search(r'(?:Buy|Get|Shop|Product)\s+([A-Z][a-zA-Z\s]+?)(?:\s*[-$]|\s*PHP|\s*₱|$)', context_text, re.IGNORECASE)
            price_match = re.search(r'(?:PHP|₱|\$)\s*([\d,]+\.?\d*)', context_text)
            
            name = name_match.group(1).strip() if name_match else "Trending Product"
            
            price = 10.0
            if price_match:
                try:
                    price_val = float(price_match.group(1).replace(',', ''))
                    price = price_val / 56 if price_val > 100 else price_val
                except:
                    pass
            
            product_id = f"AUTO_{abs(hash(video_url)) % 100000}"
            
            return {
                'product_id': product_id,
                'name': name[:100],
                'description': "Auto-extracted from trending TikTok video",
                'price': round(price, 2),
                'commission_rate': 10.0,
                'commission_amount': round(price * 0.10, 2),
                'category': 'General',
                'rating': 4.5,
                'image_url': '',
                'affiliate_link': video_url,
                'product_url': video_url,
                'sales_count': 100,
            }
        except:
            return None

    def _fetch_via_scraping(self, limit: int = 20, on_product_found=None) -> List[Dict]:
        """
        Fetch products from TikTok Shop using web scraping
        Extracts products sorted by highest sales/popularity
        
        Returns:
            List of product dictionaries sorted by sales volume
        """
        try:
            from playwright.sync_api import sync_playwright
            
            logger.info("=" * 60)
            logger.info("Starting web scraping to fetch highest bought products...")
            logger.info("Browser will open. You may need to log in if prompted.")
            logger.info("=" * 60)
            
            with sync_playwright() as p:
                # Launch browser with realistic settings
                browser = p.chromium.launch(
                    headless=False,  # Visible for better compatibility with TikTok
                    slow_mo=200  # Slow down to appear more human
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                    permissions=['geolocation'],
                    extra_http_headers={
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    }
                )
                
                # Load cookies if available (helps with authentication)
                cookies_file = Path('data/tiktok_cookies.json')
                if cookies_file.exists():
                    try:
                        with open(cookies_file, 'r') as f:
                            cookies = json.load(f)
                            if cookies:
                                context.add_cookies(cookies)
                                logger.info("✅ Loaded saved cookies for better access")
                    except Exception as e:
                        logger.debug(f"Could not load cookies: {e}")
                
                page = context.new_page()
                
                # First, navigate to TikTok homepage to establish session
                logger.info("📍 Navigating to TikTok homepage...")
                try:
                    page.goto('https://www.tiktok.com', wait_until='domcontentloaded', timeout=20000)
                    time.sleep(3)
                    
                    # Check if login is needed
                    if 'login' in page.url.lower() or 'signup' in page.url.lower():
                        logger.warning("⚠️  Login page detected. Please log in to TikTok in the browser window.")
                        logger.info("   Waiting 30 seconds for you to log in...")
                        logger.info("   After logging in, you can navigate to TikTok Shop manually.")
                        time.sleep(30)  # Give user time to log in
                    else:
                        logger.info("✅ Already logged in or no login required")
                except Exception as e:
                    logger.warning(f"Could not load homepage: {e}")
                    logger.info("   Continuing anyway...")
                
                # Try multiple TikTok Shop URLs and alternative methods
                shop_urls = [
                    'https://www.tiktok.com/shop',
                    'https://www.tiktok.com/affiliate',
                    'https://www.tiktok.com/search?q=shop',
                    'https://www.tiktok.com/search?q=product',
                ]
                
                products = []
                manual_navigation_allowed = False
                
                # First, try to detect if user wants manual navigation
                logger.info("🌐 Starting product discovery...")
                logger.info("   If TikTok Shop URLs don't work, you can manually navigate to any product page")
                
                for url in shop_urls:
                    try:
                        logger.info(f"🔍 Attempting to navigate to {url}...")
                        
                        # Use domcontentloaded instead of networkidle for faster loading
                        response = page.goto(url, wait_until='domcontentloaded', timeout=20000)
                        time.sleep(3)  # Wait for dynamic content to load
                        
                        # Check for 404 or redirect errors
                        current_url = page.url
                        status_code = response.status if response else None
                        
                        logger.info(f"   Final URL: {current_url}")
                        if status_code:
                            logger.info(f"   Status code: {status_code}")
                        
                        # Check if we hit a 404 page
                        if '404' in current_url or status_code == 404:
                            logger.warning(f"⚠️  URL returned 404: {current_url}")
                            logger.info("   Skipping this URL, trying alternatives...")
                            continue
                        
                        # Check page title for 404 indication
                        try:
                            page_title = page.title()
                            if '404' in page_title.lower() or 'not found' in page_title.lower():
                                logger.warning(f"⚠️  404 page detected by title: {page_title}")
                                continue
                        except:
                            pass
                        
                        # If redirected to login, wait for user
                        if 'login' in current_url.lower() or 'signup' in current_url.lower():
                            logger.warning("⚠️  Login page detected. Please log in in the browser window.")
                            logger.info("   Waiting 30 seconds for you to log in...")
                            logger.info("   After logging in, you can manually navigate to TikTok Shop or any product page.")
                            manual_navigation_allowed = True
                            time.sleep(30)  # Give user time to log in
                            current_url = page.url
                            logger.info(f"   Current URL after wait: {current_url}")
                        
                        # Check if user manually navigated to a product page
                        if '/shop/product/' in current_url or 'product' in current_url.lower():
                            logger.info("✅ Detected product page! Extracting products...")
                        
                        # Scroll to load more products (lazy loading)
                        logger.info("📜 Scrolling to load content...")
                        for i in range(5):
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(1.5)
                            logger.info(f"   Scroll {i+1}/5...")
                        
                        # Wait a bit more for content to load
                        time.sleep(2)
                        
                        # Try multiple extraction methods
                        logger.info("🔎 Extracting products from page...")
                        extracted = self._extract_products_from_page(page, limit - len(products))
                        
                        if extracted:
                            products.extend(extracted)
                            logger.info(f"✅ Found {len(extracted)} products from current page")
                        else:
                            logger.warning(f"⚠️  No products found on current page")
                            
                            # If this was a shop URL and no products found, allow manual navigation
                            if 'shop' in url or 'affiliate' in url:
                                if not manual_navigation_allowed:
                                    logger.info("💡 TIP: You can manually navigate to any TikTok Shop product page")
                                    logger.info("   The script will extract products from whatever page you're on")
                                    logger.info("   Waiting 15 seconds for manual navigation (or press Ctrl+C to skip)...")
                                    try:
                                        time.sleep(15)
                                        current_url = page.url
                                        if current_url != url:
                                            logger.info(f"   Detected navigation to: {current_url}")
                                            # Try extraction again from new page
                                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                            time.sleep(2)
                                            extracted = self._extract_products_from_page(page, limit - len(products))
                                            if extracted:
                                                products.extend(extracted)
                                                logger.info(f"✅ Found {len(extracted)} products from manually navigated page")
                                    except KeyboardInterrupt:
                                        logger.info("   Skipping manual navigation wait...")
                                    except:
                                        pass
                        
                        if len(products) >= limit:
                            logger.info(f"✅ Found enough products ({len(products)})!")
                            break
                        else:
                            logger.info("   Trying next method...")
                            
                    except Exception as e:
                        logger.warning(f"❌ Error with {url}: {e}")
                        logger.debug(f"   Details: {str(e)}", exc_info=True)
                        continue
                
                # If still no products, try searching TikTok for product-related content
                if not products and not manual_navigation_allowed:
                    logger.info("🔍 Trying alternative: Search TikTok for product videos...")
                    try:
                        search_urls = [
                            'https://www.tiktok.com/search?q=must%20have%20product',
                            'https://www.tiktok.com/search?q=amazon%20find',
                            'https://www.tiktok.com/search?q=shop%20now',
                        ]
                        
                        for search_url in search_urls[:1]:  # Try first search only
                            try:
                                logger.info(f"   Searching: {search_url}")
                                page.goto(search_url, wait_until='domcontentloaded', timeout=20000)
                                time.sleep(4)
                                
                                # Scroll to load videos
                                for i in range(3):
                                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                    time.sleep(2)
                                
                                # Look for product links in video descriptions
                                extracted = self._extract_products_from_videos(page, limit)
                                if extracted:
                                    products.extend(extracted)
                                    logger.info(f"✅ Found {len(extracted)} products from video search")
                                    break
                            except:
                                continue
                    except Exception as e:
                        logger.debug(f"Video search failed: {e}")
                
                # Save cookies for next time
                try:
                    cookies = context.cookies()
                    if cookies:
                        cookies_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(cookies_file, 'w') as f:
                            json.dump(cookies, f)
                        logger.info("💾 Saved cookies for next session")
                except Exception as e:
                    logger.debug(f"Could not save cookies: {e}")
                
                browser.close()
                logger.info("🔒 Browser closed")
                
                if not products:
                    logger.warning("⚠️  No products found. This could mean:")
                    logger.warning("   1. TikTok Shop is not available in your region")
                    logger.warning("   2. You need to log in first")
                    logger.warning("   3. TikTok changed their HTML structure")
                    return []
                
                # Sort by sales volume (highest first)
                products = self._sort_by_sales(products)
                logger.info(f"📊 Sorted {len(products)} products by sales volume")
                
                # Limit and filter
                products = products[:limit]
                filtered_before = len(products)
                products = [p for p in products if self._meets_criteria(
                    p.get('price', 0), 
                    p.get('commission_rate', 0), 
                    p.get('rating', 0)
                )]
                
                if filtered_before > len(products):
                    logger.info(f"🔍 Filtered products: {filtered_before} → {len(products)} (met criteria)")
                
                logger.info(f"✅ Successfully scraped {len(products)} products")
                return products
                
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright && playwright install")
            return []
        except Exception as e:
            logger.error(f"Web scraping error: {e}", exc_info=True)
            return []
    
    def _extract_products_from_page(self, page: Page, limit: int) -> List[Dict]:
        """
        Extract product data from TikTok Shop page
        Uses multiple strategies to handle TikTok's dynamic content
        """
        products = []
        
        try:
            # Strategy 1: Extract from embedded JSON data (most reliable)
            try:
                logger.debug("   Trying Strategy 1: Embedded JSON data...")
                # TikTok often embeds product data in script tags
                script_content = page.content()
                
                # Look for JSON-LD or embedded JSON structures
                json_patterns = [
                    r'__UNIVERSAL_DATA_FOR_REHYDRATION__\s*=\s*({.+?});',
                    r'window\.__UNIVERSAL_DATA_FOR_REHYDRATION__\s*=\s*({.+?});',
                    r'"products"\s*:\s*\[({.+?})\]',
                    r'productList.*?\[(.*?)\]',
                    r'\[{"id":.*?"price".*?}\]',  # Direct product array pattern
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    if matches:
                        logger.debug(f"     Found {len(matches)} JSON matches with pattern")
                    for match in matches[:5]:  # Limit matches to avoid timeout
                        try:
                            match_str = match if isinstance(match, str) else str(match)
                            if match_str.startswith('{'):
                                data = json.loads(match_str)
                            else:
                                # Try to parse as array or wrap in object
                                try:
                                    data = json.loads(f"[{match_str}]")
                                except:
                                    data = json.loads(f'{{"items": [{match_str}]}}')
                            
                            parsed = self._parse_embedded_json(data)
                            if parsed:
                                products.extend(parsed)
                                logger.info(f"     ✅ Extracted {len(parsed)} products from JSON data")
                        except json.JSONDecodeError as e:
                            logger.debug(f"     JSON decode error: {e}")
                            continue
                        except Exception as e:
                            logger.debug(f"     Error parsing JSON match: {e}")
                            continue
            except Exception as e:
                logger.debug(f"   Strategy 1 failed: {e}")
            
            # Strategy 2: Extract from HTML product cards
            try:
                logger.debug("   Trying Strategy 2: HTML product cards...")
                # Common TikTok Shop product card selectors (may need updates if UI changes)
                product_selectors = [
                    '[data-e2e="product-item"]',
                    '[data-e2e="product-card"]',
                    '[class*="product"]',
                    '[class*="ProductCard"]',
                    '[class*="Product"]',
                    'a[href*="/shop/product/"]',
                    'a[href*="tiktok.com/shop/product"]',
                ]
                
                for selector in product_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            logger.info(f"     ✅ Found {len(elements)} product elements with selector: {selector}")
                            count = 0
                            for elem in elements[:limit * 2]:  # Get more to filter later
                                product = self._parse_product_element(elem, page)
                                if product:
                                    products.append(product)
                                    count += 1
                            if count > 0:
                                logger.info(f"     ✅ Parsed {count} products from HTML")
                            break
                    except Exception as e:
                        logger.debug(f"     Selector {selector} failed: {e}")
                        continue
            except Exception as e:
                logger.debug(f"   Strategy 2 failed: {e}")
            
            # Strategy 3: Extract from page text and links
            try:
                logger.debug("   Trying Strategy 3: Product links...")
                # Get all product links
                links = page.query_selector_all('a[href*="/shop/product/"], a[href*="tiktok.com/shop/product"]')
                logger.debug(f"     Found {len(links)} product links")
                
                count = 0
                for link in links[:limit * 3]:  # Get more links, will filter later
                    try:
                        href = link.get_attribute('href')
                        if href and ('/shop/product/' in href or 'tiktok.com/shop/product' in href):
                            product_id = href.split('/shop/product/')[-1].split('?')[0].split('/')[-1]
                            if product_id and len(product_id) > 5:  # Filter out invalid IDs
                                # Try to get nearby text for product info
                                try:
                                    parent_text = link.evaluate('(element) => { const parent = element.closest("div"); return parent ? parent.textContent : ""; }')
                                    text = parent_text if parent_text else link.inner_text()
                                except:
                                    try:
                                        text = link.inner_text()
                                    except:
                                        text = ""
                                
                                product = self._extract_from_link_and_text(href, text)
                                if product:
                                    products.append(product)
                                    count += 1
                    except Exception as e:
                        logger.debug(f"     Error processing link: {e}")
                        continue
                
                if count > 0:
                    logger.info(f"     ✅ Extracted {count} products from links")
            except Exception as e:
                logger.debug(f"   Strategy 3 failed: {e}")
            
            # Remove duplicates based on product_id
            seen_ids = set()
            unique_products = []
            for p in products:
                pid = p.get('product_id') or p.get('name', '')
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    unique_products.append(p)
            
            return unique_products[:limit]
            
        except Exception as e:
            logger.error(f"Error extracting products from page: {e}", exc_info=True)
            return []
    
    def _extract_products_from_videos(self, page: Page, limit: int) -> List[Dict]:
        """
        Extract product links from TikTok video pages
        Many TikTok videos include product links in descriptions
        """
        products = []
        try:
            logger.debug("   Extracting products from video descriptions...")
            
            # Find all video links that might contain products
            video_links = page.query_selector_all('a[href*="/video/"]')
            logger.debug(f"     Found {len(video_links)} video links")
            
            # Visit a few videos to check for product links
            for video_link in video_links[:min(10, limit * 2)]:
                try:
                    href = video_link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Make full URL if needed
                    if href.startswith('/'):
                        href = f'https://www.tiktok.com{href}'
                    
                    # Navigate to video page
                    try:
                        video_page = page.context.new_page()
                        video_page.goto(href, wait_until='domcontentloaded', timeout=10000)
                        time.sleep(2)
                        
                        # Look for product links in video description or link section
                        product_links = video_page.query_selector_all('a[href*="/shop/product/"]')
                        for prod_link in product_links[:3]:  # Max 3 products per video
                            try:
                                prod_href = prod_link.get_attribute('href')
                                if prod_href:
                                    product = self._extract_from_link_and_text(prod_href, prod_link.inner_text())
                                    if product:
                                        products.append(product)
                            except:
                                continue
                        
                        video_page.close()
                        
                    except Exception as e:
                        logger.debug(f"     Could not process video {href}: {e}")
                        continue
                        
                except Exception as e:
                    logger.debug(f"     Error processing video link: {e}")
                    continue
                
                if len(products) >= limit:
                    break
            
            logger.info(f"     Extracted {len(products)} products from videos")
        except Exception as e:
            logger.debug(f"Error extracting from videos: {e}")
        
        return products[:limit]
    
    def _parse_embedded_json(self, data: dict) -> List[Dict]:
        """Parse product data from embedded JSON structures"""
        products = []
        
        try:
            # Recursively search for product data
            def find_products(obj, path=""):
                if isinstance(obj, dict):
                    # Check if this looks like a product object
                    if any(key in obj for key in ['productId', 'product_id', 'id', 'name', 'price']):
                        product = self._json_to_product(obj)
                        if product:
                            products.append(product)
                    
                    # Recursively search nested structures
                    for key, value in obj.items():
                        if key.lower() in ['products', 'items', 'data', 'list', 'results']:
                            find_products(value, f"{path}.{key}")
                        elif isinstance(value, (dict, list)):
                            find_products(value, f"{path}.{key}")
                            
                elif isinstance(obj, list):
                    for item in obj:
                        find_products(item, path)
            
            find_products(data)
            
        except Exception as e:
            logger.debug(f"Error parsing embedded JSON: {e}")
        
        return products
    
    def _json_to_product(self, obj: dict) -> Optional[Dict]:
        """Convert JSON object to product dictionary"""
        try:
            # Extract product ID
            product_id = (
                obj.get('productId') or 
                obj.get('product_id') or 
                obj.get('id') or 
                obj.get('itemId') or
                str(obj.get('skuId', ''))
            )
            
            if not product_id:
                return None
            
            # Extract name
            name = (
                obj.get('title') or 
                obj.get('name') or 
                obj.get('productName') or
                obj.get('displayName') or
                ''
            )
            
            # Extract price
            price_data = obj.get('price') or obj.get('priceInfo') or {}
            if isinstance(price_data, dict):
                price = float(price_data.get('value', price_data.get('amount', 0)) or 0)
            else:
                price = float(price_data or 0)
            
            # Extract sales/units sold (key for sorting by highest bought)
            sales_data = (
                obj.get('salesCount') or 
                obj.get('unitsSold') or 
                obj.get('sold') or
                obj.get('sales') or
                obj.get('volume') or
                0
            )
            if isinstance(sales_data, str):
                # Parse strings like "10K", "1.5M"
                sales_count = self._parse_count(sales_data)
            else:
                sales_count = int(sales_data or 0)
            
            # Extract rating
            rating_data = obj.get('rating') or obj.get('averageRating') or obj.get('score') or 0
            rating = float(rating_data or 0)
            
            # Extract commission rate (if available)
            commission_rate = float(obj.get('commissionRate') or obj.get('commission') or obj.get('affiliateRate', 10))
            
            # Extract image
            images = obj.get('images') or obj.get('imageUrls') or obj.get('gallery') or []
            image_url = ''
            if isinstance(images, list) and images:
                image_url = images[0] if isinstance(images[0], str) else images[0].get('url', '')
            elif isinstance(images, str):
                image_url = images
            
            # Extract category
            category = obj.get('category') or obj.get('categoryName') or obj.get('categoryPath') or 'General'
            if isinstance(category, list):
                category = category[-1] if category else 'General'
            
            # Extract URL
            product_url = obj.get('url') or obj.get('productUrl') or obj.get('link') or ''
            if product_url and not product_url.startswith('http'):
                product_url = f"https://www.tiktok.com{product_url}" if product_url.startswith('/') else f"https://www.tiktok.com/shop/product/{product_id}"
            
            product = {
                'product_id': str(product_id),
                'name': name or f"Product {product_id}",
                'description': obj.get('description') or obj.get('desc') or '',
                'price': round(price, 2),
                'commission_rate': round(commission_rate, 2),
                'commission_amount': round(price * commission_rate / 100, 2),
                'category': category,
                'rating': round(rating, 1),
                'image_url': image_url,
                'product_url': product_url or f"https://www.tiktok.com/shop/product/{product_id}",
                'affiliate_link': self._generate_affiliate_link(str(product_id)),
                'sales_count': sales_count,  # Key metric for sorting
            }
            
            return product
            
        except Exception as e:
            logger.debug(f"Error converting JSON to product: {e}")
            return None
    
    def _parse_product_element(self, element, page: Page) -> Optional[Dict]:
        """Parse product data from HTML element"""
        try:
            # Get product link - try query_selector first, then check if element itself is a link
            link_elem = None
            try:
                link_elem = element.query_selector('a[href*="/shop/product/"]')
            except:
                pass
            
            if not link_elem:
                # Check if element itself is a link
                try:
                    href_attr = element.get_attribute('href')
                    if href_attr and '/shop/product/' in href_attr:
                        link_elem = element
                except:
                    pass
            
            if not link_elem:
                return None
            
            try:
                href = link_elem.get_attribute('href')
                if not href or '/shop/product/' not in href:
                    return None
                
                product_id = href.split('/shop/product/')[-1].split('?')[0]
                
                # Get text content
                try:
                    text = element.inner_text()
                except:
                    try:
                        text = element.text_content()
                    except:
                        text = ""
                
                # Extract price
                price_match = re.search(r'\$?(\d+\.?\d*)', text)
                price = float(price_match.group(1)) if price_match else 0
                
                # Extract name (usually first line or in title attribute)
                try:
                    title = link_elem.get_attribute('title')
                except:
                    title = None
                name = title or (text.split('\n')[0].strip() if text else f"Product {product_id}")
                
                # Extract image
                image_url = ''
                try:
                    img_elem = element.query_selector('img')
                    if img_elem:
                        image_url = img_elem.get_attribute('src') or ''
                except:
                    pass
                
                product = {
                    'product_id': product_id,
                    'name': name,
                    'description': '',
                    'price': round(price, 2),
                    'commission_rate': 10.0,  # Default
                    'commission_amount': round(price * 0.10, 2),
                    'category': 'General',
                    'rating': 4.0,  # Default
                    'image_url': image_url,
                    'product_url': href if href.startswith('http') else f"https://www.tiktok.com{href}",
                    'affiliate_link': self._generate_affiliate_link(product_id),
                    'sales_count': 0,  # Will be updated if found
                }
                
                return product
            except Exception as e:
                logger.debug(f"Error extracting data from element: {e}")
                return None
            
        except Exception as e:
            logger.debug(f"Error parsing product element: {e}")
            return None
    
    def _extract_from_link_and_text(self, href: str, text: str) -> Optional[Dict]:
        """Extract product data from link and surrounding text"""
        try:
            product_id = href.split('/shop/product/')[-1].split('?')[0]
            if not product_id:
                return None
            
            # Extract price from text
            price_match = re.search(r'\$?(\d+\.?\d*)', text)
            price = float(price_match.group(1)) if price_match else 0
            
            # Extract name (first meaningful line)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            name = lines[0] if lines else f"Product {product_id}"
            
            # Try to extract sales count
            sales_patterns = [
                r'(\d+[KMB]?)\s*(?:sold|sales|bought|purchases)',
                r'(?:sold|sales|bought):\s*(\d+[KMB]?)',
                r'(\d+[KMB]?)\s*(?:units?|items?)',
            ]
            sales_count = 0
            for pattern in sales_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    sales_count = self._parse_count(match.group(1))
                    break
            
            product = {
                'product_id': product_id,
                'name': name,
                'description': '',
                'price': round(price, 2),
                'commission_rate': 10.0,
                'commission_amount': round(price * 0.10, 2),
                'category': 'General',
                'rating': 4.0,
                'image_url': '',
                'product_url': href if href.startswith('http') else f"https://www.tiktok.com{href}",
                'affiliate_link': self._generate_affiliate_link(product_id),
                'sales_count': sales_count,
            }
            
            return product
            
        except Exception as e:
            logger.debug(f"Error extracting from link and text: {e}")
            return None
    
    def _parse_count(self, text: str) -> int:
        """Parse count strings like '10K', '1.5M', '500'"""
        try:
            text = text.strip().upper().replace(',', '')
            if 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            elif 'B' in text:
                return int(float(text.replace('B', '')) * 1000000000)
            else:
                return int(float(text))
        except:
            return 0
    
    def _sort_by_sales(self, products: List[Dict]) -> List[Dict]:
        """Sort products by sales count (highest bought first)"""
        return sorted(
            products,
            key=lambda p: p.get('sales_count', 0),
            reverse=True
        )
    
    def search_products(self, query: str, limit: int = 10, use_scraping: bool = True) -> List[Dict]:
        """Search for specific products by keyword"""
        logger.info(f"Searching for: {query}")
        
        # Try API first if available
        if self._has_api_credentials():
            # TODO: Implement API search when signature generation is fixed
            pass
        
        # Use web scraping for search
        if use_scraping:
            try:
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=False, slow_mo=300)
                    context = browser.new_context(
                        viewport={'width': 1920, 'height': 1080},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    )
                    page = context.new_page()
                    
                    search_url = f"https://www.tiktok.com/shop/search?q={query.replace(' ', '+')}"
                    logger.info(f"Searching: {search_url}")
                    
                    page.goto(search_url, wait_until='networkidle', timeout=30000)
                    time.sleep(3)
                    
                    # Scroll to load results
                    for _ in range(2):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                    
                    products = self._extract_products_from_page(page, limit)
                    products = self._sort_by_sales(products)
                    
                    browser.close()
                    return products[:limit]
                    
            except Exception as e:
                logger.error(f"Search scraping error: {e}")
                return []
        
        return []


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Demo credentials
    credentials = {
        'tiktok_shop_api': {
            'app_key': '',
            'app_secret': '',
            'access_token': ''
        }
    }

    filters = {
        'min_commission_rate': 10,
        'min_price': 10,
        'max_price': 200,
        'min_rating': 4.0,
        'categories': ['Electronics', 'Beauty', 'Fashion']
    }

    fetcher = ProductFetcher(credentials, filters)
    products = fetcher.fetch_trending_products(limit=5)

    for product in products:
        print(f"\n{product['name']}")
        print(f"  Price: ${product['price']}")
        print(f"  Commission: {product['commission_rate']}% (${product['commission_amount']})")
        print(f"  Rating: {product['rating']}")
