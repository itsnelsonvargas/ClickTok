"""
ClickTok - Smart Installation & Setup Script
Automatically installs dependencies and syncs requirements.txt

Usage:
    python install_and_setup.py           # Full installation
    python install_and_setup.py --sync    # Install then sync requirements
    python install_and_setup.py --check   # Check installation status
"""

import subprocess
import sys
from pathlib import Path
import argparse
import json


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step, total, description):
    """Print step information"""
    print(f"[{step}/{total}] {description}")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def upgrade_pip():
    """Upgrade pip to latest version"""
    print("\n→ Upgrading pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        print("  ✅ pip upgraded")
        return True
    except Exception as e:
        print(f"  ⚠️  Could not upgrade pip: {e}")
        return False


def install_from_requirements():
    """Install packages from requirements.txt"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        print("   Creating initial requirements.txt...")
        
        # Create basic requirements.txt
        create_initial_requirements(requirements_file)
    
    print("\n→ Installing packages from requirements.txt...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
            text=True
        )
        print("  ✅ All packages installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Installation failed: {e}")
        print("\n💡 Tip: Some packages may have failed. Check output above.")
        return False


def create_initial_requirements(file_path: Path):
    """Create initial requirements.txt if it doesn't exist"""
    initial_content = """# Core Dependencies
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Video Processing - using flexible versions for Python 3.13 compatibility
moviepy>=1.0.3,<2.0.0  # Pin to 1.x (2.x has different import structure)
Pillow>=10.0.0  # Flexible version for Python 3.13
opencv-python>=4.8.0

# Text-to-Speech
pyttsx3>=2.90
gTTS>=2.4.0

# Browser Automation
playwright>=1.40.0
selenium>=4.15.0

# AI/NLP for Captions (Optional)
openai>=1.0.0
anthropic>=0.7.0

# GUI
customtkinter>=5.2.0

# Utilities
python-dotenv>=1.0.0
schedule>=1.2.0
pandas>=2.0.0
pyautogui>=0.9.54

# Image Processing
imageio>=2.33.0
imageio-ffmpeg>=0.4.9

# Additional dependencies that might be needed
numpy>=1.24.0
decorator>=4.4.2,<5.0.0  # moviepy 1.x requires decorator <5.0
proglog>=0.1.10
tqdm>=4.66.0
"""
    file_path.write_text(initial_content)
    print(f"  ✅ Created {file_path.name}")


def install_playwright_browsers():
    """Install Playwright browsers"""
    print("\n→ Installing Playwright browsers...")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True
        )
        print("  ✅ Playwright browsers installed")
        return True
    except Exception as e:
        print(f"  ⚠️  Playwright installation failed: {e}")
        print("  💡 You can install manually: python -m playwright install chromium")
        return False


