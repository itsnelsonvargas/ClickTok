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
    
    # Optional packages (check but don't fail if missing)
    optional_packages = [
        ('openai', 'openai'),
        ('groq', 'groq'),
        ('anthropic', 'anthropic'),
    ]

    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print("=" * 70)
        print("  ⚠️  MISSING DEPENDENCIES - Auto-Installing...")
        print("=" * 70)
        print("\nThe following packages are not installed:")
        for pkg in missing_packages:
            print(f"  • {pkg}")

        print("\n🔄 Starting automatic installation...")
        print("This will take about 5-10 minutes. Please wait...\n")

        try:
            # Run setup automatically
            setup_script = Path(__file__).parent / "setup.py"
            result = subprocess.run([sys.executable, str(setup_script)])

            if result.returncode == 0:
                print("\n" + "=" * 70)
                print("  ✅ Setup Complete!")
                print("=" * 70)
                print("\nDependencies installed successfully!")
                print("ClickTok will now start...\n")
                return True  # Continue to launch
            else:
                print("\n" + "=" * 70)
                print("  ❌ Setup Failed")
                print("=" * 70)
                print("\nAutomatic installation failed.")
                print("\nPlease try manual installation:")
                print("  1. Run: python setup.py")
                print("  2. Or run: setup.bat (Windows) / ./setup.sh (Mac/Linux)")
                print("  3. See: INSTALL.md for troubleshooting")
                print("\n" + "=" * 70)
                return False

        except Exception as e:
            print(f"\n❌ Error during setup: {e}")
            print("\nPlease install manually:")
            print("  pip install -r requirements.txt")
            print("  python -m playwright install chromium")
            return False

    return True


def setup_logging():
    """Setup logging configuration"""
    from config.settings import LOG_CONFIG

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
    from gui.dashboard import ClickTokDashboard

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
    import config.settings as settings
    import json

    print("=" * 60)
    print("  ClickTok CLI")
    print("=" * 60)

    # Load credentials
    cred_file = settings.BASE_DIR / "config" / "credentials.json"
    if not cred_file.exists():
        print("\n⚠️  Warning: credentials.json not found!")
        print("   Creating default credentials file from template...")
        example_file = settings.BASE_DIR / "config" / "credentials.json.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, cred_file)
            print("   ✓ Created credentials.json from template")
            print("   Please edit config/credentials.json with your credentials\n")
        else:
            print("   ⚠️  Template not found. Creating empty credentials file...")
            cred_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cred_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    with open(cred_file) as f:
        credentials = json.load(f)

    db = Database(settings.DATABASE_PATH)

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
            fetcher = ProductFetcher(credentials, settings.PRODUCT_FILTERS)
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

            creator = VideoCreator(settings.VIDEO_CONFIG, settings.ASSETS_DIR)
            caption_gen = CaptionGenerator(settings.AI_CONFIG, settings.HASHTAG_CONFIG, credentials)

            print(f"\nCreating videos for {len(products)} products...")
            for product in products:
                print(f"  Creating: {product['name']}")
                caption, hashtags = caption_gen.create_full_post(product)
                video_path = settings.VIDEOS_DIR / f"{product['product_id']}_video.mp4"
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
            print("\n❌ Cannot start ClickTok.")
            print("Please run setup manually: python setup.py")
            sys.exit(1)

    # Setup logging
    try:
        setup_logging()
    except Exception as e:
        # If logging setup fails, continue anyway
        print(f"Warning: Logging setup failed: {e}")

    # Launch appropriate interface
    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            if args.cli:
                launch_cli()
            else:
                launch_gui()
            break  # Success! Exit the retry loop

        except ImportError as e:
            retry_count += 1

            if retry_count <= max_retries:
                print("\n" + "=" * 70)
                print("  ⚠️  Import Error Detected - Auto-Fixing...")
                print("=" * 70)
                print(f"\nError: {e}")
                print("\n🔧 Attempting automatic repair...")
                print(f"Retry attempt {retry_count}/{max_retries}")
                print("\nReinstalling dependencies...\n")

                # Try to fix by reinstalling dependencies
                try:
                    setup_script = Path(__file__).parent / "setup.py"
                    result = subprocess.run([sys.executable, str(setup_script)])

                    if result.returncode == 0:
                        print("\n✅ Repair successful! Restarting ClickTok...\n")
                        # Clear any cached imports
                        if 'moviepy' in sys.modules:
                            del sys.modules['moviepy']
                        if 'moviepy.editor' in sys.modules:
                            del sys.modules['moviepy.editor']
                        continue  # Retry launch
                    else:
                        print("\n⚠️  Repair failed, trying again...")
                        continue

                except Exception as fix_error:
                    print(f"\n⚠️  Repair error: {fix_error}")
                    if retry_count < max_retries:
                        print("Retrying...")
                        continue
            else:
                # Max retries reached, show error
                print("\n" + "=" * 70)
                print("  ❌ Cannot Fix Automatically")
                print("=" * 70)
                print(f"\nError: {e}")
                print("\nAutomatic repair failed after multiple attempts.")
                print("\nManual intervention required:")
                print("  1. Close this window")
                print("  2. Open Command Prompt in ClickTok folder")
                print("  3. Run: python -m pip uninstall moviepy -y")
                print("  4. Run: python -m pip install moviepy")
                print("  5. Run: ClickTok.bat again")
                print("\nOr see PYTHON_313_FIX.txt for Python 3.13 issues")
                print("\n" + "=" * 70)
                sys.exit(1)

        except Exception as e:
            print("\n" + "=" * 70)
            print("  ❌ Unexpected Error")
            print("=" * 70)
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            print("\nPlease report this error with the above details.")
            sys.exit(1)


if __name__ == "__main__":
    main()
