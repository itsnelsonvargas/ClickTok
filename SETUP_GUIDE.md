# ClickTok - Setup & Requirements Management Guide

This guide explains how to easily install ClickTok and keep requirements.txt automatically updated.

---

## 🚀 Quick Setup (Easiest Method)

### Option 1: Smart Installation Script (Recommended)

```bash
python install_and_setup.py
```

This script automatically:
- ✅ Checks Python version
- ✅ Upgrades pip
- ✅ Installs all packages from `requirements.txt`
- ✅ Installs Playwright browsers
- ✅ Creates all necessary directories
- ✅ Creates default `credentials.json`
- ✅ Verifies installation

**With automatic requirements sync:**
```bash
python install_and_setup.py --sync
```
This also syncs `requirements.txt` with installed packages after installation.

---

### Option 2: Original Setup Script

```bash
python setup.py
```

Or use batch files:
- **Windows**: `setup.bat` or `ClickTok.bat`
- **macOS/Linux**: `./setup.sh`

---

## 📦 Keeping Requirements Updated

### Automatic Requirements Management

Whenever you install a new package or the environment changes, update `requirements.txt` automatically:

```bash
python update_requirements.py
```

This script:
- ✅ Reads all currently installed packages
- ✅ Generates an organized `requirements.txt`
- ✅ Maintains version constraints for critical packages (like moviepy)
- ✅ Preserves important comments
- ✅ Backs up existing file

---

### Usage Options

**Update requirements.txt:**
```bash
python update_requirements.py
```

**Check if requirements.txt is up to date:**
```bash
python update_requirements.py --check
```

**Install from requirements.txt then update it:**
```bash
python update_requirements.py --install
```

**Check installation status:**
```bash
python install_and_setup.py --check
```

---

## 🔄 Workflow: Installing New Packages

### Recommended Workflow

1. **Install the package:**
   ```bash
   pip install package-name
   ```

2. **Update requirements.txt automatically:**
   ```bash
   python update_requirements.py
   ```

3. **Verify it was added:**
   ```bash
   python update_requirements.py --check
   ```

### Example

```bash
# Install a new package
pip install some-new-package

# Update requirements.txt to include it
python update_requirements.py

# Verify requirements.txt is up to date
python update_requirements.py --check
```

---

## 📋 How It Works

### `update_requirements.py`

This script:
- Scans your current Python environment
- Reads all installed packages and versions
- Organizes them into categories (Core, Video Processing, Browser Automation, etc.)
- Applies version constraints for critical packages:
  - `moviepy>=1.0.3,<2.0.0` (must stay on 1.x)
  - `decorator>=4.4.2,<5.0.0` (required by moviepy)
- Generates a clean, organized `requirements.txt`
- Backs up the old file as `requirements.txt.bak`

**Features:**
- ✅ Maintains version constraints for critical packages
- ✅ Organizes packages by category
- ✅ Preserves important comments
- ✅ Handles optional packages gracefully
- ✅ Safe (backs up existing file)

---

### `install_and_setup.py`

This script provides a smarter installation experience:
- Checks prerequisites
- Installs all dependencies
- Creates necessary directories
- Sets up default configuration files
- Verifies installation
- Optional: Syncs requirements.txt after installation

**Features:**
- ✅ One-command setup
- ✅ Better error handling
- ✅ Progress indicators
- ✅ Verification at end
- ✅ Helpful next steps

---

## 🔍 Verification

### Check Installation Status

```bash
python install_and_setup.py --check
```

This shows:
- Python version
- Installed packages status
- Required files presence
- Directory structure

### Check Requirements Status

```bash
python update_requirements.py --check
```

This shows:
- If `requirements.txt` matches installed packages
- Missing packages
- Extra packages

---

## 📝 Manual Requirements Management

If you prefer to manage `requirements.txt` manually:

### Generate from Current Environment

```bash
pip freeze > requirements_current.txt
```

**Note**: `pip freeze` includes ALL packages, even system packages. The `update_requirements.py` script is smarter - it only includes ClickTok-related packages.

### Install from Requirements

```bash
pip install -r requirements.txt
```

### Update Specific Package

```bash
pip install --upgrade package-name
python update_requirements.py  # Sync requirements.txt
```

---

## ⚙️ Configuration

### Critical Package Constraints

The following packages have version constraints that are maintained by `update_requirements.py`:

```python
REQUIRED_PACKAGES = {
    'moviepy': '>=1.0.3,<2.0.0',     # Must stay on 1.x
    'decorator': '>=4.4.2,<5.0.0',   # Required by moviepy 1.x
}
```

These constraints are preserved even when auto-updating.

---

## 🐛 Troubleshooting

### Requirements.txt Out of Sync

```bash
# Check what's different
python update_requirements.py --check

# Fix it automatically
python update_requirements.py
```

### Installation Failed

```bash
# Check status
python install_and_setup.py --check

# Try installing again
python install_and_setup.py
```

### Missing Packages After Update

```bash
# Reinstall from requirements.txt
pip install -r requirements.txt --upgrade

# Then sync
python update_requirements.py
```

---

## 📚 File Structure

```
ClickTok/
├── requirements.txt              # Main requirements file (auto-updated)
├── requirements-minimal.txt      # Minimal version (backup)
├── update_requirements.py        # Auto-update script
├── install_and_setup.py          # Smart installation script
├── setup.py                      # Original setup script
└── SETUP_GUIDE.md                # This file
```

---

## 💡 Best Practices

1. **Always update requirements.txt after installing packages:**
   ```bash
   pip install new-package
   python update_requirements.py
   ```

2. **Commit requirements.txt to version control:**
   - Keeps the project's dependencies tracked
   - Others can reproduce your environment

3. **Use virtual environments:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

4. **Regular verification:**
   ```bash
   python install_and_setup.py --check
   ```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Full setup | `python install_and_setup.py` |
| Update requirements | `python update_requirements.py` |
| Check status | `python install_and_setup.py --check` |
| Verify requirements | `python update_requirements.py --check` |
| Install & sync | `python install_and_setup.py --sync` |

---

**Remember**: Always run `python update_requirements.py` after installing new packages to keep `requirements.txt` in sync!

