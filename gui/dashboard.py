"""
ClickTok GUI Dashboard
Main user interface for managing the TikTok automation system
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
import threading
import logging
import time
import random
import csv
from typing import Dict, Optional
import sys
import json
import os
import requests
import webbrowser

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database
from src.product_fetcher import ProductFetcher
from src.video_creator import VideoCreator
from src.caption_generator import CaptionGenerator
from src.tiktok_uploader import TikTokUploader
from config.settings import *

logger = logging.getLogger(__name__)


class ClickTokDashboard:
    """Main GUI Dashboard"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClickTok - TikTok Affiliate Automation")
        self.root.geometry("1200x800")

        # Load credentials
        self.credentials = self._load_credentials()

        # Initialize components
        self.db = Database(DATABASE_PATH)
        self.product_fetcher = ProductFetcher(self.credentials, PRODUCT_FILTERS)
        self.video_creator = VideoCreator(VIDEO_CONFIG, ASSETS_DIR)
        self.caption_generator = CaptionGenerator(AI_CONFIG, HASHTAG_CONFIG, self.credentials)
        self.uploader = TikTokUploader(self.credentials, TIKTOK_CONFIG)

        # Setup UI
        self.setup_ui()

        # Load initial data
        self.refresh_products()
        self.update_stats()
        
        # Initialize script tab product list
        self.refresh_script_product_list()

    def _load_credentials(self) -> Dict:
        """Load credentials from config file or .env file (prioritizes .env)"""
        creds = {}
        
        # Check .env file first (priority)
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            try:
                env_vars = {}
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            env_vars[key] = value
                            # Debug logging for OpenAI key
                            if key == 'OPENAI_API_KEY':
                                logger.info(f"Found OPENAI_API_KEY in .env (line {line_num}): length={len(value)}, starts_with={value[:7] if len(value) >= 7 else 'short'}")
                
                logger.info(f"Loaded {len(env_vars)} environment variables from .env")
                
                # Convert .env format to credentials.json format
                if 'TIKTOK_USERNAME' in env_vars or 'TIKTOK_PASSWORD' in env_vars:
                    creds['tiktok'] = {
                        'username': env_vars.get('TIKTOK_USERNAME', ''),
                        'password': env_vars.get('TIKTOK_PASSWORD', ''),
                        'cookies_file': env_vars.get('TIKTOK_COOKIES_FILE', 'data/tiktok_cookies.json')
                    }
                
                if 'OPENAI_API_KEY' in env_vars:
                    key_value = env_vars['OPENAI_API_KEY'].strip()
                    if key_value:
                        creds['openai_api_key'] = key_value
                        logger.info(f"Loaded OpenAI API key from .env (length: {len(key_value)})")
                
                if 'ANTHROPIC_API_KEY' in env_vars:
                    creds['anthropic_api_key'] = env_vars['ANTHROPIC_API_KEY']
                
                if 'GROQ_API_KEY' in env_vars:
                    key_value = env_vars['GROQ_API_KEY'].strip()
                    if key_value:
                        creds['groq_api_key'] = key_value
                        logger.info(f"Loaded Groq API key from .env (length: {len(key_value)})")
                
                if 'APIFY_API_KEY' in env_vars:
                    key_value = env_vars['APIFY_API_KEY'].strip()
                    if key_value:
                        creds['apify_api_key'] = key_value
                        logger.info(f"Loaded Apify API key from .env (length: {len(key_value)})")
                
                if 'APIFY_USER_ID' in env_vars:
                    key_value = env_vars['APIFY_USER_ID'].strip()
                    if key_value:
                        creds['apify_user_id'] = key_value
                        logger.info(f"Loaded Apify User ID from .env")
                
                if 'APIFY_ACTOR_ID' in env_vars:
                    key_value = env_vars['APIFY_ACTOR_ID'].strip()
                    if key_value:
                        creds['apify_actor_id'] = key_value
                        logger.info(f"Loaded Apify Actor ID from .env")
                
                if 'ELEVENLABS_API_KEY' in env_vars:
                    creds['elevenlabs_api_key'] = env_vars['ELEVENLABS_API_KEY']
                
                if any(k.startswith('TIKTOK_SHOP_') for k in env_vars.keys()):
                    creds['tiktok_shop_api'] = {
                        'app_key': env_vars.get('TIKTOK_SHOP_APP_KEY', ''),
                        'app_secret': env_vars.get('TIKTOK_SHOP_APP_SECRET', ''),
                        'access_token': env_vars.get('TIKTOK_SHOP_ACCESS_TOKEN', '')
                    }
                
                logger.info("Loaded credentials from .env file")
                # Don't return yet - merge with credentials.json if it exists
                cred_file = BASE_DIR / "config" / "credentials.json"
                if cred_file.exists():
                    try:
                        with open(cred_file, 'r') as f:
                            json_creds = json.load(f)
                            # Merge: .env takes priority, but fill in missing keys from json
                            for key, value in json_creds.items():
                                if key not in creds:
                                    creds[key] = value
                        logger.info("Merged credentials from .env and credentials.json")
                    except Exception as e:
                        logger.warning(f"Could not merge credentials.json: {e}")
                
                return creds
            except Exception as e:
                logger.warning(f"Could not load from .env: {e}")
        
        # Fall back to credentials.json
        cred_file = BASE_DIR / "config" / "credentials.json"
        try:
            with open(cred_file, 'r') as f:
                creds = json.load(f)
                logger.info("Loaded credentials from credentials.json")
                return creds
        except Exception as e:
            logger.error(f"Could not load credentials: {e}")
            return {}
    
    def _reload_credentials_and_ai(self):
        """Reload credentials and reinitialize AI clients"""
        self.credentials = self._load_credentials()
        # Check if OpenAI key is present
        openai_key = self.credentials.get('openai_api_key', '').strip()
        if openai_key:
            logger.info(f"Reloading OpenAI client with key (length: {len(openai_key)}, starts with: {openai_key[:7]}...)")
        else:
            logger.warning("No OpenAI API key found in credentials after reload")
        # Reinitialize caption generator with new credentials
        self.caption_generator = CaptionGenerator(AI_CONFIG, HASHTAG_CONFIG, self.credentials)
        # Also update product_fetcher credentials
        self.product_fetcher.credentials = self.credentials
        logger.info("Credentials reloaded and AI clients reinitialized")

    def setup_ui(self):
        """Setup the main UI layout"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_dashboard_tab()
        self.create_products_tab()
        self.create_videos_tab()
        self.create_script_tab()
        self.create_posting_tab()
        self.create_settings_tab()

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_dashboard_tab(self):
        """Main dashboard"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard")

        title = tk.Label(tab, text="ClickTok Dashboard", font=('Arial', 24, 'bold'))
        title.pack(pady=20)

        # Stats
        stats_frame = ttk.LabelFrame(tab, text="Statistics", padding=20)
        stats_frame.pack(fill='x', padx=20, pady=10)

        self.stats_vars = {}
        stats = [('Total Products', 'total_products'), ('Videos Created', 'total_videos'),
                 ('Videos Posted', 'posted_videos'), ('Total Views', 'total_views')]

        for i, (label, key) in enumerate(stats):
            frame = tk.Frame(stats_frame)
            frame.grid(row=i//2, column=i%2, padx=40, pady=10)
            tk.Label(frame, text=label, font=('Arial', 10)).pack()
            var = tk.StringVar(value="0")
            self.stats_vars[key] = var
            tk.Label(frame, textvariable=var, font=('Arial', 20, 'bold'), fg='blue').pack()

        # Quick Actions
        actions_frame = ttk.LabelFrame(tab, text="Quick Actions", padding=20)
        actions_frame.pack(fill='both', expand=True, padx=20, pady=10)

        btn_frame = tk.Frame(actions_frame)
        btn_frame.pack(expand=True)

        ttk.Button(btn_frame, text="Fetch New Products", command=self.fetch_products, width=25).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(btn_frame, text="Create Videos", command=self.create_videos, width=25).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(btn_frame, text="Post to TikTok", command=self.post_videos, width=25).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(btn_frame, text="Refresh Stats", command=self.update_stats, width=25).grid(row=1, column=1, padx=10, pady=10)

    def create_products_tab(self):
        """Products tab with enhanced table and manual entry"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Products")

        # Toolbar with all actions
        toolbar = tk.Frame(tab)
        toolbar.pack(fill='x', padx=10, pady=10)
        
        # Main action buttons
        ttk.Button(toolbar, text="➕ Add Product Manually", command=self.add_product_manually, 
                  style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="📥 Import CSV", command=self.import_products_csv).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🎬 Create Video from Link", command=self.create_video_from_link).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🔍 Fetch Products (Scraping)", command=self.fetch_products).pack(side='left', padx=5)
        
        # Separator
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Action buttons
        ttk.Button(toolbar, text="🔄 Refresh", command=self.refresh_products).pack(side='left', padx=5)
        ttk.Button(toolbar, text="✅ Select for Videos", command=self.select_products_for_video).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🗑️ Delete Selected", command=self.delete_selected_products).pack(side='left', padx=5)
        
        # Search/Filter frame
        filter_frame = tk.Frame(tab)
        filter_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(filter_frame, text="Search:").pack(side='left', padx=5)
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace('w', self.filter_products)
        search_entry = ttk.Entry(filter_frame, textvariable=self.product_search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        tk.Label(filter_frame, text="Category:").pack(side='left', padx=(20,5))
        self.category_filter_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_filter_var, 
                                     values=["All", "Beauty", "Skincare", "Fashion", "Accessories", 
                                            "Home", "Lifestyle", "Electronics", "Fitness"],
                                     width=15, state='readonly')
        category_combo.pack(side='left', padx=5)
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_products())

        # Table with enhanced columns
        table_frame = tk.Frame(tab)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient='vertical')
        h_scroll = ttk.Scrollbar(table_frame, orient='horizontal')
        
        # Enhanced columns
        columns = ('ID', 'Name', 'Category', 'Price (PHP)', 'Commission %', 
                   'Commission Amount', 'Rating', 'Status', 'Date Added')
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                         yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Configure column widths and headings
        column_widths = {
            'ID': 100,
            'Name': 250,
            'Category': 120,
            'Price (PHP)': 100,
            'Commission %': 100,
            'Commission Amount': 120,
            'Rating': 80,
            'Status': 120,
            'Date Added': 120
        }
        
        for col in columns:
            self.products_tree.heading(col, text=col, command=lambda c=col: self.sort_products_by_column(c))
            self.products_tree.column(col, width=column_widths.get(col, 100), anchor='center' if col in ['Price (PHP)', 'Commission %', 'Rating', 'Status'] else 'w')

        # Pack scrollbars
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        v_scroll.config(command=self.products_tree.yview)
        h_scroll.config(command=self.products_tree.xview)

        # Pack table
        self.products_tree.pack(fill='both', expand=True)
        
        # Click handler to open product URLs (only Name column is clickable, no visual styling on other columns)
        self.products_tree.bind('<Button-1>', self.on_product_click)
        # Double-click to view details
        self.products_tree.bind('<Double-1>', self.view_product_details)
        
        # Product count label
        self.product_count_label = tk.Label(tab, text="Total Products: 0", font=('Arial', 9))
        self.product_count_label.pack(side='bottom', pady=5)

    def create_videos_tab(self):
        """Videos tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Videos")

        toolbar = tk.Frame(tab)
        toolbar.pack(fill='x', padx=10, pady=10)
        ttk.Button(toolbar, text="Create Videos", command=self.create_videos).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_videos).pack(side='left', padx=5)

        table_frame = tk.Frame(tab)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        v_scroll = ttk.Scrollbar(table_frame)
        v_scroll.pack(side='right', fill='y')

        columns = ('ID', 'Product', 'Status', 'Created')
        self.videos_tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=v_scroll.set)

        for col in columns:
            self.videos_tree.heading(col, text=col)
            self.videos_tree.column(col, width=200 if col == 'Product' else 100)

        self.videos_tree.pack(fill='both', expand=True)
        v_scroll.config(command=self.videos_tree.yview)

    def create_script_tab(self):
        """Create a Script tab for AI-generated scripts"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Create a Script")
        
        # Header
        header_frame = tk.Frame(tab)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="🎬 AI Script Generator", font=('Arial', 16, 'bold')).pack()
        tk.Label(header_frame, text="Generate engaging video scripts using AI", font=('Arial', 10)).pack(pady=5)
        
        # Main content frame
        content_frame = tk.Frame(tab)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left side - Input
        left_frame = ttk.LabelFrame(content_frame, text="Script Details", padding=15)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # AI Provider selection
        tk.Label(left_frame, text="AI Provider:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.script_provider_var = tk.StringVar(value="openai")
        provider_combo = ttk.Combobox(left_frame, textvariable=self.script_provider_var,
                                      values=["openai", "groq", "apify"],
                                      width=40, state='readonly')
        provider_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        provider_combo.bind('<<ComboboxSelected>>', lambda e: self._update_provider_status())
        
        # Product selection
        tk.Label(left_frame, text="Select Product:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.script_product_var = tk.StringVar()
        self.script_product_combo = ttk.Combobox(left_frame, textvariable=self.script_product_var, width=40, state='readonly')
        self.script_product_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Tone selection
        tk.Label(left_frame, text="Script Tone:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.script_tone_var = tk.StringVar(value="Engaging")
        tone_combo = ttk.Combobox(left_frame, textvariable=self.script_tone_var, 
                                  values=["Engaging", "Energetic", "Casual", "Professional", "Funny", "Urgent"],
                                  width=40, state='readonly')
        tone_combo.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Duration
        tk.Label(left_frame, text="Script Duration (seconds):", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        self.script_duration_var = tk.StringVar(value="15")
        duration_combo = ttk.Combobox(left_frame, textvariable=self.script_duration_var,
                                     values=["10", "15", "30", "60"],
                                     width=40, state='readonly')
        duration_combo.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # Language selection
        tk.Label(left_frame, text="Script Language:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        self.script_language_var = tk.StringVar(value="English")
        language_combo = ttk.Combobox(left_frame, textvariable=self.script_language_var,
                                      values=["English", "Filipino", "Filipino and English"],
                                      width=40, state='readonly')
        language_combo.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
        # Additional notes
        tk.Label(left_frame, text="Additional Notes (optional):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='nw', pady=5)
        script_notes_text = scrolledtext.ScrolledText(left_frame, width=50, height=8, font=('Arial', 9))
        script_notes_text.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
        
        # API Status and Actions
        api_frame = ttk.LabelFrame(left_frame, text="AI API Status", padding=10)
        api_frame.grid(row=6, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.api_status_label = tk.Label(api_frame, text="Status: Not checked", font=('Arial', 9), fg='gray')
        self.api_status_label.pack(pady=5)
        
        api_btn_frame = tk.Frame(api_frame)
        api_btn_frame.pack(pady=5)
        ttk.Button(api_btn_frame, text="🔑 Test API Key", command=self.test_openai_api_key, width=18).pack(side='left', padx=3)
        ttk.Button(api_btn_frame, text="💰 Check Usage", command=self.check_openai_usage, width=18).pack(side='left', padx=3)
        
        # Generate button
        btn_frame = tk.Frame(left_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="✨ Generate Script", command=self.generate_script, width=25).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🎬 Create Video", command=self.create_video_from_script, width=25).pack(side='left', padx=5)
        
        left_frame.columnconfigure(1, weight=1)
        
        # Right side - Output
        right_frame = ttk.LabelFrame(content_frame, text="Generated Script", padding=15)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        self.generated_script_text = scrolledtext.ScrolledText(right_frame, width=50, height=25, font=('Consolas', 10))
        self.generated_script_text.pack(fill='both', expand=True)
        
        # Store notes text widget for later access
        self.script_notes_text = script_notes_text
        
        # Initialize provider status
        self._update_provider_status()
        
        # Status label for script tab
        script_status_frame = tk.Frame(tab)
        script_status_frame.pack(fill='x', padx=20, pady=10)
        self.script_status_label = tk.Label(script_status_frame, text="Ready to generate script", font=('Arial', 9), fg='gray')
        self.script_status_label.pack()

    def create_posting_tab(self):
        """Posting tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Post to TikTok")

        tk.Label(tab, text="Post Videos to TikTok", font=('Arial', 14)).pack(pady=20)
        ttk.Button(tab, text="Post Videos", command=self.post_videos, width=30).pack(pady=10)

        log_frame = ttk.LabelFrame(tab, text="Activity Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)
        self.setup_gui_logging()

    def fetch_products(self):
        """Fetch products and display them in real-time"""
        self.update_status("Fetching products... Please wait...")
        
        # Clear previous products count
        self.fetched_count = 0
        
        def on_product_found(product):
            """Callback: Called when each product is found - displays immediately!"""
            try:
                logger.info(f"🔔 Callback triggered! Product: {product.get('name', 'Unknown')}")
                
                # Validate product has required fields
                if not product or not product.get('product_id'):
                    logger.warning(f"Invalid product data: {product}")
                    return
                
                # Add to database
                try:
                    result = self.db.add_product(product)
                    logger.info(f"✅ Product added to DB: {product.get('name')}")
                except Exception as db_error:
                    logger.error(f"Database error: {db_error}")
                    # Continue anyway - might be duplicate
                
                self.fetched_count += 1
                
                # Update GUI immediately (thread-safe) - create copy of product for lambda
                product_copy = dict(product)  # Create a copy to avoid closure issues
                
                # Schedule GUI update on main thread
                self.root.after(0, lambda p=product_copy: self._add_product_to_table(p))
                self.root.after(0, lambda count=self.fetched_count: self.update_status(f"Fetching... Found {count} products so far!"))
                
                logger.info(f"✅ Product {self.fetched_count} queued for display: {product.get('name', 'Unknown')}")
            except Exception as e:
                logger.error(f"❌ Error in on_product_found callback: {e}", exc_info=True)
        
        def task():
            try:
                # Fetch with real-time callback
                products = self.product_fetcher.fetch_trending_products(
                    limit=20, 
                    use_scraping=True,
                    on_product_found=on_product_found
                )
                
                # Final update - force refresh to show all products from database
                logger.info(f"📊 Fetch complete. Total fetched: {self.fetched_count}")
                
                # Get all products from database to verify
                all_products = self.db.get_products()
                logger.info(f"📊 Total products in database: {len(all_products)}")
                
                # Force refresh of table
                self.root.after(0, self.refresh_products)
                
                # Wait a bit then update status
                self.root.after(100, lambda: self.update_status(f"✅ Completed! Found {self.fetched_count} products (Total in DB: {len(all_products)})"))
                
                if self.fetched_count > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success", 
                        f"Successfully fetched {self.fetched_count} products!\n\nProducts are displayed in the table."
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "No Products Found",
                        "No products were found. Try:\n"
                        "1. Ensure you're logged into TikTok\n"
                        "2. Use 'Add Product Manually' button\n"
                        "3. Try 'Import CSV' for bulk import"
                    ))
                    
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch products:\n{str(e)}"))
                self.root.after(0, lambda: self.update_status("❌ Fetch failed"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def _add_product_to_table(self, product: Dict):
        """Add a single product to the table immediately (for real-time display)"""
        try:
            logger.info(f"📊 Adding product to table: {product.get('name', 'Unknown')}")
            
            # Check if products_tree exists
            if not hasattr(self, 'products_tree') or self.products_tree is None:
                logger.error("❌ products_tree not initialized!")
                return
            
            # Format product for display
            price = float(product.get('price', 0))
            commission_rate = float(product.get('commission_rate', 0))
            price_php = round(price * 56, 2)
            commission_amount = product.get('commission_amount', 0) or (price * commission_rate / 100)
            date_added = "Just now"
            
            # Ensure all values are strings and properly formatted
            values = (
                str(product.get('product_id', 'N/A')),
                str(product.get('name', 'Unknown Product'))[:50],
                str(product.get('category', 'General')),
                f"₱{price_php:.2f}",
                f"{commission_rate:.1f}%",
                f"${commission_amount:.2f}",
                f"{float(product.get('rating', 0)):.1f}",
                str(product.get('status', 'pending')),
                date_added
            )
            
            logger.info(f"   Values: {values[:3]}...")  # Log first 3 values
            
            # Insert at the top (newest first)
            try:
                item = self.products_tree.insert('', 0, values=values)
                logger.info(f"   ✅ Inserted item: {item}")
            except Exception as insert_error:
                logger.error(f"   ❌ Insert failed: {insert_error}")
                logger.error(f"   Tree state: {self.products_tree}")
                raise
            
            # Get product URL and ensure it's a full TikTok product page URL
            product_url = self._get_product_url(product)
            
            # Store URL in tags for click handler (only Name column will be clickable)
            if product_url:
                # Store URL in tags
                current_tags = list(self.products_tree.item(item, 'tags'))
                current_tags.append(f'url:{product_url}')
                self.products_tree.item(item, tags=current_tags)
            
            # Tag by status
            status = str(product.get('status', 'pending')).lower()
            if status == 'selected':
                self.products_tree.set(item, 'Status', '✅ Selected')
            elif status == 'video_created':
                self.products_tree.set(item, 'Status', '🎬 Video Created')
            elif status == 'posted':
                self.products_tree.set(item, 'Status', '📤 Posted')
            
            # Update count
            try:
                current_count = len(self.products_tree.get_children())
                if hasattr(self, 'product_count_label') and self.product_count_label:
                    self.product_count_label.config(text=f"Total Products: {current_count} (Fetching... +{self.fetched_count})")
            except Exception as count_error:
                logger.debug(f"Count update error: {count_error}")
            
            # Scroll to show new item
            try:
                self.products_tree.see(item)
            except:
                pass
            
            logger.info(f"✅ Product successfully added to table!")
            
        except Exception as e:
            logger.error(f"❌ Error adding product to table: {e}", exc_info=True)
            # Try to at least refresh the table
            try:
                self.root.after(100, self.refresh_products)
            except:
                pass

    def on_product_click(self, event):
        """Handle click on product name column to open product URL"""
        region = self.products_tree.identify_region(event.x, event.y)
        if region == 'cell':
            column = self.products_tree.identify_column(event.x)
            item = self.products_tree.identify_row(event.y)
            
            # Only handle clicks on Name column (column 2, indexed from 1)
            if column == '#2' and item:
                # Ensure the row is selected
                self.products_tree.selection_set(item)
                
                # Get URL from item tags
                tags = self.products_tree.item(item, 'tags')
                url = None
                for tag in tags:
                    if tag.startswith('url:'):
                        url = tag[4:]  # Remove 'url:' prefix
                        break
                
                # If no URL in tags, get product from database to get the real URL
                if not url:
                    values = self.products_tree.item(item, 'values')
                    if values and len(values) > 0:
                        product_id = values[0]
                        # Get product from database to get the actual stored URL
                        products = self.db.get_products()
                        product = next((p for p in products if p.get('product_id') == product_id), None)
                        if product:
                            url = self._get_product_url(product)
                
                # Open the actual URL if it exists (must be a valid URL, not empty)
                if url and url.startswith('http'):
                    webbrowser.open(url)
                    return
        
        # For other columns, allow normal selection
        return None
    
    def select_products_for_video(self):
        """Mark selected products"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select products first")
            return
        for item in selected:
            product_id = self.products_tree.item(item)['values'][0]
            self.db.update_product_status(product_id, 'selected')
        self.refresh_products()
        messagebox.showinfo("Success", f"Selected {len(selected)} products")
    
    def add_product_manually(self):
        """Open dialog to add product manually"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Product Manually")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        fields = {}
        row = 0
        
        # Product Name
        tk.Label(dialog, text="Product Name *:").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        fields['name'] = ttk.Entry(dialog, width=50)
        fields['name'].grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Category
        tk.Label(dialog, text="Category *:").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        fields['category'] = ttk.Combobox(dialog, values=["Beauty", "Skincare", "Fashion", "Accessories", 
                                                          "Home", "Lifestyle", "Electronics", "Fitness"],
                                         width=47, state='readonly')
        fields['category'].grid(row=row, column=1, padx=10, pady=5)
        fields['category'].current(0)  # Default to Beauty
        row += 1
        
        # Price (USD)
        tk.Label(dialog, text="Price (USD) *:").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        fields['price'] = ttk.Entry(dialog, width=50)
        fields['price'].grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Commission Rate
        tk.Label(dialog, text="Commission Rate (%) *:").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        fields['commission_rate'] = ttk.Entry(dialog, width=50)
        fields['commission_rate'].grid(row=row, column=1, padx=10, pady=5)
        fields['commission_rate'].insert(0, "10")  # Default 10%
        row += 1
        
        # Rating
        tk.Label(dialog, text="Rating (0-5):").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        fields['rating'] = ttk.Entry(dialog, width=50)
        fields['rating'].grid(row=row, column=1, padx=10, pady=5)
        fields['rating'].insert(0, "4.5")  # Default rating
        row += 1
        
        # Product URL / Affiliate Link
        tk.Label(dialog, text="Product/Affiliate Link *:").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        fields['affiliate_link'] = ttk.Entry(dialog, width=50)
        fields['affiliate_link'].grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Image URL
        tk.Label(dialog, text="Image URL (optional):").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        fields['image_url'] = ttk.Entry(dialog, width=50)
        fields['image_url'].grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Description
        tk.Label(dialog, text="Description:").grid(row=row, column=0, sticky='nw', padx=10, pady=5)
        fields['description'] = scrolledtext.ScrolledText(dialog, width=50, height=5)
        fields['description'].grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        def save_product():
            """Save product to database"""
            try:
                # Validate required fields
                name = fields['name'].get().strip()
                if not name:
                    messagebox.showerror("Error", "Product name is required!")
                    return
                
                price = float(fields['price'].get().strip() or 0)
                if price <= 0:
                    messagebox.showerror("Error", "Price must be greater than 0!")
                    return
                
                commission_rate = float(fields['commission_rate'].get().strip() or 0)
                if commission_rate <= 0:
                    messagebox.showerror("Error", "Commission rate must be greater than 0!")
                    return
                
                affiliate_link = fields['affiliate_link'].get().strip()
                if not affiliate_link:
                    messagebox.showerror("Error", "Product/Affiliate link is required!")
                    return
                
                # Generate product ID
                import random
                product_id = f"MANUAL_{random.randint(1000, 9999)}_{int(time.time())}"
                
                # Create product dict
                product = {
                    'product_id': product_id,
                    'name': name,
                    'description': fields['description'].get('1.0', tk.END).strip(),
                    'price': price,
                    'commission_rate': commission_rate,
                    'commission_amount': round(price * commission_rate / 100, 2),
                    'category': fields['category'].get() or 'General',
                    'rating': float(fields['rating'].get().strip() or 4.5),
                    'image_url': fields['image_url'].get().strip(),
                    'affiliate_link': affiliate_link,
                    'product_url': affiliate_link.split('?')[0] if '?' in affiliate_link else affiliate_link,
                    'status': 'pending'
                }
                
                # Save to database
                self.db.add_product(product)
                self.refresh_products()
                dialog.destroy()
                messagebox.showinfo("Success", f"Product '{name}' added successfully!")
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid number format: {str(e)}")
            except Exception as e:
                logger.error(f"Error adding product: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to add product: {str(e)}")
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Save Product", command=save_product).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=10)
    
    def import_products_csv(self):
        """Import products from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file to import",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            imported = 0
            skipped = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Map CSV columns to product fields
                        product = {
                            'product_id': row.get('product_id') or f"CSV_{random.randint(1000, 9999)}_{int(time.time())}",
                            'name': row.get('name', '').strip(),
                            'description': row.get('description', '').strip(),
                            'price': float(row.get('price', 0)),
                            'commission_rate': float(row.get('commission_rate', 10)),
                            'commission_amount': float(row.get('price', 0)) * float(row.get('commission_rate', 10)) / 100,
                            'category': row.get('category', 'General'),
                            'rating': float(row.get('rating', 4.5)),
                            'image_url': row.get('image_url', '').strip(),
                            'affiliate_link': row.get('affiliate_link') or row.get('product_url', '').strip(),
                            'product_url': row.get('product_url', '').strip(),
                            'status': 'pending'
                        }
                        
                        # Validate required fields
                        if not product['name'] or product['price'] <= 0:
                            skipped += 1
                            continue
                        
                        # Add to database
                        self.db.add_product(product)
                        imported += 1
                        
                    except (ValueError, KeyError) as e:
                        logger.debug(f"Skipping invalid row: {e}")
                        skipped += 1
                        continue
            
            self.refresh_products()
            messagebox.showinfo("Import Complete", 
                              f"Imported {imported} products successfully!\n"
                              f"Skipped {skipped} invalid rows.")
            
        except Exception as e:
            logger.error(f"Error importing CSV: {e}", exc_info=True)
            messagebox.showerror("Import Error", f"Failed to import CSV:\n{str(e)}")
    
    def delete_selected_products(self):
        """Delete selected products"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select products to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected)} product(s)?"):
            return
        
        try:
            for item in selected:
                product_id = self.products_tree.item(item)['values'][0]
                self.db.delete_product(product_id)
            
            self.refresh_products()
            messagebox.showinfo("Success", f"Deleted {len(selected)} product(s)")
            
        except Exception as e:
            logger.error(f"Error deleting products: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to delete products: {str(e)}")
    
    def view_product_details(self, event):
        """View product details on double-click"""
        selected = self.products_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        product_id = self.products_tree.item(item)['values'][0]
        
        # Get product from database
        products = self.db.get_products()
        product = next((p for p in products if p.get('product_id') == product_id), None)
        
        if not product:
            return
        
        # Create details window
        details = tk.Toplevel(self.root)
        details.title(f"Product Details - {product.get('name', 'N/A')}")
        details.geometry("600x500")
        
        # Display product information
        info_text = scrolledtext.ScrolledText(details, wrap=tk.WORD, font=('Arial', 10))
        info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        details_text = f"""
PRODUCT DETAILS
{'='*60}

ID: {product.get('product_id', 'N/A')}
Name: {product.get('name', 'N/A')}
Category: {product.get('category', 'General')}

PRICING:
Price (USD): ${product.get('price', 0):.2f}
Price (PHP): ₱{product.get('price', 0) * 56:.2f}
Commission Rate: {product.get('commission_rate', 0):.1f}%
Commission Amount: ${product.get('commission_amount', 0):.2f}

RATINGS:
Rating: {product.get('rating', 0):.1f} / 5.0

STATUS:
Status: {product.get('status', 'pending')}
Date Added: {product.get('date_added', 'N/A')[:10] if product.get('date_added') else 'N/A'}

DESCRIPTION:
{product.get('description', 'No description available')}

LINKS:
Product URL: {product.get('product_url', 'N/A')}
Affiliate Link: {product.get('affiliate_link', 'N/A')}
Image URL: {product.get('image_url', 'N/A')}
"""
        
        info_text.insert('1.0', details_text)
        info_text.config(state='disabled')
        
        # Close button
        ttk.Button(details, text="Close", command=details.destroy).pack(pady=10)

    def create_video_from_link(self):
        """Create a video directly from a TikTok product link"""
        # Dialog to get TikTok product URL
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Video from TikTok Link")
        dialog.geometry("600x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter TikTok Product URL:", font=('Arial', 10)).pack(pady=10)
        
        url_entry = ttk.Entry(dialog, width=70)
        url_entry.pack(pady=10, padx=20)
        url_entry.focus()
        
        def process_link():
            url = url_entry.get().strip()
            if not url:
                messagebox.showerror("Error", "Please enter a TikTok product URL")
                return
            
            dialog.destroy()
            self.update_status("Extracting product info from URL...")
            
            def task():
                """Extract product info in background thread (web scraping only)"""
                try:
                    # Extract product from URL (only web scraping in background thread)
                    product = self._extract_product_from_url(url)
                    
                    # Schedule all database operations in main thread
                    if not product:
                        self.root.after(0, lambda: messagebox.showerror(
                            "Error", 
                            "Could not extract product information from the URL.\n\n"
                            "Please ensure:\n"
                            "1. The URL is a valid TikTok Shop product page\n"
                            "2. You're connected to the internet\n"
                            "3. The product page is accessible"
                        ))
                        self.root.after(0, lambda: self.update_status("❌ Extraction failed"))
                        return
                    
                    # Pass product data to main thread for database operations
                    self.root.after(0, lambda p=product: self._process_extracted_product(p))
                        
                except Exception as e:
                    logger.error(f"Error extracting product from link: {e}", exc_info=True)
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to extract product:\n{str(e)}"))
                    self.root.after(0, lambda: self.update_status("❌ Error occurred"))
            
            threading.Thread(target=task, daemon=True).start()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Create Video", command=process_link).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=10)
        
        # Allow Enter key to submit
        url_entry.bind('<Return>', lambda e: process_link())
    
    def _process_extracted_product(self, product: Dict):
        """Process extracted product in main thread (database operations)"""
        try:
            # Add product to database (in main thread)
            self.update_status("Adding product to database...")
            product_id = self.db.add_product(product)
            
            if product_id == -1:
                # Product already exists, get it from database
                products = self.db.get_products()
                existing = next((p for p in products if p.get('product_id') == product.get('product_id')), None)
                if existing:
                    product = existing
            else:
                # Refresh products table
                self.refresh_products()
            
            # Create video immediately (in main thread)
            self.update_status("Creating video...")
            
            def create_video_task():
                """Create video in background thread, but database ops in main thread"""
                try:
                    caption, hashtags = self.caption_generator.create_full_post(product)
                    video_path = VIDEOS_DIR / f"{product['product_id']}_video.mp4"
                    
                    if self.video_creator.create_product_video(product, video_path):
                        # Database operations must be in main thread
                        self.root.after(0, lambda: self.db.add_video({
                            'product_id': product['product_id'], 
                            'video_path': str(video_path),
                            'caption': caption, 
                            'hashtags': hashtags, 
                            'status': 'created'
                        }))
                        self.root.after(0, lambda: self.db.update_product_status(product['product_id'], 'video_created'))
                        
                        self.root.after(0, self.refresh_videos)
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Success!", 
                            f"Video created successfully!\n\n"
                            f"Product: {product.get('name', 'Unknown')}\n"
                            f"Video saved to: {video_path.name}"
                        ))
                        self.root.after(0, lambda: self.update_status("✅ Video created!"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", "Failed to create video"))
                        self.root.after(0, lambda: self.update_status("❌ Video creation failed"))
                except Exception as e:
                    logger.error(f"Error creating video: {e}", exc_info=True)
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to create video:\n{str(e)}"))
                    self.root.after(0, lambda: self.update_status("❌ Error occurred"))
            
            # Run video creation in background thread (it's slow)
            threading.Thread(target=create_video_task, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error processing product: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to process product:\n{str(e)}")
            self.update_status("❌ Error occurred")
    
    def _extract_product_from_url(self, url: str) -> Optional[Dict]:
        """Extract product information from a TikTok product URL"""
        try:
            from playwright.sync_api import sync_playwright
            import time
            
            # Validate URL
            if not url.startswith('http'):
                if url.startswith('www.'):
                    url = f"https://{url}"
                elif url.startswith('/'):
                    url = f"https://www.tiktok.com{url}"
                else:
                    url = f"https://www.tiktok.com/shop/product/{url}"
            
            logger.info(f"Extracting product from URL: {url}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    time.sleep(3)  # Wait for content to load
                    
                    # Try to extract product info using ProductFetcher methods
                    # Strategy 1: Extract from embedded JSON
                    script_content = page.content()
                    import json
                    import re
                    
                    # Look for product data in JSON
                    json_patterns = [
                        r'__UNIVERSAL_DATA_FOR_REHYDRATION__\s*=\s*({.+?});',
                        r'window\.__UNIVERSAL_DATA_FOR_REHYDRATION__\s*=\s*({.+?});',
                        r'"product".*?({.+?"id".+?})',
                        r'"itemInfo".*?({.+?})',
                    ]
                    
                    for pattern in json_patterns:
                        matches = re.findall(pattern, script_content, re.DOTALL)
                        for match in matches[:3]:
                            try:
                                if isinstance(match, str) and match.strip().startswith('{'):
                                    data = json.loads(match.strip())
                                    # Try to parse product from this data
                                    product = self.product_fetcher._json_to_product(data)
                                    if product:
                                        product['product_url'] = url
                                        product['affiliate_link'] = url
                                        browser.close()
                                        return product
                            except:
                                continue
                    
                    # Strategy 2: Extract from page HTML
                    try:
                        # Try to get product name from title or h1
                        title = page.title()
                        name = title.replace(' | TikTok', '').replace(' - TikTok Shop', '').strip()
                        
                        # Try to get price
                        price_elements = page.query_selector_all('[class*="price"], [class*="Price"], [data-e2e*="price"]')
                        price = 0.0
                        for elem in price_elements:
                            try:
                                text = elem.inner_text()
                                price_match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
                                if price_match:
                                    price = float(price_match.group().replace(',', ''))
                                    break
                            except:
                                continue
                        
                        # Try to get product ID from URL
                        product_id = url.split('/shop/product/')[-1].split('?')[0].split('/')[-1] if '/shop/product/' in url else f"URL_{abs(hash(url)) % 100000}"
                        
                        # Try to get image
                        img_elements = page.query_selector_all('img[src*="product"], img[alt*="product"], [class*="product-image"] img')
                        image_url = ''
                        for img in img_elements[:1]:
                            try:
                                image_url = img.get_attribute('src') or ''
                                if image_url:
                                    break
                            except:
                                continue
                        
                        if name and name != 'TikTok':
                            product = {
                                'product_id': product_id,
                                'name': name[:200],
                                'description': f"Product from {url}",
                                'price': price or 19.99,  # Default if not found
                                'commission_rate': 10.0,
                                'commission_amount': (price or 19.99) * 0.10,
                                'category': 'General',
                                'rating': 4.5,
                                'image_url': image_url,
                                'product_url': url,
                                'affiliate_link': url,
                                'status': 'pending'
                            }
                            browser.close()
                            return product
                    except Exception as e:
                        logger.debug(f"HTML extraction error: {e}")
                    
                    browser.close()
                    return None
                    
                except Exception as e:
                    logger.error(f"Error loading page: {e}")
                    browser.close()
                    return None
                    
        except ImportError:
            logger.error("Playwright not installed")
            messagebox.showerror("Error", "Playwright is required. Install with: pip install playwright && playwright install")
            return None
        except Exception as e:
            logger.error(f"Error extracting product from URL: {e}", exc_info=True)
            return None
    
    def create_videos(self):
        """Create videos"""
        products = self.db.get_products(status='selected')
        if not products:
            messagebox.showwarning("No Products", "No products selected")
            return
        self.update_status("Creating videos...")
        def task():
            try:
                for product in products:
                    caption, hashtags = self.caption_generator.create_full_post(product)
                    video_path = VIDEOS_DIR / f"{product['product_id']}_video.mp4"
                    if self.video_creator.create_product_video(product, video_path):
                        self.db.add_video({'product_id': product['product_id'], 'video_path': str(video_path),
                                          'caption': caption, 'hashtags': hashtags, 'status': 'created'})
                        self.db.update_product_status(product['product_id'], 'video_created')
                self.root.after(0, self.refresh_videos)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Created {len(products)} videos!"))
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=task, daemon=True).start()

    def post_videos(self):
        """Post videos"""
        videos = self.db.get_videos(status='created')
        if not videos:
            messagebox.showwarning("No Videos", "No videos ready to post")
            return
        if not messagebox.askyesno("Post", f"Post {len(videos)} video(s)?"):
            return
        for video in videos[:1]:
            try:
                url = self.uploader.upload_video(Path(video['video_path']), video['caption'],
                                                video['hashtags'], manual_review=True)
                if url:
                    self.db.update_video_post(video['id'], url)
                    messagebox.showinfo("Success", f"Posted!\n{url}")
            except Exception as e:
                logger.error(f"Error: {e}")
                messagebox.showerror("Error", str(e))
        self.refresh_videos()

    def create_settings_tab(self):
        """Settings and Configuration tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Settings")

        # Main container with scrollbar
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title
        title = tk.Label(scrollable_frame, text="⚙️ Settings & Configuration", font=('Arial', 20, 'bold'))
        title.pack(pady=20)

        subtitle = tk.Label(scrollable_frame, text="Configure your API credentials and account settings",
                           font=('Arial', 10), fg='gray')
        subtitle.pack(pady=(0, 20))

        # Create credential entry fields dictionary
        self.cred_entries = {}
        self.status_indicators = {}  # For API status circles
        self.visibility_toggles = {}  # For hide/show buttons
        self.api_test_buttons = {}  # Individual test buttons

        # TikTok Account Section
        tiktok_frame = ttk.LabelFrame(scrollable_frame, text="🎵 TikTok Account", padding=20)
        tiktok_frame.pack(fill='x', padx=40, pady=10)

        self._create_entry_with_toggle(tiktok_frame, "Username:", "tiktok.username", 0, sensitive=False)
        self._create_entry_with_toggle(tiktok_frame, "Password:", "tiktok.password", 1, sensitive=True)
        self._create_entry_with_toggle(tiktok_frame, "Cookies File:", "tiktok.cookies_file", 2, sensitive=False)

        tk.Label(tiktok_frame, text="ℹ️ Your TikTok account credentials for posting videos",
                fg='gray', font=('Arial', 8)).grid(row=3, column=0, columnspan=4, pady=(5,0), sticky='w')

        # TikTok Shop API Section
        shop_frame = ttk.LabelFrame(scrollable_frame, text="🛍️ TikTok Shop API (Optional)", padding=20)
        shop_frame.pack(fill='x', padx=40, pady=10)

        self._create_api_entry(shop_frame, "App Key:", "tiktok_shop_api.app_key", 0, api_name="TikTok Shop")
        self._create_api_entry(shop_frame, "App Secret:", "tiktok_shop_api.app_secret", 1, api_name="TikTok Shop")
        self._create_api_entry(shop_frame, "Access Token:", "tiktok_shop_api.access_token", 2, api_name="TikTok Shop")

        tk.Label(shop_frame, text="ℹ️ Required for fetching real TikTok Shop products. Leave empty to use demo mode.",
                fg='gray', font=('Arial', 8)).grid(row=3, column=0, columnspan=2, pady=(10,0), sticky='w')

        # AI API Keys Section
        ai_frame = ttk.LabelFrame(scrollable_frame, text="🤖 AI API Keys (Optional)", padding=20)
        ai_frame.pack(fill='x', padx=40, pady=10)

        self._create_api_entry(ai_frame, "OpenAI API Key:", "openai_api_key", 0, api_name="OpenAI")
        self._create_api_entry(ai_frame, "Anthropic API Key:", "anthropic_api_key", 1, api_name="Anthropic")
        self._create_api_entry(ai_frame, "Groq API Key:", "groq_api_key", 2, api_name="Groq")
        self._create_api_entry(ai_frame, "Apify API Key:", "apify_api_key", 3, api_name="Apify")
        self._create_api_entry(ai_frame, "ElevenLabs API Key:", "elevenlabs_api_key", 4, api_name="ElevenLabs")
        
        # Apify Actor ID configuration
        tk.Label(ai_frame, text="Apify Actor ID:", font=('Arial', 10)).grid(row=5, column=0,
                                                                    sticky='w', pady=8, padx=(0, 10))
        apify_actor_frame = tk.Frame(ai_frame)
        apify_actor_frame.grid(row=5, column=1, sticky='ew', pady=8)
        apify_actor_frame.columnconfigure(0, weight=1)
        
        apify_actor_entry = ttk.Entry(apify_actor_frame, width=35)
        apify_actor_entry.grid(row=0, column=0, sticky='ew')
        self.cred_entries['apify_actor_id'] = apify_actor_entry
        
        tk.Label(ai_frame, text="ℹ️ Format: username~actorName or actor ID (e.g., apify~web-scraper). Leave empty to use OpenAI directly.",
                fg='gray', font=('Arial', 8)).grid(row=6, column=0, columnspan=2, pady=(0,10), sticky='w')

        tk.Label(ai_frame, text="ℹ️ For AI-generated captions and voiceovers. Leave empty to use templates.",
                fg='gray', font=('Arial', 8)).grid(row=7, column=0, columnspan=2, pady=(10,0), sticky='w')

        # .env File Section
        env_frame = ttk.LabelFrame(scrollable_frame, text="📄 Environment Variables (.env)", padding=20)
        env_frame.pack(fill='x', padx=40, pady=10)
        
        env_help = tk.Label(env_frame, 
                           text="ℹ️ Load credentials from .env file or export as environment variables",
                           fg='gray', font=('Arial', 8), wraplength=600, justify='left')
        env_help.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 10))
        
        env_btn_frame = tk.Frame(env_frame)
        env_btn_frame.grid(row=1, column=0, columnspan=3, sticky='w')
        
        ttk.Button(env_btn_frame, text="📥 Load from .env", command=self.load_from_env,
                  width=18).pack(side='left', padx=5)
        ttk.Button(env_btn_frame, text="💾 Save to .env", command=self.save_to_env,
                  width=18).pack(side='left', padx=5)
        ttk.Button(env_btn_frame, text="🔄 Auto-Reload .env", command=self.auto_reload_env,
                  width=20).pack(side='left', padx=5)
        ttk.Button(env_btn_frame, text="🌐 Load from Environment", command=self.load_from_environment,
                  width=22).pack(side='left', padx=5)

        # Buttons Frame
        btn_frame = tk.Frame(scrollable_frame)
        btn_frame.pack(pady=30)

        ttk.Button(btn_frame, text="💾 Save Settings", command=self.save_credentials,
                  width=20).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="🔄 Reload", command=self.load_credentials_to_ui,
                  width=20).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="🧪 Test All APIs", command=self.test_all_apis,
                  width=20).pack(side='left', padx=10)

        # TikTok Account Stats Section
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📊 TikTok Account Statistics", padding=20)
        stats_frame.pack(fill='x', padx=40, pady=10)
        
        stats_info = tk.Label(stats_frame, 
                             text="ℹ️ Account statistics will be displayed after connecting to TikTok",
                             fg='gray', font=('Arial', 8), wraplength=600, justify='left')
        stats_info.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 10))
        
        # Stats display
        self.tiktok_stats = {}
        stats_labels = [
            ("Account Name:", "account_name"),
            ("Following:", "following"),
            ("Followers:", "followers"),
            ("Total Likes:", "total_likes")
        ]
        
        for i, (label_text, key) in enumerate(stats_labels):
            tk.Label(stats_frame, text=label_text, font=('Arial', 10, 'bold')).grid(
                row=i+1, column=0, sticky='w', pady=5, padx=(0, 10)
            )
            value_label = tk.Label(stats_frame, text="Not loaded", font=('Arial', 10), fg='gray')
            value_label.grid(row=i+1, column=1, sticky='w', pady=5)
            self.tiktok_stats[key] = value_label
        
        # Refresh stats button
        stats_btn_frame = tk.Frame(stats_frame)
        stats_btn_frame.grid(row=len(stats_labels)+1, column=0, columnspan=2, pady=10, sticky='w')
        ttk.Button(stats_btn_frame, text="🔄 Refresh Account Stats", 
                  command=self.refresh_tiktok_stats, width=25).pack(side='left', padx=5)

        # Status label
        self.settings_status = tk.Label(scrollable_frame, text="", font=('Arial', 10))
        self.settings_status.pack(pady=10)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load current credentials (prioritize .env file if it exists)
        self.load_credentials_to_ui()

    def _create_entry(self, parent, label_text, key, row, show=None):
        """Helper to create labeled entry field"""
        tk.Label(parent, text=label_text, font=('Arial', 10)).grid(row=row, column=0,
                                                                    sticky='w', pady=8, padx=(0, 10))
        entry = ttk.Entry(parent, width=50, show=show)
        entry.grid(row=row, column=1, sticky='ew', pady=8)
        parent.columnconfigure(1, weight=1)
        self.cred_entries[key] = entry

    def _create_entry_with_toggle(self, parent, label_text, key, row, sensitive=False):
        """Create entry field with hide/show toggle for sensitive data"""
        tk.Label(parent, text=label_text, font=('Arial', 10)).grid(row=row, column=0,
                                                                    sticky='w', pady=8, padx=(0, 10))
        
        entry_frame = tk.Frame(parent)
        entry_frame.grid(row=row, column=1, sticky='ew', pady=8)
        entry_frame.columnconfigure(0, weight=1)
        
        show_char = '*' if sensitive else None
        entry = ttk.Entry(entry_frame, width=45, show=show_char)
        entry.grid(row=0, column=0, sticky='ew')
        self.cred_entries[key] = entry
        
        if sensitive:
            toggle_btn = ttk.Button(entry_frame, text="👁️", width=4,
                                   command=lambda k=key: self._toggle_visibility(k))
            toggle_btn.grid(row=0, column=1, padx=(5, 0))
            self.visibility_toggles[key] = {'entry': entry, 'visible': False, 'button': toggle_btn}

    def _create_api_entry(self, parent, label_text, key, row, api_name="API"):
        """Create API entry field with status indicator and test button"""
        tk.Label(parent, text=label_text, font=('Arial', 10)).grid(row=row, column=0,
                                                                    sticky='w', pady=8, padx=(0, 10))
        
        entry_frame = tk.Frame(parent)
        entry_frame.grid(row=row, column=1, sticky='ew', pady=8)
        entry_frame.columnconfigure(0, weight=1)
        
        # Entry field
        entry = ttk.Entry(entry_frame, width=35, show='*')
        entry.grid(row=0, column=0, sticky='ew')
        self.cred_entries[key] = entry
        
        # Hide/Show toggle
        toggle_btn = ttk.Button(entry_frame, text="👁️", width=4,
                               command=lambda k=key: self._toggle_visibility(k))
        toggle_btn.grid(row=0, column=1, padx=(5, 0))
        self.visibility_toggles[key] = {'entry': entry, 'visible': False, 'button': toggle_btn}
        
        # Status indicator (circle)
        status_canvas = tk.Canvas(entry_frame, width=20, height=20, highlightthickness=0)
        status_canvas.grid(row=0, column=2, padx=(5, 0))
        status_circle = status_canvas.create_oval(5, 5, 15, 15, fill='gray', outline='gray')
        self.status_indicators[key] = {
            'canvas': status_canvas,
            'circle': status_circle,
            'api_name': api_name
        }
        
        # Test button
        test_btn = ttk.Button(entry_frame, text="🧪", width=4,
                             command=lambda k=key, a=api_name: self._test_single_api(k, a))
        test_btn.grid(row=0, column=3, padx=(5, 0))
        self.api_test_buttons[key] = test_btn
        
        parent.columnconfigure(1, weight=1)

    def _toggle_visibility(self, key):
        """Toggle visibility of sensitive entry field"""
        if key not in self.visibility_toggles:
            return
        
        toggle_info = self.visibility_toggles[key]
        entry = toggle_info['entry']
        is_visible = toggle_info['visible']
        
        if is_visible:
            # Hide
            entry.config(show='*')
            toggle_info['button'].config(text="👁️")
            toggle_info['visible'] = False
        else:
            # Show
            entry.config(show='')
            toggle_info['button'].config(text="🙈")
            toggle_info['visible'] = True

    def _update_status_indicator(self, key, status):
        """Update status indicator circle (green=working, red=not working, gray=unknown)"""
        if key not in self.status_indicators:
            return
        
        indicator = self.status_indicators[key]
        canvas = indicator['canvas']
        circle = indicator['circle']
        
        if status == 'working':
            color = 'green'
        elif status == 'error':
            color = 'red'
        else:
            color = 'gray'
        
        canvas.itemconfig(circle, fill=color, outline=color)

    def load_credentials_to_ui(self):
        """Load credentials from file to UI fields - prioritizes .env file"""
        try:
            # Check .env file first (priority)
            env_file = BASE_DIR / ".env"
            cred_file = BASE_DIR / "config" / "credentials.json"
            
            creds = {}
            
            # Load from .env if it exists (takes priority)
            if env_file.exists():
                env_vars = {}
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip().strip('"').strip("'")
                
                # Convert .env format to credentials.json format
                if 'TIKTOK_USERNAME' in env_vars or 'TIKTOK_PASSWORD' in env_vars:
                    creds['tiktok'] = {
                        'username': env_vars.get('TIKTOK_USERNAME', ''),
                        'password': env_vars.get('TIKTOK_PASSWORD', ''),
                        'cookies_file': env_vars.get('TIKTOK_COOKIES_FILE', 'data/tiktok_cookies.json')
                    }
                
                if 'OPENAI_API_KEY' in env_vars:
                    creds['openai_api_key'] = env_vars['OPENAI_API_KEY']
                
                if 'ANTHROPIC_API_KEY' in env_vars:
                    creds['anthropic_api_key'] = env_vars['ANTHROPIC_API_KEY']
                
                if 'GROQ_API_KEY' in env_vars:
                    creds['groq_api_key'] = env_vars['GROQ_API_KEY']
                
                if 'APIFY_API_KEY' in env_vars:
                    creds['apify_api_key'] = env_vars['APIFY_API_KEY']
                
                if 'APIFY_USER_ID' in env_vars:
                    creds['apify_user_id'] = env_vars['APIFY_USER_ID']
                
                if 'APIFY_ACTOR_ID' in env_vars:
                    creds['apify_actor_id'] = env_vars['APIFY_ACTOR_ID']
                
                if 'ELEVENLABS_API_KEY' in env_vars:
                    creds['elevenlabs_api_key'] = env_vars['ELEVENLABS_API_KEY']
                
                if any(k.startswith('TIKTOK_SHOP_') for k in env_vars.keys()):
                    creds['tiktok_shop_api'] = {
                        'app_key': env_vars.get('TIKTOK_SHOP_APP_KEY', ''),
                        'app_secret': env_vars.get('TIKTOK_SHOP_APP_SECRET', ''),
                        'access_token': env_vars.get('TIKTOK_SHOP_ACCESS_TOKEN', '')
                    }
                
                logger.info("Loaded credentials from .env file")
                
                # Merge with credentials.json if it exists (for any missing keys)
                if cred_file.exists():
                    try:
                        with open(cred_file, 'r') as f:
                            json_creds = json.load(f)
                            # Merge: .env takes priority, but fill in missing keys from json
                            for key, value in json_creds.items():
                                if key not in creds:
                                    creds[key] = value
                            logger.info("Merged credentials from .env and credentials.json")
                    except Exception as e:
                        logger.warning(f"Could not merge credentials.json: {e}")
            
            # Fall back to credentials.json if .env doesn't exist
            elif cred_file.exists():
                with open(cred_file, 'r') as f:
                    creds = json.load(f)
                logger.info("Loaded credentials from credentials.json")
            
            # Create default if neither exists
            else:
                # Create default credentials file from example
                example_file = BASE_DIR / "config" / "credentials.json.example"
                if example_file.exists():
                    import shutil
                    cred_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(example_file, cred_file)
                    creds = {}
                else:
                    creds = {}
                logger.info("Created default credentials file")

            # Load TikTok credentials
            if 'tiktok' in creds:
                self.cred_entries['tiktok.username'].delete(0, tk.END)
                self.cred_entries['tiktok.username'].insert(0, creds['tiktok'].get('username', ''))

                self.cred_entries['tiktok.password'].delete(0, tk.END)
                self.cred_entries['tiktok.password'].insert(0, creds['tiktok'].get('password', ''))

                self.cred_entries['tiktok.cookies_file'].delete(0, tk.END)
                self.cred_entries['tiktok.cookies_file'].insert(0, creds['tiktok'].get('cookies_file', ''))

            # Load TikTok Shop API credentials
            if 'tiktok_shop_api' in creds:
                self.cred_entries['tiktok_shop_api.app_key'].delete(0, tk.END)
                self.cred_entries['tiktok_shop_api.app_key'].insert(0, creds['tiktok_shop_api'].get('app_key', ''))

                self.cred_entries['tiktok_shop_api.app_secret'].delete(0, tk.END)
                self.cred_entries['tiktok_shop_api.app_secret'].insert(0, creds['tiktok_shop_api'].get('app_secret', ''))

                self.cred_entries['tiktok_shop_api.access_token'].delete(0, tk.END)
                self.cred_entries['tiktok_shop_api.access_token'].insert(0, creds['tiktok_shop_api'].get('access_token', ''))

            # Load AI API keys
            self.cred_entries['openai_api_key'].delete(0, tk.END)
            self.cred_entries['openai_api_key'].insert(0, creds.get('openai_api_key', ''))

            self.cred_entries['anthropic_api_key'].delete(0, tk.END)
            self.cred_entries['anthropic_api_key'].insert(0, creds.get('anthropic_api_key', ''))

            self.cred_entries['groq_api_key'].delete(0, tk.END)
            self.cred_entries['groq_api_key'].insert(0, creds.get('groq_api_key', ''))

            self.cred_entries['apify_api_key'].delete(0, tk.END)
            self.cred_entries['apify_api_key'].insert(0, creds.get('apify_api_key', ''))
            
            if 'apify_actor_id' in self.cred_entries:
                self.cred_entries['apify_actor_id'].delete(0, tk.END)
                self.cred_entries['apify_actor_id'].insert(0, creds.get('apify_actor_id', ''))

            self.cred_entries['elevenlabs_api_key'].delete(0, tk.END)
            self.cred_entries['elevenlabs_api_key'].insert(0, creds.get('elevenlabs_api_key', ''))

            # Also sync to credentials.json for backward compatibility
            if creds:
                try:
                    cred_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(cred_file, 'w') as f:
                        json.dump(creds, f, indent=2)
                except:
                    pass  # Non-critical
                
                # Update self.credentials to include apify_user_id if present
                if 'apify_user_id' in creds:
                    self.credentials['apify_user_id'] = creds['apify_user_id']
            
            self.settings_status.config(text="✅ Settings loaded", fg='green')
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            self.settings_status.config(text=f"❌ Error loading: {str(e)}", fg='red')

    def save_credentials(self):
        """Save credentials from UI to file"""
        try:
            creds = {
                "tiktok": {
                    "username": self.cred_entries['tiktok.username'].get(),
                    "password": self.cred_entries['tiktok.password'].get(),
                    "cookies_file": self.cred_entries['tiktok.cookies_file'].get()
                },
                "openai_api_key": self.cred_entries['openai_api_key'].get(),
                "anthropic_api_key": self.cred_entries['anthropic_api_key'].get(),
                "groq_api_key": self.cred_entries['groq_api_key'].get(),
                "apify_api_key": self.cred_entries['apify_api_key'].get(),
                "apify_actor_id": self.cred_entries['apify_actor_id'].get() if 'apify_actor_id' in self.cred_entries else '',
                "apify_user_id": self.credentials.get('apify_user_id', ''),  # Load from existing credentials
                "elevenlabs_api_key": self.cred_entries['elevenlabs_api_key'].get(),
                "tiktok_shop_api": {
                    "app_key": self.cred_entries['tiktok_shop_api.app_key'].get(),
                    "app_secret": self.cred_entries['tiktok_shop_api.app_secret'].get(),
                    "access_token": self.cred_entries['tiktok_shop_api.access_token'].get()
                }
            }

            cred_file = BASE_DIR / "config" / "credentials.json"
            with open(cred_file, 'w') as f:
                json.dump(creds, f, indent=2)

            # Reload credentials into components
            self.credentials = creds
            self.product_fetcher = ProductFetcher(self.credentials, PRODUCT_FILTERS)
            self.caption_generator = CaptionGenerator(AI_CONFIG, HASHTAG_CONFIG, self.credentials)
            self.uploader = TikTokUploader(self.credentials, TIKTOK_CONFIG)

            # Auto-save to .env file as well
            try:
                self.save_to_env(show_message=False)
            except Exception as e:
                logger.warning(f"Could not auto-save to .env: {e}")

            self.settings_status.config(text="✅ Settings saved successfully!", fg='green')
            messagebox.showinfo("Success", "Settings saved successfully!\n\nCredentials have been updated and synced to .env file.")

        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            self.settings_status.config(text=f"❌ Error saving: {str(e)}", fg='red')
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")

    def _test_single_api(self, key, api_name):
        """Test a single API and update status indicator"""
        self.settings_status.config(text=f"🔄 Testing {api_name}...", fg='blue')

        def test_task():
            status = 'error'
            message = ""
            
            try:
                api_key = self.cred_entries[key].get().strip()
                
                if not api_key or api_key.startswith("YOUR_") or api_key == "":
                    status = 'error'
                    message = f"{api_name}: Not configured"
                else:
                    # Test based on API type
                    if key == 'openai_api_key':
                        status, message = self._test_openai(api_key)
                    elif key == 'anthropic_api_key':
                        status, message = self._test_anthropic(api_key)
                    elif key == 'groq_api_key':
                        status, message = self._test_groq(api_key)
                    elif key == 'apify_api_key':
                        status, message = self._test_apify(api_key)
                    elif key == 'elevenlabs_api_key':
                        status, message = self._test_elevenlabs(api_key)
                    elif key in ['tiktok_shop_api.app_key', 'tiktok_shop_api.app_secret', 'tiktok_shop_api.access_token']:
                        # Test TikTok Shop API (needs all three)
                        app_key = self.cred_entries['tiktok_shop_api.app_key'].get().strip()
                        app_secret = self.cred_entries['tiktok_shop_api.app_secret'].get().strip()
                        access_token = self.cred_entries['tiktok_shop_api.access_token'].get().strip()
                        if app_key and app_secret and access_token:
                            status, message = self._test_tiktok_shop(app_key, app_secret, access_token)
                            # Update all three indicators
                            for k in ['tiktok_shop_api.app_key', 'tiktok_shop_api.app_secret', 'tiktok_shop_api.access_token']:
                                self.root.after(0, lambda s=status, k=k: self._update_status_indicator(k, s))
                            self.root.after(0, lambda: self.settings_status.config(text=message, fg='green' if status == 'working' else 'red'))
                            return
                        else:
                            status = 'error'
                            message = "TikTok Shop: Missing credentials"
                    else:
                        status = 'unknown'
                        message = f"{api_name}: Test not implemented"
                
                # Update indicator for this key
                self.root.after(0, lambda s=status, k=key: self._update_status_indicator(k, s))
                self.root.after(0, lambda: self.settings_status.config(text=message, fg='green' if status == 'working' else 'red'))
                
            except Exception as e:
                logger.error(f"Error testing {api_name}: {e}")
                self.root.after(0, lambda: self._update_status_indicator(key, 'error'))
                self.root.after(0, lambda: self.settings_status.config(text=f"{api_name}: Error - {str(e)}", fg='red'))
        
        threading.Thread(target=test_task, daemon=True).start()

    def _test_openai(self, api_key):
        """Test OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            # Simple test - list models
            client.models.list(limit=1)
            return 'working', "OpenAI: ✅ Working"
        except Exception as e:
            return 'error', f"OpenAI: ❌ {str(e)[:50]}"
    
    def _test_anthropic(self, api_key):
        """Test Anthropic API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            # Simple test - count tokens (lightweight operation)
            client.count_tokens("test")
            return 'working', "Anthropic: ✅ Working"
        except Exception as e:
            return 'error', f"Anthropic: ❌ {str(e)[:50]}"
    
    def _test_groq(self, api_key):
        """Test Groq API"""
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            # Simple test - list models
            client.models.list()
            return 'working', "Groq: ✅ Working"
        except ImportError:
            return 'error', "Groq: ❌ Package not installed (pip install groq)"
        except Exception as e:
            return 'error', f"Groq: ❌ {str(e)[:50]}"
    
    def _test_apify(self, api_key):
        """Test Apify API"""
        try:
            from apify_client import ApifyClient
            client = ApifyClient(api_key)
            # Simple test - get user info
            user = client.user().get()
            if user and 'data' in user:
                return 'working', "Apify: ✅ Working"
            return 'error', "Apify: ❌ Invalid response"
        except ImportError:
            return 'error', "Apify: ❌ Package not installed (pip install apify-client)"
        except Exception as e:
            return 'error', f"Apify: ❌ {str(e)[:50]}"
    
    def _test_elevenlabs(self, api_key):
        """Test ElevenLabs API"""
        try:
            headers = {"xi-api-key": api_key}
            response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers, timeout=10)
            if response.status_code == 200:
                return 'working', "ElevenLabs: ✅ Working"
            else:
                return 'error', f"ElevenLabs: ❌ Status {response.status_code}"
        except Exception as e:
            return 'error', f"ElevenLabs: ❌ {str(e)[:50]}"
    
    def _test_tiktok_shop(self, app_key, app_secret, access_token):
        """Test TikTok Shop API"""
        try:
            # Basic validation - check if credentials format is correct
            if len(app_key) < 10 or len(access_token) < 10:
                return 'error', "TikTok Shop: Invalid credentials format"
            
            # Try a lightweight API call
            base_url = "https://open-api.tiktokglobalshop.com"
            endpoint = f"{base_url}/product/202309/products/search"
            
            params = {
                'app_key': app_key,
                'access_token': access_token,
                'page_size': 1,
                'timestamp': int(time.time())
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return 'working', "TikTok Shop: ✅ Working"
                else:
                    return 'error', f"TikTok Shop: ❌ {data.get('message', 'Unknown error')}"
            else:
                return 'error', f"TikTok Shop: ❌ Status {response.status_code}"
        except Exception as e:
            return 'error', f"TikTok Shop: ❌ {str(e)[:50]}"

    def test_all_apis(self):
        """Test all configured APIs"""
        self.settings_status.config(text="🔄 Testing all APIs...", fg='blue')
        
        def test_all_task():
            results = []

            # Test OpenAI
            openai_key = self.cred_entries['openai_api_key'].get().strip()
            if openai_key and not openai_key.startswith("YOUR_"):
                status, msg = self._test_openai(openai_key)
                self.root.after(0, lambda: self._update_status_indicator('openai_api_key', status))
                results.append(msg)
            else:
                self.root.after(0, lambda: self._update_status_indicator('openai_api_key', 'unknown'))

            # Test Anthropic
            anthropic_key = self.cred_entries['anthropic_api_key'].get().strip()
            if anthropic_key and not anthropic_key.startswith("YOUR_"):
                status, msg = self._test_anthropic(anthropic_key)
                self.root.after(0, lambda: self._update_status_indicator('anthropic_api_key', status))
                results.append(msg)
            else:
                self.root.after(0, lambda: self._update_status_indicator('anthropic_api_key', 'unknown'))
            
            # Test Groq
            groq_key = self.cred_entries['groq_api_key'].get().strip()
            if groq_key and not groq_key.startswith("YOUR_"):
                status, msg = self._test_groq(groq_key)
                self.root.after(0, lambda: self._update_status_indicator('groq_api_key', status))
                results.append(msg)
            else:
                self.root.after(0, lambda: self._update_status_indicator('groq_api_key', 'unknown'))
            
            # Test Apify
            apify_key = self.cred_entries['apify_api_key'].get().strip()
            if apify_key and not apify_key.startswith("YOUR_"):
                status, msg = self._test_apify(apify_key)
                self.root.after(0, lambda: self._update_status_indicator('apify_api_key', status))
                results.append(msg)
            else:
                self.root.after(0, lambda: self._update_status_indicator('apify_api_key', 'unknown'))
            
            # Test ElevenLabs
            elevenlabs_key = self.cred_entries['elevenlabs_api_key'].get().strip()
            if elevenlabs_key and not elevenlabs_key.startswith("YOUR_"):
                status, msg = self._test_elevenlabs(elevenlabs_key)
                self.root.after(0, lambda: self._update_status_indicator('elevenlabs_api_key', status))
                results.append(msg)
            else:
                self.root.after(0, lambda: self._update_status_indicator('elevenlabs_api_key', 'unknown'))
            
            # Test TikTok Shop (needs all three)
            app_key = self.cred_entries['tiktok_shop_api.app_key'].get().strip()
            app_secret = self.cred_entries['tiktok_shop_api.app_secret'].get().strip()
            access_token = self.cred_entries['tiktok_shop_api.access_token'].get().strip()
            
            if app_key and app_secret and access_token:
                status, msg = self._test_tiktok_shop(app_key, app_secret, access_token)
                shop_keys = ['tiktok_shop_api.app_key', 'tiktok_shop_api.app_secret', 'tiktok_shop_api.access_token']
                for k in shop_keys:
                    self.root.after(0, lambda key=k, st=status: self._update_status_indicator(key, st))
                results.append(msg)
            else:
                shop_keys = ['tiktok_shop_api.app_key', 'tiktok_shop_api.app_secret', 'tiktok_shop_api.access_token']
                for k in shop_keys:
                    self.root.after(0, lambda key=k: self._update_status_indicator(key, 'unknown'))
            
            result_text = "\n".join(results) if results else "No APIs configured to test"
            self.root.after(0, lambda: messagebox.showinfo("API Test Results", result_text))
            self.root.after(0, lambda: self.settings_status.config(text="✅ All API tests completed", fg='green'))
        
        threading.Thread(target=test_all_task, daemon=True).start()

    def load_from_env(self):
        """Load credentials from .env file and update UI"""
        try:
            env_file = BASE_DIR / ".env"
            if not env_file.exists():
                messagebox.showinfo("Info", ".env file not found. Create one or use 'Save to .env' to create it.")
                return
            
            # Use the main load function which handles .env
            self.load_credentials_to_ui()
            
            self.settings_status.config(text="✅ Loaded from .env file", fg='green')
            messagebox.showinfo("Success", "Credentials loaded from .env file and synced to GUI!")
            
        except Exception as e:
            logger.error(f"Error loading from .env: {e}")
            messagebox.showerror("Error", f"Failed to load from .env:\n{str(e)}")

    def auto_reload_env(self):
        """Auto-reload .env file and sync to GUI"""
        try:
            env_file = BASE_DIR / ".env"
            if not env_file.exists():
                messagebox.showinfo("Info", ".env file not found.")
                return
            
            # Reload from .env
            self.load_credentials_to_ui()
            self.settings_status.config(text="✅ Auto-reloaded from .env file", fg='green')
            messagebox.showinfo("Success", "Settings reloaded from .env file!")
            
        except Exception as e:
            logger.error(f"Error auto-reloading .env: {e}")
            messagebox.showerror("Error", f"Failed to reload from .env:\n{str(e)}")

    def refresh_tiktok_stats(self):
        """Fetch and display TikTok account statistics"""
        self.settings_status.config(text="🔄 Fetching TikTok account stats...", fg='blue')
        
        def fetch_stats_task():
            try:
                username = self.cred_entries['tiktok.username'].get().strip()
                if not username or username.startswith("YOUR_"):
                    self.root.after(0, lambda: self.settings_status.config(
                        text="❌ Please enter TikTok username first", fg='red'))
                    return
                
                # Try to get stats using Playwright
                stats = self._fetch_tiktok_stats(username)
                
                if stats:
                    # Update UI with stats
                    self.root.after(0, lambda: self._update_tiktok_stats_display(stats))
                    self.root.after(0, lambda: self.settings_status.config(
                        text="✅ Account stats updated", fg='green'))
                else:
                    self.root.after(0, lambda: self.settings_status.config(
                        text="❌ Could not fetch stats. Try again or check username.", fg='red'))
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Warning", "Could not fetch TikTok account stats.\n\n" +
                        "Possible reasons:\n" +
                        "• Username is incorrect\n" +
                        "• TikTok website changed (selectors may need update)\n" +
                        "• Network/connection issue\n" +
                        "• Account is private or restricted\n\n" +
                        "Tip: The browser window opened during fetch - check if any errors appeared."))
                    
            except Exception as e:
                logger.error(f"Error fetching TikTok stats: {e}", exc_info=True)
                self.root.after(0, lambda: self.settings_status.config(
                    text=f"❌ Error: {str(e)[:50]}", fg='red'))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to fetch TikTok stats:\n{str(e)}"))
        
        threading.Thread(target=fetch_stats_task, daemon=True).start()

    def _fetch_tiktok_stats(self, username):
        """Fetch TikTok account statistics using Playwright - Improved version"""
        try:
            from playwright.sync_api import sync_playwright
            import re
            
            logger.info(f"Fetching TikTok stats for @{username}")
            
            with sync_playwright() as p:
                # Launch browser in visible mode for better compatibility
                browser = p.chromium.launch(
                    headless=False,  # Visible for debugging and better compatibility
                    slow_mo=500  # Slow down to appear more human
                )
                
                # Create context with realistic browser settings
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
                
                # Load cookies if available
                cookies_file = Path(self.cred_entries['tiktok.cookies_file'].get().strip() or 
                                  BASE_DIR / "data" / "tiktok_cookies.json")
                if cookies_file.exists():
                    try:
                        with open(cookies_file, 'r') as f:
                            cookies = json.load(f)
                            if cookies:
                                context.add_cookies(cookies)
                                logger.info("Loaded saved cookies")
                    except Exception as e:
                        logger.warning(f"Could not load cookies: {e}")
                
                page = context.new_page()
                
                # First, try to access TikTok homepage to establish session
                logger.info("Navigating to TikTok homepage...")
                try:
                    page.goto('https://www.tiktok.com', wait_until='domcontentloaded', timeout=20000)
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"Could not load homepage: {e}")
                
                # Navigate to profile
                profile_url = f"https://www.tiktok.com/@{username}"
                logger.info(f"Navigating to profile: {profile_url}")
                
                try:
                    page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
                    time.sleep(5)  # Wait for page to fully load
                    
                    # Check for age verification or login required
                    if "age" in page.url.lower() or "login" in page.url.lower():
                        logger.warning("TikTok requires login or age verification")
                    
                    # Check if profile exists
                    page_content = page.content().lower()
                    if "couldn't find" in page_content or "user not found" in page_content or "doesn't exist" in page_content:
                        logger.error(f"Profile @{username} not found")
                        browser.close()
                        return None
                    
                except Exception as e:
                    logger.error(f"Error navigating to profile: {e}")
                    browser.close()
                    return None
                
                # Initialize stats
                stats = {
                    'account_name': username,
                    'following': 'N/A',
                    'followers': 'N/A',
                    'total_likes': 'N/A'
                }
                
                # Method 1: Try to extract from JSON data in page (most reliable)
                try:
                    page_content = page.content()
                    
                    # Look for JSON data embedded in page (TikTok stores profile data in script tags)
                    json_pattern = r'<script[^>]*id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>'
                    matches = re.findall(json_pattern, page_content, re.DOTALL)
                    
                    if matches:
                        try:
                            data_json = json.loads(matches[0])
                            # Navigate through TikTok's data structure
                            user_info = data_json.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {}).get('userInfo', {})
                            
                            if user_info:
                                if 'followerCount' in user_info:
                                    stats['followers'] = self._parse_count(str(user_info['followerCount']))
                                if 'followingCount' in user_info:
                                    stats['following'] = self._parse_count(str(user_info['followingCount']))
                                if 'likeCount' in user_info:
                                    stats['total_likes'] = self._parse_count(str(user_info['likeCount']))
                                
                                logger.info("Successfully extracted stats from JSON data")
                        except Exception as e:
                            logger.debug(f"Could not parse JSON data: {e}")
                except Exception as e:
                    logger.debug(f"JSON extraction method failed: {e}")
                
                # Method 2: Try multiple CSS selectors (if JSON method didn't work)
                if stats['followers'] == 'N/A' or stats['following'] == 'N/A':
                    logger.info("Trying CSS selector method...")
                    
                    # Updated selectors based on current TikTok structure
                    followers_selectors = [
                        '[data-e2e="followers-count"]',
                        '[data-e2e="followers"]',
                        'strong:has-text("Followers")',
                        'div[class*="count"]:has-text("Followers")',
                        'strong[title*="Followers"]',
                        '.profile-stats strong',
                        '[class*="follower"] strong',
                        'div:has-text("Followers") + strong',
                        'div:has-text("Followers") ~ strong'
                    ]
                    
                    following_selectors = [
                        '[data-e2e="following-count"]',
                        '[data-e2e="following"]',
                        'strong:has-text("Following")',
                        'div[class*="count"]:has-text("Following")',
                        'strong[title*="Following"]',
                        '.profile-stats strong',
                        '[class*="following"] strong'
                    ]
                    
                    # Try to get all strong elements and match by context
                    try:
                        all_strong = page.query_selector_all('strong')
                        for element in all_strong:
                            text = element.inner_text().strip()
                            parent = element.evaluate('el => el.parentElement.innerText')
                            
                            if 'follower' in parent.lower() and 'following' not in parent.lower():
                                if stats['followers'] == 'N/A':
                                    stats['followers'] = self._parse_count(text)
                            elif 'following' in parent.lower():
                                if stats['following'] == 'N/A':
                                    stats['following'] = self._parse_count(text)
                    except:
                        pass
                    
                    # Try individual selectors as fallback
                    for selector in followers_selectors:
                        try:
                            element = page.query_selector(selector)
                            if element:
                                text = element.inner_text().strip()
                                if stats['followers'] == 'N/A':
                                    stats['followers'] = self._parse_count(text)
                                    break
                        except:
                            continue
                    
                    for selector in following_selectors:
                        try:
                            element = page.query_selector(selector)
                            if element:
                                text = element.inner_text().strip()
                                if stats['following'] == 'N/A':
                                    stats['following'] = self._parse_count(text)
                                    break
                        except:
                            continue
                
                # Method 3: Extract from page text using regex
                if stats['followers'] == 'N/A' or stats['following'] == 'N/A':
                    logger.info("Trying regex extraction method...")
                    try:
                        page_text = page.inner_text()
                        
                        # Pattern for followers: "1.2M Followers" or "Followers\n1.2M"
                        followers_patterns = [
                            r'(\d+[\d.,]*[KMBkmb]?)\s*[Ff]ollowers?',
                            r'[Ff]ollowers?[:\s]+(\d+[\d.,]*[KMBkmb]?)',
                            r'"followerCount":(\d+)',
                        ]
                        
                        for pattern in followers_patterns:
                            match = re.search(pattern, page_text, re.IGNORECASE)
                            if match and stats['followers'] == 'N/A':
                                stats['followers'] = self._parse_count(match.group(1))
                                break
                        
                        # Pattern for following
                        following_patterns = [
                            r'(\d+[\d.,]*[KMBkmb]?)\s*[Ff]ollowing',
                            r'[Ff]ollowing[:\s]+(\d+[\d.,]*[KMBkmb]?)',
                            r'"followingCount":(\d+)',
                        ]
                        
                        for pattern in following_patterns:
                            match = re.search(pattern, page_text, re.IGNORECASE)
                            if match and stats['following'] == 'N/A':
                                stats['following'] = self._parse_count(match.group(1))
                                break
                                
                    except Exception as e:
                        logger.debug(f"Regex extraction failed: {e}")
                
                # Try to get total likes
                try:
                    page_text = page.content()
                    likes_patterns = [
                        r'"likeCount":(\d+)',
                        r'"heartCount":(\d+)',
                        r'(\d+[\d.,]*[KMBkmb]?)\s*[Ll]ikes?',
                    ]
                    for pattern in likes_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            stats['total_likes'] = self._parse_count(match.group(1))
                            break
                except:
                    pass
                
                browser.close()
                
                # If we got at least some data, return it
                if stats['followers'] != 'N/A' or stats['following'] != 'N/A':
                    logger.info(f"Successfully fetched stats: {stats}")
                    return stats
                else:
                    logger.warning("Could not extract any stats")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in _fetch_tiktok_stats: {e}", exc_info=True)
            return None

    def _parse_count(self, text):
        """Parse TikTok count format (e.g., '1.2M', '500K', '1,234')"""
        if not text:
            return 'N/A'
        
        text = text.strip().upper()
        
        # Remove commas
        text = text.replace(',', '')
        
        # Handle K, M, B suffixes
        if 'K' in text:
            num = float(text.replace('K', ''))
            return f"{int(num * 1000):,}"
        elif 'M' in text:
            num = float(text.replace('M', ''))
            return f"{int(num * 1000000):,}"
        elif 'B' in text:
            num = float(text.replace('B', ''))
            return f"{int(num * 1000000000):,}"
        else:
            # Just numbers
            try:
                num = int(float(text))
                return f"{num:,}"
            except:
                return text

    def _update_tiktok_stats_display(self, stats):
        """Update the TikTok stats display in UI"""
        if 'account_name' in stats:
            self.tiktok_stats['account_name'].config(text=stats['account_name'], fg='blue')
        
        if 'following' in stats:
            self.tiktok_stats['following'].config(text=str(stats['following']), fg='black')
        
        if 'followers' in stats:
            self.tiktok_stats['followers'].config(text=str(stats['followers']), fg='black')
        
        if 'total_likes' in stats:
            self.tiktok_stats['total_likes'].config(text=str(stats['total_likes']), fg='black')

    def save_to_env(self, show_message=True):
        """Save credentials to .env file"""
        try:
            env_file = BASE_DIR / ".env"
            
            lines = [
                "# ClickTok Environment Variables",
                "# Generated automatically - edit manually if needed",
                "# This file is auto-synced with GUI settings",
                ""
            ]
            
            # TikTok
            username = self.cred_entries['tiktok.username'].get().strip()
            password = self.cred_entries['tiktok.password'].get().strip()
            cookies_file = self.cred_entries['tiktok.cookies_file'].get().strip()
            
            if username:
                lines.append(f"TIKTOK_USERNAME={username}")
            if password:
                lines.append(f"TIKTOK_PASSWORD={password}")
            if cookies_file:
                lines.append(f"TIKTOK_COOKIES_FILE={cookies_file}")
            
            lines.append("")
            
            # API Keys
            openai_key = self.cred_entries['openai_api_key'].get().strip()
            anthropic_key = self.cred_entries['anthropic_api_key'].get().strip()
            groq_key = self.cred_entries['groq_api_key'].get().strip()
            apify_key = self.cred_entries['apify_api_key'].get().strip()
            apify_actor_id = self.cred_entries['apify_actor_id'].get().strip() if 'apify_actor_id' in self.cred_entries else ''
            apify_user_id = self.credentials.get('apify_user_id', '').strip() if self.credentials else ''
            elevenlabs_key = self.cred_entries['elevenlabs_api_key'].get().strip()
            
            if openai_key:
                lines.append(f"OPENAI_API_KEY={openai_key}")
            if anthropic_key:
                lines.append(f"ANTHROPIC_API_KEY={anthropic_key}")
            if groq_key:
                lines.append(f"GROQ_API_KEY={groq_key}")
            if apify_key:
                lines.append(f"APIFY_API_KEY={apify_key}")
            if apify_user_id:
                lines.append(f"APIFY_USER_ID={apify_user_id}")
            if apify_actor_id:
                lines.append(f"APIFY_ACTOR_ID={apify_actor_id}")
            if elevenlabs_key:
                lines.append(f"ELEVENLABS_API_KEY={elevenlabs_key}")
            
            lines.append("")
            
            # TikTok Shop
            app_key = self.cred_entries['tiktok_shop_api.app_key'].get().strip()
            app_secret = self.cred_entries['tiktok_shop_api.app_secret'].get().strip()
            access_token = self.cred_entries['tiktok_shop_api.access_token'].get().strip()
            
            if app_key:
                lines.append(f"TIKTOK_SHOP_APP_KEY={app_key}")
            if app_secret:
                lines.append(f"TIKTOK_SHOP_APP_SECRET={app_secret}")
            if access_token:
                lines.append(f"TIKTOK_SHOP_ACCESS_TOKEN={access_token}")
            
            env_file.write_text('\n'.join(lines))
            if show_message:
                self.settings_status.config(text="✅ Saved to .env file", fg='green')
                messagebox.showinfo("Success", f"Credentials saved to .env file!\n\nLocation: {env_file}")
            else:
                logger.info("Auto-synced credentials to .env file")
            
        except Exception as e:
            logger.error(f"Error saving to .env: {e}")
            if show_message:
                messagebox.showerror("Error", f"Failed to save to .env:\n{str(e)}")

    def load_from_environment(self):
        """Load credentials from system environment variables"""
        try:
            # Load from environment
            if 'TIKTOK_USERNAME' in os.environ:
                self.cred_entries['tiktok.username'].delete(0, tk.END)
                self.cred_entries['tiktok.username'].insert(0, os.environ['TIKTOK_USERNAME'])
            
            if 'TIKTOK_PASSWORD' in os.environ:
                self.cred_entries['tiktok.password'].delete(0, tk.END)
                self.cred_entries['tiktok.password'].insert(0, os.environ['TIKTOK_PASSWORD'])
            
            if 'OPENAI_API_KEY' in os.environ:
                self.cred_entries['openai_api_key'].delete(0, tk.END)
                self.cred_entries['openai_api_key'].insert(0, os.environ['OPENAI_API_KEY'])
            
            if 'ANTHROPIC_API_KEY' in os.environ:
                self.cred_entries['anthropic_api_key'].delete(0, tk.END)
                self.cred_entries['anthropic_api_key'].insert(0, os.environ['ANTHROPIC_API_KEY'])
            
            if 'GROQ_API_KEY' in os.environ:
                self.cred_entries['groq_api_key'].delete(0, tk.END)
                self.cred_entries['groq_api_key'].insert(0, os.environ['GROQ_API_KEY'])
            
            if 'APIFY_API_KEY' in os.environ:
                self.cred_entries['apify_api_key'].delete(0, tk.END)
                self.cred_entries['apify_api_key'].insert(0, os.environ['APIFY_API_KEY'])
            
            if 'APIFY_USER_ID' in os.environ:
                # Store in credentials since there's no GUI field for it
                if 'apify_user_id' not in self.credentials:
                    self.credentials['apify_user_id'] = os.environ['APIFY_USER_ID']
                else:
                    self.credentials['apify_user_id'] = os.environ['APIFY_USER_ID']
            
            if 'APIFY_ACTOR_ID' in os.environ:
                if 'apify_actor_id' in self.cred_entries:
                    self.cred_entries['apify_actor_id'].delete(0, tk.END)
                    self.cred_entries['apify_actor_id'].insert(0, os.environ['APIFY_ACTOR_ID'])
            
            if 'ELEVENLABS_API_KEY' in os.environ:
                self.cred_entries['elevenlabs_api_key'].delete(0, tk.END)
                self.cred_entries['elevenlabs_api_key'].insert(0, os.environ['ELEVENLABS_API_KEY'])
            
            if 'TIKTOK_SHOP_APP_KEY' in os.environ:
                self.cred_entries['tiktok_shop_api.app_key'].delete(0, tk.END)
                self.cred_entries['tiktok_shop_api.app_key'].insert(0, os.environ['TIKTOK_SHOP_APP_KEY'])
            
            if 'TIKTOK_SHOP_APP_SECRET' in os.environ:
                self.cred_entries['tiktok_shop_api.app_secret'].delete(0, tk.END)
                self.cred_entries['tiktok_shop_api.app_secret'].insert(0, os.environ['TIKTOK_SHOP_APP_SECRET'])
            
            if 'TIKTOK_SHOP_ACCESS_TOKEN' in os.environ:
                self.cred_entries['tiktok_shop_api.access_token'].delete(0, tk.END)
                self.cred_entries['tiktok_shop_api.access_token'].insert(0, os.environ['TIKTOK_SHOP_ACCESS_TOKEN'])
            
            self.settings_status.config(text="✅ Loaded from environment variables", fg='green')
            messagebox.showinfo("Success", "Credentials loaded from system environment variables!")
            
        except Exception as e:
            logger.error(f"Error loading from environment: {e}")
            messagebox.showerror("Error", f"Failed to load from environment:\n{str(e)}")

    def test_credentials(self):
        """Test if credentials are valid (legacy method - kept for compatibility)"""
        self.test_all_apis()

    def _get_product_url(self, product_data: Dict) -> str:
        """Get the actual TikTok product page URL for a product from stored data"""
        # Priority: Use product_url first, then affiliate_link
        product_url = product_data.get('product_url') or ''
        affiliate_link = product_data.get('affiliate_link') or ''
        
        # Use the actual stored URL (product_url takes priority)
        url = product_url or affiliate_link
        
        if not url:
            return ''
        
        # Clean up the URL - ensure it starts with http/https
        if not url.startswith('http'):
            if url.startswith('/'):
                url = f"https://www.tiktok.com{url}"
            else:
                # If it's not a valid URL format, return empty
                return ''
        
        # Validate it's not just the homepage
        if url in ['https://tiktok.com', 'http://tiktok.com', 'https://www.tiktok.com', 'http://www.tiktok.com']:
            return ''
        
        # Return the actual URL as stored (don't construct from product_id)
        # The product_id might be fake (like MANUAL_1234) so we must use the real URL
        return url
    
    def refresh_products(self):
        """Refresh products table with enhanced display"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        products = self.db.get_products()
        
        for p in products:
            # Format price in PHP (assuming 1 USD = 56 PHP)
            price_php = round(p.get('price', 0) * 56, 2)
            commission_amount = p.get('commission_amount', 0) or (p.get('price', 0) * p.get('commission_rate', 0) / 100)
            date_added = p.get('date_added', '')[:10] if p.get('date_added') else 'N/A'
            
            values = (
                p.get('product_id', 'N/A'),
                p.get('name', '')[:50],  # Longer name display
                p.get('category', 'General'),
                f"₱{price_php:.2f}",
                f"{p.get('commission_rate', 0):.1f}%",
                f"${commission_amount:.2f}",
                f"{p.get('rating', 0):.1f}",
                p.get('status', 'pending'),
                date_added
            )
            
            # Get product URL and ensure it's a full TikTok product page URL
            product_url = self._get_product_url(p)
            
            # Color code by status
            item = self.products_tree.insert('', 'end', values=values)
            
            # Store URL in tags for click handler (only Name column will be clickable)
            if product_url:
                # Store URL in tags - use a special tag format
                current_tags = list(self.products_tree.item(item, 'tags'))
                current_tags.append(f'url:{product_url}')
                # Don't apply visual styling - only Name column should be clickable
                self.products_tree.item(item, tags=current_tags)
            
            # Tag items by status for color coding
            status = p.get('status', 'pending').lower()
            if status == 'selected':
                self.products_tree.set(item, 'Status', '✅ Selected')
            elif status == 'video_created':
                self.products_tree.set(item, 'Status', '🎬 Video Created')
            elif status == 'posted':
                self.products_tree.set(item, 'Status', '📤 Posted')
        
        # Update count
        self.product_count_label.config(text=f"Total Products: {len(products)}")
        
        # Also refresh script product list
        self.refresh_script_product_list()
    
    def filter_products(self, *args):
        """Filter products by search term and category"""
        search_term = self.product_search_var.get().lower()
        category_filter = self.category_filter_var.get()
        
        # Get all items
        items_to_show = []
        items_to_hide = []
        
        for item in self.products_tree.get_children():
            values = self.products_tree.item(item)['values']
            name = values[1].lower() if len(values) > 1 else ''
            category = values[2] if len(values) > 2 else ''
            product_id = str(values[0]).lower() if len(values) > 0 else ''
            
            # Filter by search term
            matches_search = not search_term or search_term in name or search_term in product_id
            # Filter by category
            matches_category = category_filter == "All" or category == category_filter
            
            if matches_search and matches_category:
                items_to_show.append(item)
            else:
                items_to_hide.append(item)
        
        # Hide items that don't match
        for item in items_to_hide:
            self.products_tree.detach(item)
        
        # Reattach items that match (they stay visible)
        for item in items_to_show:
            try:
                self.products_tree.reattach(item, '', 'end')
            except:
                pass  # Item already visible
    
    def sort_products_by_column(self, column):
        """Sort products by selected column"""
        items = [(self.products_tree.set(item, column), item) for item in self.products_tree.get_children('')]
        
        # Try numeric sorting first
        try:
            items.sort(key=lambda t: float(t[0].replace('$', '').replace('₱', '').replace('%', '').strip()), reverse=True)
        except ValueError:
            # Fall back to string sorting
            items.sort(key=lambda t: t[0].lower())
        
        # Reorder items
        for index, (val, item) in enumerate(items):
            self.products_tree.move(item, '', index)

    def refresh_videos(self):
        """Refresh videos table"""
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        for v in self.db.get_videos():
            self.videos_tree.insert('', 'end', values=(v['id'], v['product_id'],
                v['status'], v['date_created'][:10] if v['date_created'] else ''))
    
    def refresh_script_product_list(self):
        """Populate script tab product dropdown"""
        if not hasattr(self, 'script_product_combo'):
            return
        
        products = self.db.get_products()
        product_list = []
        self.script_product_map = {}  # Store mapping: display -> product_id
        
        for p in products:
            product_id = p.get('product_id', '')
            product_display = f"{p.get('name', 'Unknown')} - ${p.get('price', 0):.2f}"
            product_list.append(product_display)
            self.script_product_map[product_display] = product_id
        
        self.script_product_combo['values'] = product_list
        if product_list:
            self.script_product_combo.current(0)
    
    def test_openai_api_key(self):
        """Test if selected AI provider API key is valid"""
        if not hasattr(self, 'api_status_label'):
            return
        
        # Get selected provider
        provider = self.script_provider_var.get() if hasattr(self, 'script_provider_var') else 'openai'
        
        self.api_status_label.config(text="Testing API key...", fg='blue')
        self.update_status(f"Testing {provider.upper()} API key...")
        
        def test_task():
            try:
                # Reload credentials
                self.root.after(0, lambda: self.update_status("🔄 Reloading credentials..."))
                self._reload_credentials_and_ai()
                
                # Get API key based on provider
                if provider == 'groq':
                    self.root.after(0, lambda: self.update_status("🔄 Validating Groq API key..."))
                    api_key = (self.credentials.get('groq_api_key') or '').strip()
                    if not api_key and hasattr(self, 'cred_entries') and 'groq_api_key' in self.cred_entries:
                        api_key = self.cred_entries['groq_api_key'].get().strip()
                    
                    if not api_key:
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: No Groq API key found", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "API Key Not Found",
                            "Groq API key not found in credentials.\n\n"
                            "Please add your API key in Settings tab or .env file."))
                        return
                    
                    # Try to import Groq
                    try:
                        from groq import Groq
                    except ImportError:
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: Groq package not installed", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "Package Missing",
                            "Groq package is not installed.\n\n"
                            "Please install it by running:\n"
                            "python -m pip install groq"))
                        return
                    
                    # Create client and test
                    self.root.after(0, lambda: self.update_status("🔄 Testing Groq API connection..."))
                    client = Groq(api_key=api_key)
                    self.root.after(0, lambda: self.update_status("🔄 Sending test request to Groq..."))
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",  # Updated: replaced deprecated llama-3.1-70b-versatile
                        messages=[{"role": "user", "content": "Say 'test'"}],
                        max_tokens=5
                    )
                    
                    model_used = response.model
                    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'
                    
                    self.root.after(0, lambda: self.api_status_label.config(
                        text=f"✅ Status: Groq API key valid (Model: {model_used})", fg='green'))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "API Key Valid",
                        f"✅ Groq API key is valid and working!\n\n"
                        f"Model: {model_used}\n"
                        f"Test tokens used: {tokens_used}\n\n"
                        f"API key format: {api_key[:7]}...{api_key[-4:] if len(api_key) > 11 else ''}"))
                    self.root.after(0, lambda: self.update_status("✅ Groq API key verified"))
                    
                else:  # openai
                    self.root.after(0, lambda: self.update_status("🔄 Validating OpenAI API key..."))
                    api_key = (self.credentials.get('openai_api_key') or '').strip()
                    if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
                        if hasattr(self, 'cred_entries') and 'openai_api_key' in self.cred_entries:
                            api_key = self.cred_entries['openai_api_key'].get().strip()
                    
                    if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: No API key found", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "API Key Not Found",
                            "OpenAI API key not found in credentials.\n\n"
                            "Please add your API key in Settings tab or .env file."))
                        return
                    
                    # Try to import OpenAI
                    try:
                        import openai
                    except ImportError:
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: OpenAI package not installed", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "Package Missing",
                            "OpenAI package is not installed.\n\n"
                            "Please install it by running:\n"
                            "python -m pip install openai"))
                        return
                    
                    # Create client and test with a simple request
                    self.root.after(0, lambda: self.update_status("🔄 Testing OpenAI API connection..."))
                    client = openai.OpenAI(api_key=api_key)
                    self.root.after(0, lambda: self.update_status("🔄 Sending test request to OpenAI..."))
                    # Make a minimal test call
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Say 'test'"}],
                        max_tokens=5
                    )
                    
                    # Success!
                    model_used = response.model
                    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'
                    
                    self.root.after(0, lambda: self.api_status_label.config(
                        text=f"✅ Status: API key valid (Model: {model_used})", fg='green'))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "API Key Valid",
                        f"✅ OpenAI API key is valid and working!\n\n"
                        f"Model: {model_used}\n"
                        f"Test tokens used: {tokens_used}\n\n"
                        f"API key format: {api_key[:7]}...{api_key[-4:] if len(api_key) > 11 else ''}"))
                    self.root.after(0, lambda: self.update_status("✅ OpenAI API key verified"))
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"{provider.upper()} API test failed: {e}", exc_info=True)
                
                # Parse common errors
                if "401" in error_msg or "invalid" in error_msg.lower() or "authentication" in error_msg.lower():
                    status_msg = f"❌ Status: Invalid {provider.upper()} API key"
                    detail_msg = f"The {provider.upper()} API key is invalid or incorrect.\n\nPlease check your API key in Settings or .env file."
                elif "429" in error_msg or "rate limit" in error_msg.lower():
                    status_msg = f"⚠️ Status: Rate limit exceeded"
                    detail_msg = "Rate limit exceeded.\n\nPlease wait a moment and try again."
                elif "insufficient_quota" in error_msg.lower() or "quota" in error_msg.lower():
                    status_msg = f"❌ Status: Insufficient credits/quota"
                    detail_msg = f"Insufficient credits or quota.\n\nPlease add credits to your {provider.upper()} account."
                else:
                    status_msg = f"❌ Status: Error - {error_msg[:50]}"
                    detail_msg = f"Failed to test {provider.upper()} API key:\n\n{error_msg}"
                
                self.root.after(0, lambda: self.api_status_label.config(
                    text=status_msg, fg='red'))
                self.root.after(0, lambda: messagebox.showerror("API Test Failed", detail_msg))
                self.root.after(0, lambda: self.update_status(f"❌ {provider.upper()} API test failed"))
        
        threading.Thread(target=test_task, daemon=True).start()
    
    def check_openai_usage(self):
        """Check selected AI provider API usage and credits"""
        if not hasattr(self, 'api_status_label'):
            return
        
        # Get selected provider
        provider = self.script_provider_var.get() if hasattr(self, 'script_provider_var') else 'openai'
        
        self.api_status_label.config(text="Checking usage...", fg='blue')
        self.update_status(f"Checking {provider.upper()} usage...")
        
        def check_task():
            try:
                # Reload credentials
                self.root.after(0, lambda: self.update_status("🔄 Reloading credentials..."))
                self._reload_credentials_and_ai()
                
                # Get API key based on provider
                if provider == 'groq':
                    self.root.after(0, lambda: self.update_status("🔄 Checking Groq API key..."))
                    api_key = (self.credentials.get('groq_api_key') or '').strip()
                    if not api_key and hasattr(self, 'cred_entries') and 'groq_api_key' in self.cred_entries:
                        api_key = self.cred_entries['groq_api_key'].get().strip()
                    
                    if not api_key:
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: No Groq API key found", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "API Key Not Found",
                            "Groq API key not found in credentials."))
                        return
                    
                    # Try to import Groq
                    try:
                        from groq import Groq
                    except ImportError:
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: Groq package not installed", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "Package Missing",
                            "Groq package is not installed."))
                        return
                    
                    # Create client
                    self.root.after(0, lambda: self.update_status("🔄 Connecting to Groq API..."))
                    client = Groq(api_key=api_key)
                    self.root.after(0, lambda: self.update_status("🔄 Fetching usage information..."))
                    
                    # Make a test call to get usage info
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",  # Updated: replaced deprecated llama-3.1-70b-versatile
                        messages=[{"role": "user", "content": "Say 'usage test'"}],
                        max_tokens=10
                    )
                    
                    # Extract usage information
                    self.root.after(0, lambda: self.update_status("🔄 Processing usage data..."))
                    usage_info = []
                    if hasattr(response, 'usage'):
                        usage = response.usage
                        usage_info.append(f"Prompt tokens: {usage.prompt_tokens}")
                        usage_info.append(f"Completion tokens: {usage.completion_tokens}")
                        usage_info.append(f"Total tokens: {usage.total_tokens}")
                    
                    billing_info = "✅ Groq API key is active and working"
                    
                    # Format message
                    info_lines = [
                        "📊 Groq Usage Information",
                        "",
                        billing_info,
                        ""
                    ]
                    
                    if usage_info:
                        info_lines.extend(usage_info)
                        info_lines.append("")
                    
                    info_lines.extend([
                        "ℹ️ Note: Groq offers free tier with generous limits.",
                        "Check your usage dashboard at:",
                        "https://console.groq.com/",
                        "",
                        "💡 Tip: Groq is fast and offers free tier for testing."
                    ])
                    
                    message = "\n".join(info_lines)
                    
                    self.root.after(0, lambda: self.api_status_label.config(
                        text="✅ Status: Groq usage checked", fg='green'))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Groq Usage Information",
                        message))
                    self.root.after(0, lambda: self.update_status("✅ Groq usage checked"))
                    
                else:  # openai
                    self.root.after(0, lambda: self.update_status("🔄 Checking OpenAI API key..."))
                    api_key = (self.credentials.get('openai_api_key') or '').strip()
                    if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
                        if hasattr(self, 'cred_entries') and 'openai_api_key' in self.cred_entries:
                            api_key = self.cred_entries['openai_api_key'].get().strip()
                    
                    if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: No OpenAI API key found", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "API Key Not Found",
                            "OpenAI API key not found in credentials."))
                        return
                    
                    # Try to import OpenAI
                    try:
                        import openai
                    except ImportError:
                        self.root.after(0, lambda: self.api_status_label.config(
                            text="❌ Status: OpenAI package not installed", fg='red'))
                        self.root.after(0, lambda: messagebox.showerror(
                            "Package Missing",
                            "OpenAI package is not installed."))
                        return
                    
                    # Create client
                    self.root.after(0, lambda: self.update_status("🔄 Connecting to OpenAI API..."))
                    client = openai.OpenAI(api_key=api_key)
                    self.root.after(0, lambda: self.update_status("🔄 Fetching usage information..."))
                    
                    # Make a test call to get usage info
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Say 'usage test'"}],
                        max_tokens=10
                    )
                    
                    # Extract usage information
                    self.root.after(0, lambda: self.update_status("🔄 Processing usage data..."))
                    usage_info = []
                    if hasattr(response, 'usage'):
                        usage = response.usage
                        usage_info.append(f"Prompt tokens: {usage.prompt_tokens}")
                        usage_info.append(f"Completion tokens: {usage.completion_tokens}")
                        usage_info.append(f"Total tokens: {usage.total_tokens}")
                    
                    # Try to get billing/subscription info (if available)
                    try:
                        # Note: OpenAI doesn't have a direct credits endpoint, but we can check if the key works
                        # and show usage from the test call
                        billing_info = "✅ OpenAI API key is active and working"
                    except Exception as e:
                        billing_info = f"Could not retrieve billing info: {str(e)}"
                    
                    # Format message
                    info_lines = [
                        "📊 OpenAI Usage Information",
                        "",
                        billing_info,
                        ""
                    ]
                    
                    if usage_info:
                        info_lines.extend(usage_info)
                        info_lines.append("")
                    
                    info_lines.extend([
                        "ℹ️ Note: OpenAI uses pay-as-you-go billing.",
                        "Check your usage dashboard at:",
                        "https://platform.openai.com/usage",
                        "",
                        "💡 Tip: Monitor your usage regularly to avoid unexpected charges."
                    ])
                    
                    message = "\n".join(info_lines)
                    
                    self.root.after(0, lambda: self.api_status_label.config(
                        text="✅ Status: OpenAI usage checked", fg='green'))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "OpenAI Usage Information",
                        message))
                    self.root.after(0, lambda: self.update_status("✅ OpenAI usage checked"))
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"{provider.upper()} usage check failed: {e}", exc_info=True)
                
                if "401" in error_msg or "invalid" in error_msg.lower():
                    status_msg = f"❌ Status: Invalid {provider.upper()} API key"
                    detail_msg = f"Cannot check usage: Invalid {provider.upper()} API key."
                elif "insufficient_quota" in error_msg.lower() or "quota" in error_msg.lower():
                    status_msg = f"❌ Status: Insufficient credits"
                    if provider == 'groq':
                        detail_msg = ("⚠️ Your Groq account has insufficient credits/quota.\n\n"
                                    "Please check your Groq account:\n"
                                    "https://console.groq.com/")
                    else:
                        detail_msg = ("⚠️ Your OpenAI account has insufficient credits/quota.\n\n"
                                    "Please add credits to your OpenAI account:\n"
                                    "https://platform.openai.com/account/billing")
                else:
                    status_msg = f"❌ Status: Error checking usage"
                    detail_msg = f"Failed to check {provider.upper()} usage:\n\n{error_msg}"
                
                self.root.after(0, lambda: self.api_status_label.config(
                    text=status_msg, fg='red'))
                self.root.after(0, lambda: messagebox.showerror("Usage Check Failed", detail_msg))
                self.root.after(0, lambda: self.update_status(f"❌ {provider.upper()} usage check failed"))
        
        threading.Thread(target=check_task, daemon=True).start()
    
    def _update_provider_status(self):
        """Update API status label based on selected provider"""
        provider = self.script_provider_var.get()
        if provider == "groq":
            self.api_status_label.config(text="Provider: Groq AI", fg='blue')
        elif provider == "apify":
            self.api_status_label.config(text="Provider: Apify", fg='blue')
        else:
            self.api_status_label.config(text="Provider: OpenAI", fg='blue')
    
    def generate_script(self):
        """Generate video script using selected AI provider (OpenAI, Groq, or Apify)"""
        # Get selected product
        selected_product = self.script_product_var.get()
        if not selected_product:
            messagebox.showwarning("No Product Selected", "Please select a product first")
            return
        
        # Get product_id from mapping
        product_id = getattr(self, 'script_product_map', {}).get(selected_product)
        if not product_id:
            messagebox.showerror("Error", "Could not find selected product")
            return
        
        # Get product from database using product_id
        products = self.db.get_products()
        product = next((p for p in products if p.get('product_id') == product_id), None)
        
        if not product:
            messagebox.showerror("Error", "Could not find selected product in database")
            return
        
        # Get selected provider
        provider = self.script_provider_var.get()
        if provider not in ['openai', 'groq', 'apify']:
            messagebox.showerror("Invalid Provider", "Please select a valid AI provider")
            return
        
        # Reload credentials
        self._reload_credentials_and_ai()
        
        # Get API key based on provider
        if provider == 'groq':
            api_key = (self.credentials.get('groq_api_key') or '').strip()
            if not api_key and hasattr(self, 'cred_entries') and 'groq_api_key' in self.cred_entries:
                api_key = self.cred_entries['groq_api_key'].get().strip()
            
            if not api_key or len(api_key) < 10:
                error_msg = ("Groq API key is not configured.\n\n"
                             f"Found key length: {len(api_key) if api_key else 0}\n\n"
                             "Please add your Groq API key in Settings tab or .env file.\n"
                             "Format: GROQ_API_KEY=gsk_...")
                messagebox.showerror("Groq Not Configured", error_msg)
                return
        elif provider == 'apify':
            api_key = (self.credentials.get('apify_api_key') or '').strip()
            if not api_key and hasattr(self, 'cred_entries') and 'apify_api_key' in self.cred_entries:
                api_key = self.cred_entries['apify_api_key'].get().strip()
            
            if not api_key or len(api_key) < 10:
                error_msg = ("Apify API key is not configured.\n\n"
                             f"Found key length: {len(api_key) if api_key else 0}\n\n"
                             "Please add your Apify API key in Settings tab or .env file.\n"
                             "Format: APIFY_API_KEY=apify_...")
                messagebox.showerror("Apify Not Configured", error_msg)
                return
        else:  # openai
            api_key = (self.credentials.get('openai_api_key') or '').strip()
            if not api_key and hasattr(self, 'cred_entries') and 'openai_api_key' in self.cred_entries:
                api_key = self.cred_entries['openai_api_key'].get().strip()
            
            if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE' or len(api_key) < 10:
                error_msg = ("OpenAI API key is not configured.\n\n"
                             f"Found key length: {len(api_key) if api_key else 0}\n\n"
                             "Please add your OpenAI API key in Settings tab or .env file.\n"
                             "Format: OPENAI_API_KEY=sk-...")
                messagebox.showerror("OpenAI Not Configured", error_msg)
                return
        
        # Update status
        self.script_status_label.config(text=f"Generating script using {provider.upper()}...", fg='blue')
        self.update_status(f"Generating AI script using {provider.upper()}...")
        
        def task():
            try:
                # Prepare script generation prompt
                self.root.after(0, lambda: self.update_status("🔄 Preparing script request..."))
                tone = self.script_tone_var.get()
                duration = int(self.script_duration_var.get())
                language = self.script_language_var.get()
                notes = self.script_notes_text.get('1.0', tk.END).strip()
                
                # Build language instruction based on selection
                language_instruction = ""
                if language == "English":
                    language_instruction = "Write the entire script in English only."
                elif language == "Filipino":
                    language_instruction = "Write the entire script in Filipino (Tagalog) only. Use natural Filipino expressions and colloquialisms."
                elif language == "Filipino and English":
                    language_instruction = "Write the script mixing Filipino (Tagalog) and English naturally, as Filipinos commonly speak. Use 'Taglish' (Tagalog-English mix) where appropriate."
                
                prompt = f"""Create an engaging TikTok video script for this product:

Product: {product['name']}
Price: ${product['price']:.2f} (₱{product['price'] * 56:.2f} PHP)
Category: {product.get('category', 'General')}
Rating: {product.get('rating', 4.5)}/5.0
Commission: ${product['commission_amount']:.2f} ({product['commission_rate']:.1f}%)

Script Requirements:
- Tone: {tone}
- Duration: {duration} seconds
- Language: {language_instruction}
- Hook viewers immediately
- Highlight key benefits
- Create urgency/scarcity
- Clear call-to-action
- Use natural, conversational language
- Optimize for TikTok's short-form format"""

                if notes:
                    prompt += f"\n\nAdditional Instructions:\n{notes}"
                
                prompt += "\n\nProvide the script as readable text that can be narrated in a video."

                # Generate script using selected provider
                if provider == 'groq':
                    try:
                        from groq import Groq
                        self.root.after(0, lambda: self.update_status("🔄 Connecting to Groq API..."))
                        client = Groq(api_key=api_key)
                        self.root.after(0, lambda: self.update_status("🔄 Generating script with Groq AI..."))
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",  # Updated: replaced deprecated llama-3.1-70b-versatile
                            messages=[
                                {"role": "system", "content": "You are a professional TikTok video script writer specializing in product marketing and viral content."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.8,
                            max_tokens=500
                        )
                        self.root.after(0, lambda: self.update_status("🔄 Processing script response..."))
                        script = response.choices[0].message.content.strip()
                    except ImportError:
                        raise ImportError("Groq package not installed. Install with: python -m pip install groq")
                    except Exception as e:
                        raise Exception(f"Groq API error: {str(e)}")
                elif provider == 'apify':
                    try:
                        from apify_client import ApifyClient
                        self.root.after(0, lambda: self.update_status("🔄 Connecting to Apify API..."))
                        client = ApifyClient(api_key)
                        
                        # Get actor ID from settings or use default
                        actor_id = ""
                        if hasattr(self, 'cred_entries') and 'apify_actor_id' in self.cred_entries:
                            actor_id = self.cred_entries['apify_actor_id'].get().strip()
                        
                        # Also check credentials (loaded from .env or credentials.json)
                        if not actor_id:
                            actor_id = (self.credentials.get('apify_actor_id') or '').strip()
                        
                        # If no actor ID configured, use OpenAI directly through Apify API key
                        # (This assumes Apify API key can be used with OpenAI, or fallback to OpenAI)
                        if not actor_id:
                            # Try to use OpenAI directly if Apify API key format matches OpenAI
                            # Otherwise, suggest configuring an actor
                            error_msg = ("Apify Actor ID not configured.\n\n"
                                       "Please configure an Apify Actor ID in Settings tab or .env file.\n"
                                       "Format: username~actorName (e.g., apify~web-scraper)\n\n"
                                       "Or use OpenAI/Groq providers directly for script generation.")
                            raise Exception(error_msg)
                        
                        self.root.after(0, lambda: self.update_status(f"🔄 Running Apify actor: {actor_id}..."))
                        
                        # Validate actor exists before running
                        try:
                            actor_info = client.actor(actor_id).get()
                            if not actor_info or (isinstance(actor_info, dict) and not actor_info.get('data')):
                                raise Exception(f"Actor '{actor_id}' not found or not accessible")
                        except Exception as e:
                            error_msg = str(e)
                            if 'not found' in error_msg.lower() or '404' in error_msg or 'does not exist' in error_msg.lower():
                                raise Exception(
                                    f"Actor '{actor_id}' not found.\n\n"
                                    "Please check:\n"
                                    "1. The Actor ID format is correct (username~actorName or actor ID)\n"
                                    "2. The Actor exists in your Apify account\n"
                                    "3. You have access to this Actor\n"
                                    "4. Visit https://console.apify.com/actors to find/verify your Actor ID\n\n"
                                    f"Current Actor ID: {actor_id}\n\n"
                                    "Note: Actor IDs are case-sensitive and must match exactly."
                                )
                            raise
                        
                        # Run the actor with the prompt
                        run_input = {
                            "prompt": prompt,
                            "system_prompt": "You are a professional TikTok video script writer specializing in product marketing and viral content.",
                            "max_tokens": 500,
                            "temperature": 0.8
                        }
                        
                        # Try different input formats that actors might expect
                        try:
                            run = client.actor(actor_id).call(run_input=run_input)
                        except Exception as e:
                            error_msg = str(e)
                            # Check if it's an actor not found error
                            if 'not found' in error_msg.lower() or '404' in error_msg or 'does not exist' in error_msg.lower():
                                raise Exception(
                                    f"Actor '{actor_id}' not found.\n\n"
                                    "Please check:\n"
                                    "1. The Actor ID format is correct (username~actorName or actor ID)\n"
                                    "2. The Actor exists and is accessible\n"
                                    "3. You have the correct permissions\n"
                                    "4. Visit https://console.apify.com/actors to find/verify your Actor ID\n\n"
                                    f"Current Actor ID: {actor_id}\n\n"
                                    "Note: Actor IDs are case-sensitive and must match exactly."
                                )
                            # Try alternative input format
                            if "input" in error_msg.lower() or "invalid input" in error_msg.lower():
                                try:
                                    run_input_alt = {
                                        "input": {
                                            "prompt": prompt,
                                            "system_prompt": "You are a professional TikTok video script writer specializing in product marketing and viral content.",
                                            "max_tokens": 500,
                                            "temperature": 0.8
                                        }
                                    }
                                    run = client.actor(actor_id).call(run_input=run_input_alt)
                                except Exception as e2:
                                    raise Exception(f"Failed to run Apify actor '{actor_id}': {str(e2)}\n\nOriginal error: {str(e)}")
                            else:
                                raise Exception(f"Failed to run Apify actor '{actor_id}': {error_msg}")
                        
                        # Wait for the run to finish
                        self.root.after(0, lambda: self.update_status("🔄 Waiting for Apify actor to complete..."))
                        run_id = run['data']['id'] if isinstance(run, dict) and 'data' in run else run.get('id') if isinstance(run, dict) else str(run)
                        
                        # Poll for completion
                        import time
                        max_wait_time = 300  # 5 minutes max
                        wait_time = 0
                        while wait_time < max_wait_time:
                            try:
                                run_status = client.run(run_id).get()
                                status = run_status.get('data', {}).get('status') if isinstance(run_status, dict) else run_status.get('status')
                                
                                if status in ['SUCCEEDED', 'SUCCEEDED_AND_TERMINATED']:
                                    break
                                elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                                    raise Exception(f"Apify actor failed with status: {status}")
                                
                                time.sleep(2)
                                wait_time += 2
                            except Exception as e:
                                error_msg = str(e)
                                if 'not found' in error_msg.lower() or '404' in error_msg:
                                    raise Exception(
                                        f"Actor '{actor_id}' not found.\n\n"
                                        "Please check:\n"
                                        "1. The Actor ID format is correct (username~actorName)\n"
                                        "2. The Actor exists in your Apify account\n"
                                        "3. You have access to this Actor\n"
                                        "4. Visit https://console.apify.com/actors to find your Actor ID\n\n"
                                        f"Current Actor ID: {actor_id}"
                                    )
                                raise Exception(f"Apify actor error: {error_msg}\n\nActor ID: {actor_id}")
                        
                        if wait_time >= max_wait_time:
                            raise Exception("Apify actor timed out after 5 minutes")
                        
                        # Get the dataset items
                        dataset_id = run_status.get('data', {}).get('defaultDatasetId') if isinstance(run_status, dict) else run_status.get('defaultDatasetId')
                        if not dataset_id:
                            raise Exception("Could not get dataset ID from Apify run")
                        
                        dataset_items = list(client.dataset(dataset_id).list_items())
                        
                        if not dataset_items:
                            raise Exception("Apify actor returned no results")
                        
                        # Extract script from the first item
                        result = dataset_items[0]
                        # Handle different response formats
                        script = None
                        if isinstance(result, dict):
                            if 'text' in result:
                                script = result['text'].strip()
                            elif 'content' in result:
                                script = result['content'].strip()
                            elif 'message' in result:
                                script = result['message'].strip()
                            elif 'script' in result:
                                script = result['script'].strip()
                            elif 'output' in result:
                                script = str(result['output']).strip()
                            elif 'result' in result:
                                script = str(result['result']).strip()
                            else:
                                # Try to get any text-like field
                                for key in ['response', 'generated_text', 'completion', 'answer']:
                                    if key in result:
                                        script = str(result[key]).strip()
                                        break
                        
                        if not script:
                            # Last resort: convert entire result to string
                            script = str(result).strip()
                        
                        if not script or script == '{}' or script == '[]':
                            raise Exception("Could not extract script from Apify response. Check actor output format.")
                        
                        self.root.after(0, lambda: self.update_status("🔄 Processing script response..."))
                    except ImportError:
                        raise ImportError("Apify package not installed. Install with: python -m pip install apify-client")
                    except Exception as e:
                        raise Exception(f"Apify API error: {str(e)}")
                else:  # openai
                    try:
                        import openai
                        self.root.after(0, lambda: self.update_status("🔄 Connecting to OpenAI API..."))
                        client = openai.OpenAI(api_key=api_key)
                        self.root.after(0, lambda: self.update_status("🔄 Generating script with OpenAI..."))
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a professional TikTok video script writer specializing in product marketing and viral content."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.8,
                            max_tokens=500
                        )
                        self.root.after(0, lambda: self.update_status("🔄 Processing script response..."))
                        script = response.choices[0].message.content.strip()
                    except ImportError:
                        raise ImportError("OpenAI package not installed. Install with: python -m pip install openai")
                    except Exception as e:
                        raise Exception(f"OpenAI API error: {str(e)}")
                
                # Update GUI with result
                self.root.after(0, lambda: self.generated_script_text.delete('1.0', tk.END))
                self.root.after(0, lambda: self.generated_script_text.insert('1.0', script))
                self.root.after(0, lambda: self.script_status_label.config(
                    text=f"✓ Script generated successfully using {provider.upper()}!", fg='green'))
                self.root.after(0, lambda: self.update_status(f"✓ Script generated using {provider.upper()}"))
                
            except Exception as e:
                logger.error(f"Error generating script: {e}", exc_info=True)
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Failed to generate script:\n{str(e)}\n\n"
                    f"Make sure {provider.upper()} API key is valid and you have available credits."))
                self.root.after(0, lambda: self.script_status_label.config(
                    text=f"❌ Script generation failed", fg='red'))
                self.root.after(0, lambda: self.update_status(f"❌ Script generation failed"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def create_video_from_script(self):
        """Create a video using the generated script with narration and subtitles"""
        # Get generated script
        script = self.generated_script_text.get('1.0', tk.END).strip()
        
        if not script:
            messagebox.showwarning("No Script", "Please generate a script first")
            return
        
        # Get selected product
        selected_product = self.script_product_var.get()
        if not selected_product:
            messagebox.showwarning("No Product Selected", "Please select a product first")
            return
        
        # Get product_id from mapping
        product_id = getattr(self, 'script_product_map', {}).get(selected_product)
        if not product_id:
            messagebox.showerror("Error", "Could not find selected product")
            return
        
        # Get product from database using product_id
        products = self.db.get_products()
        product = next((p for p in products if p.get('product_id') == product_id), None)
        
        if not product:
            messagebox.showerror("Error", "Could not find selected product in database")
            return
        
        # Get script duration
        try:
            script_duration = int(self.script_duration_var.get())
        except:
            script_duration = 15
        
        self.update_status("Creating video from script...")
        self.script_status_label.config(text="Creating video with script narration...", fg='blue')
        
        def task():
            try:
                self.root.after(0, lambda: self.update_status("🔄 Generating narration from script..."))
                
                # Generate narration audio using ElevenLabs or fallback
                narration_audio_path = None
                elevenlabs_key = (self.credentials.get('elevenlabs_api_key') or '').strip()
                if not elevenlabs_key and hasattr(self, 'cred_entries') and 'elevenlabs_api_key' in self.cred_entries:
                    elevenlabs_key = self.cred_entries['elevenlabs_api_key'].get().strip()
                
                if elevenlabs_key and len(elevenlabs_key) > 10:
                    # Use ElevenLabs for high-quality narration
                    try:
                        import requests
                        self.root.after(0, lambda: self.update_status("🔄 Generating voiceover with ElevenLabs..."))
                        
                        narration_audio_path = VIDEOS_DIR / f"{product['product_id']}_narration.mp3"
                        
                        # Call ElevenLabs API
                        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Default voice
                        headers = {
                            "Accept": "audio/mpeg",
                            "Content-Type": "application/json",
                            "xi-api-key": elevenlabs_key
                        }
                        data = {
                            "text": script,
                            "model_id": "eleven_monolingual_v1",
                            "voice_settings": {
                                "stability": 0.5,
                                "similarity_boost": 0.75
                            }
                        }
                        
                        response = requests.post(url, json=data, headers=headers, timeout=60)
                        if response.status_code == 200:
                            with open(narration_audio_path, 'wb') as f:
                                f.write(response.content)
                            logger.info("Generated narration with ElevenLabs")
                        else:
                            logger.warning(f"ElevenLabs API error: {response.status_code}")
                            narration_audio_path = None
                    except Exception as e:
                        logger.warning(f"Could not use ElevenLabs: {e}")
                        narration_audio_path = None
                
                # Generate caption and hashtags
                self.root.after(0, lambda: self.update_status("🔄 Generating caption and hashtags..."))
                caption, hashtags = self.caption_generator.create_full_post(product)
                
                # Create video with script
                self.root.after(0, lambda: self.update_status("🔄 Creating video with script..."))
                video_path = VIDEOS_DIR / f"{product['product_id']}_script_video.mp4"
                
                # Create video with script narration and subtitles
                success = self.video_creator.create_product_video_with_script(
                    product=product,
                    script=script,
                    output_path=video_path,
                    narration_audio_path=narration_audio_path,
                    duration=script_duration,
                    template=self.script_tone_var.get().lower() if self.script_tone_var.get().lower() in ['modern', 'minimal', 'energetic'] else 'modern'
                )
                
                if success:
                    # Save video to database
                    self.root.after(0, lambda: self.db.add_video({
                        'product_id': product['product_id'],
                        'video_path': str(video_path),
                        'caption': caption,
                        'hashtags': hashtags,
                        'script': script,  # Store the script
                        'status': 'created'
                    }))
                    
                    self.root.after(0, lambda: self.db.update_product_status(product['product_id'], 'video_created'))
                    self.root.after(0, self.refresh_videos)
                    
                    narration_info = "with AI voiceover" if narration_audio_path else "with subtitles"
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success!",
                        f"Video created successfully!\n\n"
                        f"Product: {product.get('name', 'Unknown')}\n"
                        f"Video saved to: {video_path.name}\n"
                        f"Duration: {script_duration} seconds\n"
                        f"Features: {narration_info}\n\n"
                        f"The script has been incorporated into the video."
                    ))
                    self.root.after(0, lambda: self.script_status_label.config(
                        text=f"✅ Video created successfully!", fg='green'))
                    self.root.after(0, lambda: self.update_status("✅ Video created!"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to create video"))
                    self.root.after(0, lambda: self.script_status_label.config(
                        text="❌ Video creation failed", fg='red'))
                    self.root.after(0, lambda: self.update_status("❌ Video creation failed"))
                    
            except Exception as e:
                logger.error(f"Error creating video from script: {e}", exc_info=True)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to create video:\n{str(e)}"))
                self.root.after(0, lambda: self.script_status_label.config(
                    text="❌ Error occurred", fg='red'))
                self.root.after(0, lambda: self.update_status("❌ Error occurred"))
        
        threading.Thread(target=task, daemon=True).start()

    def update_stats(self):
        """Update statistics"""
        stats = self.db.get_stats()
        for key, var in self.stats_vars.items():
            var.set(str(stats.get(key, 0)))

    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)

    def setup_gui_logging(self):
        """Setup logging to GUI"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            def emit(self, record):
                msg = self.format(record) + '\n'
                self.text_widget.insert(tk.END, msg)
                self.text_widget.see(tk.END)
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                       handlers=[logging.FileHandler(LOG_CONFIG['log_file']), logging.StreamHandler()])
    app = ClickTokDashboard()
    app.run()


if __name__ == "__main__":
    main()
