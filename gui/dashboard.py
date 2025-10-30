"""
ClickTok GUI Dashboard
Main user interface for managing the TikTok automation system
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
import logging
from typing import Dict
import sys
import json

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

    def _load_credentials(self) -> Dict:
        """Load credentials from config file"""
        cred_file = BASE_DIR / "config" / "credentials.json"
        try:
            with open(cred_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load credentials: {e}")
            return {}

    def setup_ui(self):
        """Setup the main UI layout"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_dashboard_tab()
        self.create_products_tab()
        self.create_videos_tab()
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
        """Products tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Products")

        toolbar = tk.Frame(tab)
        toolbar.pack(fill='x', padx=10, pady=10)
        ttk.Button(toolbar, text="Fetch Products", command=self.fetch_products).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_products).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Select for Videos", command=self.select_products_for_video).pack(side='left', padx=5)

        # Table
        table_frame = tk.Frame(tab)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        v_scroll = ttk.Scrollbar(table_frame)
        v_scroll.pack(side='right', fill='y')

        columns = ('ID', 'Name', 'Price', 'Commission', 'Rating', 'Status')
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=v_scroll.set)

        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=150 if col == 'Name' else 100)

        self.products_tree.pack(fill='both', expand=True)
        v_scroll.config(command=self.products_tree.yview)

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
        """Fetch products"""
        self.update_status("Fetching products...")
        def task():
            try:
                products = self.product_fetcher.fetch_trending_products(limit=20)
                for product in products:
                    self.db.add_product(product)
                self.root.after(0, self.refresh_products)
                self.root.after(0, lambda: self.update_status(f"Fetched {len(products)} products"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Fetched {len(products)} products!"))
            except Exception as e:
                logger.error(f"Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=task, daemon=True).start()

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

        # TikTok Account Section
        tiktok_frame = ttk.LabelFrame(scrollable_frame, text="🎵 TikTok Account", padding=20)
        tiktok_frame.pack(fill='x', padx=40, pady=10)

        self._create_entry(tiktok_frame, "Username:", "tiktok.username", 0)
        self._create_entry(tiktok_frame, "Password:", "tiktok.password", 1, show='*')
        self._create_entry(tiktok_frame, "Cookies File:", "tiktok.cookies_file", 2)

        tk.Label(tiktok_frame, text="ℹ️ Your TikTok account credentials for posting videos",
                fg='gray', font=('Arial', 8)).grid(row=3, column=0, columnspan=2, pady=(5,0), sticky='w')

        # TikTok Shop API Section
        shop_frame = ttk.LabelFrame(scrollable_frame, text="🛍️ TikTok Shop API (Optional)", padding=20)
        shop_frame.pack(fill='x', padx=40, pady=10)

        self._create_entry(shop_frame, "App Key:", "tiktok_shop_api.app_key", 0)
        self._create_entry(shop_frame, "App Secret:", "tiktok_shop_api.app_secret", 1, show='*')
        self._create_entry(shop_frame, "Access Token:", "tiktok_shop_api.access_token", 2, show='*')

        tk.Label(shop_frame, text="ℹ️ Required for fetching real TikTok Shop products. Leave empty to use demo mode.",
                fg='gray', font=('Arial', 8)).grid(row=3, column=0, columnspan=2, pady=(5,0), sticky='w')

        # AI API Keys Section
        ai_frame = ttk.LabelFrame(scrollable_frame, text="🤖 AI API Keys (Optional)", padding=20)
        ai_frame.pack(fill='x', padx=40, pady=10)

        self._create_entry(ai_frame, "OpenAI API Key:", "openai_api_key", 0, show='*')
        self._create_entry(ai_frame, "Anthropic API Key:", "anthropic_api_key", 1, show='*')
        self._create_entry(ai_frame, "ElevenLabs API Key:", "elevenlabs_api_key", 2, show='*')

        tk.Label(ai_frame, text="ℹ️ For AI-generated captions and voiceovers. Leave empty to use templates.",
                fg='gray', font=('Arial', 8)).grid(row=3, column=0, columnspan=2, pady=(5,0), sticky='w')

        # Buttons Frame
        btn_frame = tk.Frame(scrollable_frame)
        btn_frame.pack(pady=30)

        ttk.Button(btn_frame, text="💾 Save Settings", command=self.save_credentials,
                  width=20).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="🔄 Reload", command=self.load_credentials_to_ui,
                  width=20).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="📝 Test Connection", command=self.test_credentials,
                  width=20).pack(side='left', padx=10)

        # Status label
        self.settings_status = tk.Label(scrollable_frame, text="", font=('Arial', 10))
        self.settings_status.pack(pady=10)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load current credentials
        self.load_credentials_to_ui()

    def _create_entry(self, parent, label_text, key, row, show=None):
        """Helper to create labeled entry field"""
        tk.Label(parent, text=label_text, font=('Arial', 10)).grid(row=row, column=0,
                                                                    sticky='w', pady=8, padx=(0, 10))
        entry = ttk.Entry(parent, width=50, show=show)
        entry.grid(row=row, column=1, sticky='ew', pady=8)
        parent.columnconfigure(1, weight=1)
        self.cred_entries[key] = entry

    def load_credentials_to_ui(self):
        """Load credentials from file to UI fields"""
        try:
            cred_file = BASE_DIR / "config" / "credentials.json"
            with open(cred_file, 'r') as f:
                creds = json.load(f)

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

            self.cred_entries['elevenlabs_api_key'].delete(0, tk.END)
            self.cred_entries['elevenlabs_api_key'].insert(0, creds.get('elevenlabs_api_key', ''))

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

            self.settings_status.config(text="✅ Settings saved successfully!", fg='green')
            messagebox.showinfo("Success", "Settings saved successfully!\n\nCredentials have been updated.")

        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            self.settings_status.config(text=f"❌ Error saving: {str(e)}", fg='red')
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")

    def test_credentials(self):
        """Test if credentials are valid"""
        self.settings_status.config(text="🔄 Testing credentials...", fg='blue')

        def test_task():
            results = []

            # Test TikTok credentials
            tiktok_user = self.cred_entries['tiktok.username'].get()
            if tiktok_user and tiktok_user != "YOUR_TIKTOK_USERNAME":
                results.append("✅ TikTok username configured")
            else:
                results.append("⚠️ TikTok username not configured")

            # Test TikTok Shop API
            app_key = self.cred_entries['tiktok_shop_api.app_key'].get()
            if app_key and app_key != "YOUR_TIKTOK_SHOP_APP_KEY":
                results.append("✅ TikTok Shop API configured")
            else:
                results.append("ℹ️ TikTok Shop API not configured (demo mode)")

            # Test OpenAI
            openai_key = self.cred_entries['openai_api_key'].get()
            if openai_key and openai_key != "YOUR_OPENAI_API_KEY_HERE":
                results.append("✅ OpenAI API key configured")
            else:
                results.append("ℹ️ OpenAI not configured (template mode)")

            # Test Anthropic
            anthropic_key = self.cred_entries['anthropic_api_key'].get()
            if anthropic_key and anthropic_key != "YOUR_ANTHROPIC_API_KEY_HERE":
                results.append("✅ Anthropic API key configured")
            else:
                results.append("ℹ️ Anthropic not configured (template mode)")

            result_text = "\n".join(results)
            self.root.after(0, lambda: messagebox.showinfo("Credential Test Results", result_text))
            self.root.after(0, lambda: self.settings_status.config(text="✅ Test completed", fg='green'))

        threading.Thread(target=test_task, daemon=True).start()

    def refresh_products(self):
        """Refresh products table"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        for p in self.db.get_products():
            self.products_tree.insert('', 'end', values=(p['product_id'], p['name'][:40],
                f"${p['price']}", f"{p['commission_rate']}%", p['rating'], p['status']))

    def refresh_videos(self):
        """Refresh videos table"""
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        for v in self.db.get_videos():
            self.videos_tree.insert('', 'end', values=(v['id'], v['product_id'],
                v['status'], v['date_created'][:10] if v['date_created'] else ''))

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
