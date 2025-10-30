"""
ClickTok - TikTok Affiliate Marketing Automation System
Main Entry Point

Usage:
    python main.py                    # Launch GUI dashboard
    python main.py --cli              # Command-line interface
    python main.py --help             # Show help
"""
import sys
import logging
from pathlib import Path
import argparse
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """
    Check if all required dependencies are installed
    Returns True if all OK, False if missing dependencies
    """
    missing_packages = []
    required_packages = [
        ('moviepy', 'moviepy'),
        ('playwright', 'playwright'),
        ('PIL', 'Pillow'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
    ]

    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print("=" * 70)
        print("  ⚠️  MISSING DEPENDENCIES DETECTED")
        print("=" * 70)
        print("\nThe following packages are not installed:")
        for pkg in missing_packages:
            print(f"  • {pkg}")

        print("\nYou have two options:\n")
        print("Option 1 (Recommended): Run the automated setup")
        print("  python setup.py")
        print("  OR")
        print("  setup.bat (Windows) / ./setup.sh (Mac/Linux)")
        print("\nOption 2: Install manually")
        print("  pip install -r requirements.txt")
        print("  python -m playwright install chromium")
        print("\n" + "=" * 70)

        response = input("\nRun automated setup now? (y/n): ").strip().lower()
        if response == 'y':
            print("\nLaunching setup.py...\n")
            try:
                result = subprocess.run([sys.executable, "setup.py"], check=True)
                if result.returncode == 0:
                    print("\n✅ Setup complete! Please restart ClickTok.")
                    return False
            except subprocess.CalledProcessError:
                print("\n❌ Setup failed. Please install manually.")
                return False
        else:
            print("\nPlease install dependencies and try again.")
            return False

    return True


from config.settings import LOG_CONFIG
from gui.dashboard import ClickTokDashboard


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=LOG_CONFIG['log_level'],
        format=LOG_CONFIG['log_format'],
        handlers=[
            logging.FileHandler(LOG_CONFIG['log_file']),
            logging.StreamHandler()
        ]
    )


def launch_gui():
    """Launch the GUI dashboard"""
    print("=" * 60)
    print("  ClickTok - TikTok Affiliate Marketing Automation")
    print("=" * 60)
    print("\nLaunching dashboard...\n")

    app = ClickTokDashboard()
    app.run()


def launch_cli():
    """Launch CLI interface"""
    from src.database import Database
    from src.product_fetcher import ProductFetcher
    from src.video_creator import VideoCreator
    from src.caption_generator import CaptionGenerator
    from config.settings import *
    import json

    print("=" * 60)
    print("  ClickTok CLI")
    print("=" * 60)

    # Load credentials
    with open(BASE_DIR / "config" / "credentials.json") as f:
        credentials = json.load(f)

    db = Database(DATABASE_PATH)

    while True:
        print("\n" + "=" * 60)
        print("Main Menu:")
        print("1. Fetch Products")
        print("2. View Products")
        print("3. Create Videos")
        print("4. View Videos")
        print("5. Statistics")
        print("6. Exit")
        print("=" * 60)

        choice = input("\nSelect option: ").strip()

        if choice == '1':
            fetcher = ProductFetcher(credentials, PRODUCT_FILTERS)
            print("\nFetching products...")
            products = fetcher.fetch_trending_products(limit=20)
            for product in products:
                db.add_product(product)
            print(f"\nFetched {len(products)} products!")

        elif choice == '2':
            products = db.get_products()
            print(f"\n{len(products)} Products:")
            for p in products[:10]:
                print(f"  - {p['name']} | ${p['price']} | {p['commission_rate']}% | {p['status']}")

        elif choice == '3':
            products = db.get_products(status='selected')
            if not products:
                print("\nNo products selected. Please select products first.")
                continue

            creator = VideoCreator(VIDEO_CONFIG, ASSETS_DIR)
            caption_gen = CaptionGenerator(AI_CONFIG, HASHTAG_CONFIG, credentials)

            print(f"\nCreating videos for {len(products)} products...")
            for product in products:
                print(f"  Creating: {product['name']}")
                caption, hashtags = caption_gen.create_full_post(product)
                video_path = VIDEOS_DIR / f"{product['product_id']}_video.mp4"
                if creator.create_product_video(product, video_path):
                    db.add_video({
                        'product_id': product['product_id'],
                        'video_path': str(video_path),
                        'caption': caption,
                        'hashtags': hashtags,
                        'status': 'created'
                    })
                    print(f"    ✓ Created: {video_path.name}")

        elif choice == '4':
            videos = db.get_videos()
            print(f"\n{len(videos)} Videos:")
            for v in videos[:10]:
                print(f"  - {v['product_id']} | {v['status']} | {v['date_created']}")

        elif choice == '5':
            stats = db.get_stats()
            print("\nStatistics:")
            print(f"  Total Products: {stats['total_products']}")
            print(f"  Total Videos: {stats['total_videos']}")
            print(f"  Posted Videos: {stats['posted_videos']}")
            print(f"  Total Views: {stats['total_views']}")
            print(f"  Total Likes: {stats['total_likes']}")

        elif choice == '6':
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ClickTok - TikTok Affiliate Marketing Automation')
    parser.add_argument('--cli', action='store_true', help='Launch CLI interface')
    parser.add_argument('--version', action='version', version='ClickTok 1.0.0')
    parser.add_argument('--skip-check', action='store_true', help='Skip dependency check')

    args = parser.parse_args()

    # Check dependencies (unless skipped)
    if not args.skip_check:
        if not check_dependencies():
            print("\n❌ Cannot start ClickTok without dependencies.")
            print("Please run: python setup.py")
            sys.exit(1)

    # Setup logging
    setup_logging()

    # Launch appropriate interface
    if args.cli:
        launch_cli()
    else:
        launch_gui()


if __name__ == "__main__":
    main()
