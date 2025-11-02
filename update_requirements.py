"""
ClickTok - Requirements Manager
Automatically updates requirements.txt from installed packages

Usage:
    python update_requirements.py              # Update requirements.txt
    python update_requirements.py --check     # Check if requirements are up to date
    python update_requirements.py --install   # Install from requirements.txt then update
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


# Core packages that MUST be included with specific version constraints
REQUIRED_PACKAGES = {
    'moviepy': '>=1.0.3,<2.0.0',  # Must stay on 1.x
    'decorator': '>=4.4.2,<5.0.0',  # Required by moviepy 1.x
}

# Optional packages (will be included if installed)
OPTIONAL_PACKAGES = {
    'openai': '>=1.0.0',
    'anthropic': '>=0.7.0',
    'customtkinter': '>=5.2.0',
    'selenium': '>=4.15.0',
    'pyttsx3': '>=2.90',
    'gTTS': '>=2.4.0',
}

# Package categories for organized output
PACKAGE_CATEGORIES = {
    'Core Dependencies': [
        'requests', 'beautifulsoup4', 'lxml'
    ],
    'Video Processing': [
        'moviepy', 'Pillow', 'opencv-python', 'imageio', 'imageio-ffmpeg', 'numpy'
    ],
    'Browser Automation': [
        'playwright', 'selenium'
    ],
    'AI/NLP for Captions (Optional)': [
        'openai', 'anthropic'
    ],
    'GUI': [
        'customtkinter'
    ],
    'Utilities': [
        'python-dotenv', 'schedule', 'pandas', 'pyautogui', 'decorator', 'proglog', 'tqdm'
    ],
    'Text-to-Speech': [
        'pyttsx3', 'gTTS'
    ],
}


def get_installed_packages() -> Dict[str, str]:
    """Get all installed packages with versions"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
            capture_output=True,
            text=True,
            check=True
        )
        
        packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                packages[name.lower()] = {'name': name, 'version': version}
        
        return packages
    except Exception as e:
        print(f"Error getting installed packages: {e}")
        return {}


def get_package_info(package_name: str, installed_packages: Dict) -> Tuple[str, str]:
    """
    Get package name and version constraint
    
    Returns: (package_name, version_constraint)
    """
    pkg_lower = package_name.lower()
    
    if pkg_lower in installed_packages:
        installed_name = installed_packages[pkg_lower]['name']
        installed_version = installed_packages[pkg_lower]['version']
        
        # Check if we have a specific constraint for this package
        if package_name in REQUIRED_PACKAGES:
            constraint = REQUIRED_PACKAGES[package_name]
            return (installed_name, constraint)
        elif package_name in OPTIONAL_PACKAGES:
            # Use minimum version from optional, but allow any version >= that
            min_version = OPTIONAL_PACKAGES[package_name]
            return (installed_name, min_version)
        else:
            # Use >= installed version to allow updates
            return (installed_name, f">={installed_version}")
    
    # Package not installed
    if package_name in REQUIRED_PACKAGES:
        return (package_name, REQUIRED_PACKAGES[package_name])
    elif package_name in OPTIONAL_PACKAGES:
        return (package_name, OPTIONAL_PACKAGES[package_name])
    else:
        return None


def categorize_package(package_name: str) -> str:
    """Determine which category a package belongs to"""
    pkg_lower = package_name.lower()
    
    for category, packages in PACKAGE_CATEGORIES.items():
        if pkg_lower in [p.lower() for p in packages]:
            return category
    
    return 'Additional dependencies that might be needed'


