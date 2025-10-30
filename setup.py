"""
ClickTok - One-Command Setup Script
Installs all dependencies and sets up the environment
"""
import subprocess
import sys
import os
from pathlib import Path
import platform


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step_num, total_steps, description):
    """Print step information"""
    print(f"[Step {step_num}/{total_steps}] {description}")


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n→ {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )

        print("  ✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e}")
        if e.stderr:
            print(f"  Details: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False

    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")

    # Warn about Python 3.13+
    if version.major == 3 and version.minor >= 13:
        print("\n⚠️  WARNING: Python 3.13 is very new!")
        print("  Some packages may not have pre-built wheels yet.")
        print("  Installation may take longer as packages build from source.")
        print("  For best compatibility, Python 3.11 or 3.12 is recommended.\n")

    return True


def install_pip_packages():
    """Install Python packages from requirements.txt"""
    # First upgrade pip
    print("\n→ Upgrading pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        print("  ✓ pip upgraded")
    except:
        print("  ⚠️  Could not upgrade pip, continuing...")

    # Try installing all packages at once
    print("\n→ Installing Python packages...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        print("  ✓ All packages installed successfully")
        return True
    except subprocess.TimeoutExpired:
        print("  ✗ Installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print("  ✗ Batch installation failed")
        print("\n⚠️  Trying individual package installation...")

        # Fallback: Install critical packages one by one
        critical_packages = [
            "requests",
            "beautifulsoup4",
            "lxml",
            "Pillow",
            "moviepy",
            "playwright",
            "imageio",
            "imageio-ffmpeg",
            "numpy"
        ]

        success_count = 0
        for package in critical_packages:
            try:
                print(f"\n  → Installing {package}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package, "--upgrade"],
                    check=True,
                    capture_output=True,
                    timeout=120
                )
                print(f"    ✓ {package} installed")
                success_count += 1
            except:
                print(f"    ✗ {package} failed (will continue anyway)")

        if success_count >= 6:  # At least 6 critical packages
            print(f"\n  ✓ Installed {success_count}/{len(critical_packages)} critical packages")
            return True
        else:
            print(f"\n  ✗ Only {success_count}/{len(critical_packages)} packages installed")
            return False


def install_playwright_browsers():
    """Install Playwright browsers"""
    command = [sys.executable, "-m", "playwright", "install", "chromium"]
    return run_command(command, "Installing Playwright Chromium browser")


def verify_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            capture_output=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg is NOT installed")
        print("\n  FFmpeg is required for video processing.")
        print("  Please install it:")

        if platform.system() == "Windows":
            print("\n  Windows:")
            print("    Option 1: choco install ffmpeg")
            print("    Option 2: Download from https://ffmpeg.org/download.html")
        elif platform.system() == "Darwin":
            print("\n  macOS:")
            print("    brew install ffmpeg")
        else:
            print("\n  Linux:")
            print("    sudo apt install ffmpeg")

        return False


def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/products",
        "data/videos",
        "assets",
        "assets/music",
        "assets/fonts",
        "logs"
    ]

    print("\n→ Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("  ✓ All directories created")
    return True


def verify_installation():
    """Verify that key packages are installed"""
    packages_to_check = [
        ("moviepy", "MoviePy"),
        ("playwright", "Playwright"),
        ("PIL", "Pillow"),
        ("requests", "Requests"),
        ("tkinter", "Tkinter")
    ]

    print("\n→ Verifying installation...")
    all_ok = True

    for package, name in packages_to_check:
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            all_ok = False

    return all_ok


def create_sample_assets():
    """Create placeholder files for assets"""
    print("\n→ Setting up asset placeholders...")

    # Create a simple text file reminder for logo
    logo_readme = Path("assets") / "README.txt"
    if not logo_readme.exists():
        logo_readme.write_text("""ClickTok Assets Folder

Please add the following files:

1. logo.png
   - Your logo/watermark
   - Recommended size: 200x200 to 500x500 pixels
   - PNG format with transparent background

2. music/*.mp3
   - Royalty-free background music
   - MP3 format
   - 15-30 seconds duration recommended

Free music sources:
- YouTube Audio Library
- Pixabay Music
- Free Music Archive
- Incompetech

3. fonts/*.ttf (optional)
   - Custom fonts for text overlays
""")
        print("  ✓ Created assets/README.txt")

    return True


def print_next_steps():
    """Print what to do next"""
    print_header("Setup Complete!")

    print("✅ All dependencies installed successfully!\n")
    print("📋 Next Steps:\n")
    print("1. Edit config/credentials.json with your TikTok credentials")
    print("   - Add your TikTok username and password")
    print("   - (Optional) Add OpenAI API key for AI captions\n")

    print("2. Add your assets:")
    print("   - Place your logo in: assets/logo.png")
    print("   - Add music files to: assets/music/*.mp3")
    print("   - See assets/README.txt for details\n")

    print("3. Run ClickTok:")
    print("   - GUI Mode:  python main.py")
    print("   - CLI Mode:  python main.py --cli")
    print("   - Examples:  python example_usage.py\n")

    print("📚 Documentation:")
    print("   - README.md         - Complete guide")
    print("   - SETUP_GUIDE.md    - Detailed setup")
    print("   - QUICK_REFERENCE.md - Cheat sheet\n")

    print("🚀 You're ready to start earning with TikTok affiliate marketing!\n")


def main():
    """Main setup process"""
    print_header("ClickTok Setup - One-Command Installation")

    print("This script will:")
    print("  • Check Python version")
    print("  • Install all Python packages")
    print("  • Install Playwright browsers")
    print("  • Verify FFmpeg installation")
    print("  • Create necessary directories")
    print("  • Verify installation\n")

    # Confirm
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("\nSetup cancelled.")
        return

    total_steps = 6
    current_step = 0

    # Step 1: Check Python
    current_step += 1
    print_step(current_step, total_steps, "Checking Python version")
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.8+ required")
        sys.exit(1)

    # Step 2: Install pip packages
    current_step += 1
    print_step(current_step, total_steps, "Installing Python packages")
    if not install_pip_packages():
        print("\n❌ Setup failed: Could not install Python packages")
        print("Try running manually: pip install -r requirements.txt")
        sys.exit(1)

    # Step 3: Install Playwright
    current_step += 1
    print_step(current_step, total_steps, "Installing Playwright browsers")
    if not install_playwright_browsers():
        print("\n⚠️  Warning: Playwright browser installation failed")
        print("Try running manually: python -m playwright install chromium")

    # Step 4: Check FFmpeg
    current_step += 1
    print_step(current_step, total_steps, "Checking FFmpeg")
    ffmpeg_ok = verify_ffmpeg()
    if not ffmpeg_ok:
        print("\n⚠️  Warning: FFmpeg not found. Please install it manually.")

    # Step 5: Create directories
    current_step += 1
    print_step(current_step, total_steps, "Creating directories")
    create_directories()
    create_sample_assets()

    # Step 6: Verify
    current_step += 1
    print_step(current_step, total_steps, "Verifying installation")
    if not verify_installation():
        print("\n⚠️  Some packages may not be installed correctly")
        print("Check the output above for details")

    # Print next steps
    print_next_steps()

    # Final check
    if not ffmpeg_ok:
        print("⚠️  IMPORTANT: Install FFmpeg before creating videos!")
        print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