def sync_requirements():
    """Sync requirements.txt with installed packages"""
    print("\n→ Syncing requirements.txt with installed packages...")
    try:
        # Import and run the update script
        update_script = Path(__file__).parent / "update_requirements.py"
        if update_script.exists():
            result = subprocess.run(
                [sys.executable, str(update_script)],
                check=True,
                text=True
            )
            print("  ✅ requirements.txt synced")
            return True
        else:
            print("  ⚠️  update_requirements.py not found")
            return False
    except Exception as e:
        print(f"  ⚠️  Sync failed: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n→ Creating directories...")
    directories = [
        "data",
        "data/products",
        "data/videos",
        "assets",
        "assets/music",
        "assets/fonts",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("  ✅ Directories created")
    return True


def create_default_credentials():
    """Create default credentials.json if it doesn't exist"""
    cred_file = Path("config/credentials.json")
    example_file = Path("config/credentials.json.example")
    
    if not cred_file.exists():
        if example_file.exists():
            import shutil
            shutil.copy(example_file, cred_file)
            print("  ✅ Created credentials.json from template")
        else:
            # Create empty credentials
            cred_file.parent.mkdir(parents=True, exist_ok=True)
            cred_file.write_text(json.dumps({
                "tiktok": {
                    "username": "",
                    "password": "",
                    "cookies_file": "data/tiktok_cookies.json"
                },
                "openai_api_key": "",
                "anthropic_api_key": "",
                "tiktok_shop_api": {
                    "app_key": "",
                    "app_secret": "",
                    "access_token": ""
                }
            }, indent=2))
            print("  ✅ Created empty credentials.json")
    return True


def verify_installation():
    """Verify key packages are installed"""
    print("\n→ Verifying installation...")
    
    key_packages = {
        'moviepy': 'MoviePy',
        'playwright': 'Playwright',
        'PIL': 'Pillow',
        'requests': 'Requests',
        'tkinter': 'Tkinter'
    }
    
    all_ok = True
    for module, name in key_packages.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def check_installation_status():
    """Check current installation status"""
    print_header("Installation Status Check")
    
    # Check Python
    print("Python:", end=" ")
    if check_python_version():
        pass
    else:
        print("❌ Please upgrade Python")
        return
    
    # Check key packages
    print("\nKey Packages:")
    verify_installation()
    
    # Check files
    print("\nFiles:")
    files_to_check = [
        ("requirements.txt", Path("requirements.txt")),
        ("credentials.json", Path("config/credentials.json")),
        ("settings.py", Path("config/settings.py")),
    ]
    
    for name, path in files_to_check:
        if path.exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} - MISSING")
    
    # Check directories
    print("\nDirectories:")
    dirs_to_check = [
        "data", "data/products", "data/videos",
        "assets", "assets/music", "logs"
    ]
    
    for dir_name in dirs_to_check:
        if Path(dir_name).exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ - MISSING")


def main():
    parser = argparse.ArgumentParser(
        description='ClickTok Smart Installation & Setup'
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Sync requirements.txt after installation'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check installation status only'
    )
    parser.add_argument(
        '--skip-browsers',
        action='store_true',
        help='Skip Playwright browser installation'
    )
    
    args = parser.parse_args()
    
    if args.check:
        check_installation_status()
        return
    
    print_header("ClickTok - Smart Installation & Setup")
    
    print("This script will:")
    print("  • Check Python version")
    print("  • Upgrade pip")
    print("  • Install all packages from requirements.txt")
    if not args.skip_browsers:
        print("  • Install Playwright browsers")
    print("  • Create necessary directories")
    print("  • Create default credentials file")
    if args.sync:
        print("  • Sync requirements.txt with installed packages")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("\nInstallation cancelled.")
        return
    
    total_steps = 5
    step = 0
    
    # Step 1: Check Python
    step += 1
    print_step(step, total_steps, "Checking Python version")
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.8+ required")
        sys.exit(1)
    
    # Step 2: Upgrade pip
    step += 1
    print_step(step, total_steps, "Upgrading pip")
    upgrade_pip()
    
    # Step 3: Install packages
    step += 1
    print_step(step, total_steps, "Installing packages")
    if not install_from_requirements():
        print("\n⚠️  Some packages may have failed to install")
        print("   Continuing with setup...")
    
    # Step 4: Install Playwright
    if not args.skip_browsers:
        step += 1
        print_step(step, total_steps, "Installing Playwright browsers")
        install_playwright_browsers()
    
    # Step 5: Create directories
    step += 1
    print_step(step, total_steps, "Creating directories")
    create_directories()
    create_default_credentials()
    
    # Step 6: Sync requirements (if requested)
    if args.sync:
        print("\n→ Syncing requirements.txt...")
        sync_requirements()
    
    # Final verification
    print("\n" + "=" * 70)
    print("  ✅ Installation Complete!")
    print("=" * 70)
    
    print("\n📋 Next Steps:")
    print("  1. Edit config/credentials.json with your TikTok credentials")
    print("  2. Add logo to assets/logo.png (optional)")
    print("  3. Add music to assets/music/*.mp3 (optional)")
    print("  4. Run: python main.py")
    
    print("\n💡 Tips:")
    print("  • Run 'python update_requirements.py' after installing new packages")
    print("  • Run 'python install_and_setup.py --check' to verify installation")
    
    # Verify
    print("\n→ Final verification...")
    verify_installation()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