def generate_requirements_content(installed_packages: Dict) -> str:
    """Generate the requirements.txt content"""
    lines = []
    categorized = {}
    
    # Organize packages by category
    all_packages = set()
    
    # Add required packages
    for pkg in REQUIRED_PACKAGES:
        all_packages.add(pkg)
    
    # Add optional packages (if installed)
    for pkg in OPTIONAL_PACKAGES:
        if pkg.lower() in installed_packages:
            all_packages.add(pkg)
    
    # Add all categorized packages
    for category, packages in PACKAGE_CATEGORIES.items():
        for pkg in packages:
            all_packages.add(pkg)
    
    # Categorize packages
    for pkg in sorted(all_packages, key=str.lower):
        category = categorize_package(pkg)
        if category not in categorized:
            categorized[category] = []
        
        pkg_info = get_package_info(pkg, installed_packages)
        if pkg_info:
            pkg_name, constraint = pkg_info
            # Check if package is actually installed (for optional packages)
            if pkg.lower() in installed_packages or pkg in REQUIRED_PACKAGES:
                categorized[category].append((pkg_name, constraint))
    
    # Generate output
    for category in PACKAGE_CATEGORIES.keys():
        if category in categorized and categorized[category]:
            lines.append(f"# {category}")
            for pkg_name, constraint in sorted(categorized[category]):
                comment = ""
                if pkg_name == "moviepy":
                    comment = "  # Pin to 1.x (2.x has different import structure)"
                elif pkg_name == "Pillow":
                    comment = "  # Flexible version for Python 3.13"
                elif pkg_name == "decorator":
                    comment = "  # moviepy 1.x requires decorator <5.0"
                
                lines.append(f"{pkg_name}{constraint}{comment}")
            lines.append("")
    
    # Add uncategorized packages if any
    if 'Additional dependencies that might be needed' in categorized:
        lines.append("# Additional dependencies that might be needed")
        for pkg_name, constraint in categorized['Additional dependencies that might be needed']:
            lines.append(f"{pkg_name}{constraint}")
    
    return '\n'.join(lines).strip()


def update_requirements_file(output_path: Path = None):
    """Update requirements.txt file"""
    if output_path is None:
        output_path = Path(__file__).parent / "requirements.txt"
    
    print("🔄 Updating requirements.txt...")
    print(f"   Reading installed packages...")
    
    installed_packages = get_installed_packages()
    
    if not installed_packages:
        print("❌ Error: Could not get installed packages list")
        return False
    
    print(f"   Found {len(installed_packages)} installed packages")
    
    content = generate_requirements_content(installed_packages)
    
    # Backup existing file
    if output_path.exists():
        backup_path = output_path.with_suffix('.txt.bak')
        output_path.rename(backup_path)
        print(f"   ✓ Backed up existing file to {backup_path.name}")
    
    # Write new file
    output_path.write_text(content)
    print(f"   ✓ Updated {output_path.name}")
    print(f"   ✓ File written successfully")
    
    return True


def check_requirements_status():
    """Check if requirements.txt matches installed packages"""
    print("🔍 Checking requirements.txt status...")
    
    installed_packages = get_installed_packages()
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    # Read requirements.txt
    requirements_content = requirements_file.read_text()
    
    # Extract package names from requirements.txt
    req_packages = set()
    for line in requirements_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            # Parse package name (handle >=, ==, etc.)
            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
            if match:
                req_packages.add(match.group(1).lower())
    
    # Check installed packages
    installed_names = set(pkg.lower() for pkg in installed_packages.keys())
    
    missing_from_req = installed_names - req_packages
    missing_from_install = req_packages - installed_names
    
    if not missing_from_req and not missing_from_install:
        print("✅ requirements.txt is up to date!")
        return True
    else:
        print("\n⚠️  requirements.txt needs updating:")
        if missing_from_req:
            print(f"   Missing from requirements.txt ({len(missing_from_req)}):")
            for pkg in sorted(missing_from_req)[:10]:
                print(f"     - {pkg}")
            if len(missing_from_req) > 10:
                print(f"     ... and {len(missing_from_req) - 10} more")
        
        if missing_from_install:
            print(f"   In requirements.txt but not installed ({len(missing_from_install)}):")
            for pkg in sorted(missing_from_install)[:10]:
                print(f"     - {pkg}")
            if len(missing_from_install) > 10:
                print(f"     ... and {len(missing_from_install) - 10} more")
        
        print("\n💡 Run 'python update_requirements.py' to update")
        return False


def install_and_sync():
    """Install packages from requirements.txt then sync"""
    print("📦 Installing packages from requirements.txt...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            check=True
        )
        print("✅ Packages installed successfully")
        
        # Now update requirements.txt
        return update_requirements_file()
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Update ClickTok requirements.txt automatically'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if requirements.txt is up to date'
    )
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install from requirements.txt then update it'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: requirements.txt)'
    )
    
    args = parser.parse_args()
    
    if args.check:
        check_requirements_status()
    elif args.install:
        install_and_sync()
    else:
        output_path = Path(args.output) if args.output else None
        update_requirements_file(output_path)
        print("\n✅ Done! requirements.txt has been updated.")
        print("\n💡 Tip: Run 'python update_requirements.py --check' to verify")


if __name__ == "__main__":
    main()

