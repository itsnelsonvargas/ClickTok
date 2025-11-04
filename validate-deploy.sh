#!/bin/bash
# Deployment Validation Script
# Run this before deploying to another computer

set -e

echo "=========================================="
echo "  ClickTok Deployment Validation"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✓ PASS${NC} - $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC} - $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARNING${NC} - $1"
    ((WARNINGS++))
}

echo "Checking deployment readiness..."
echo ""

# Check 1: Required files exist
echo "=== Checking Required Files ==="
FILES=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    "docker-entrypoint.sh"
    "requirements.txt"
    "main.py"
    "env.example"
    "config/credentials.json.example"
    "README.md"
    "DOCKER_README.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file missing"
    fi
done
echo ""

# Check 2: Sensitive files NOT present (should use examples)
echo "=== Checking for Sensitive Files ==="
if [ -f ".env" ] && grep -q "YOUR_" .env; then
    check_pass ".env has placeholder values"
elif [ -f ".env" ]; then
    check_warn ".env exists with real values (exclude from deployment)"
fi

if [ -f "config/credentials.json" ]; then
    if grep -q "YOUR_" config/credentials.json; then
        check_pass "credentials.json has placeholder values"
    else
        check_warn "credentials.json may contain real credentials (exclude from deployment)"
    fi
fi
echo ""

# Check 3: Git repository status
echo "=== Checking Git Status ==="
if [ -d ".git" ]; then
    # Check for uncommitted changes
    if [ -z "$(git status --porcelain)" ]; then
        check_pass "No uncommitted changes"
    else
        check_warn "Uncommitted changes exist"
        git status --short
    fi

    # Check if .env and credentials are in gitignore
    if git check-ignore .env > /dev/null 2>&1; then
        check_pass ".env is git-ignored"
    else
        check_warn ".env not in .gitignore"
    fi

    if git check-ignore config/credentials.json > /dev/null 2>&1; then
        check_pass "credentials.json is git-ignored"
    else
        check_warn "credentials.json not in .gitignore"
    fi
else
    check_warn "Not a git repository"
fi
echo ""

# Check 4: Docker configuration
echo "=== Checking Docker Configuration ==="
if command -v docker &> /dev/null; then
    check_pass "Docker is available"

    if docker info &> /dev/null; then
        check_pass "Docker daemon is running"
    else
        check_warn "Docker daemon not running"
    fi
else
    check_warn "Docker not installed (needed for testing)"
fi

if command -v docker-compose &> /dev/null; then
    check_pass "Docker Compose is available"
else
    check_warn "Docker Compose not installed (needed for testing)"
fi
echo ""

# Check 5: Dockerfile validation
echo "=== Validating Dockerfile ==="
if grep -q "FROM python:3.11" Dockerfile; then
    check_pass "Python 3.11 base image"
else
    check_warn "Python version may differ"
fi

if grep -q "ffmpeg" Dockerfile; then
    check_pass "FFmpeg included in Dockerfile"
else
    check_fail "FFmpeg not found in Dockerfile"
fi

if grep -q "playwright" Dockerfile; then
    check_pass "Playwright included"
else
    check_warn "Playwright may not be configured"
fi
echo ""

# Check 6: No hardcoded paths
echo "=== Checking for Hardcoded Paths ==="
HARDCODED_PATHS=$(grep -r "C:\\Users\|/Users/\|/home/" --include="*.py" --include="*.sh" --exclude-dir=".git" . 2>/dev/null | grep -v "Binary file" | grep -v ".md:" || true)

if [ -z "$HARDCODED_PATHS" ]; then
    check_pass "No hardcoded paths found in code"
else
    check_warn "Potential hardcoded paths found:"
    echo "$HARDCODED_PATHS" | head -5
fi
echo ""

# Check 7: Scripts are executable
echo "=== Checking Script Permissions ==="
SCRIPTS=(
    "docker-start.sh"
    "docker-test.sh"
    "docker-entrypoint.sh"
    "validate-deploy.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_pass "$script is executable"
        else
            check_warn "$script not executable (run: chmod +x $script)"
        fi
    fi
done
echo ""

# Check 8: Documentation completeness
echo "=== Checking Documentation ==="
DOCS=(
    "README.md"
    "DOCKER_README.md"
    "DOCKER_QUICKSTART.md"
    "DEPLOY_ANYWHERE.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ] && [ -s "$doc" ]; then
        check_pass "$doc exists and not empty"
    else
        check_warn "$doc missing or empty"
    fi
done
echo ""

# Check 9: Test build (optional but recommended)
echo "=== Testing Docker Build (Optional) ==="
read -p "Do you want to test Docker build? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Building Docker image..."
    if docker-compose build --quiet 2>&1 | grep -q "error"; then
        check_fail "Docker build failed"
    else
        check_pass "Docker build successful"
    fi
else
    echo "Skipping Docker build test"
fi
echo ""

# Summary
echo "=========================================="
echo "  Validation Summary"
echo "=========================================="
echo -e "Passed:   ${GREEN}$PASSED${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "Failed:   ${RED}$FAILED${NC}"
fi
echo ""

# Final verdict
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ READY FOR DEPLOYMENT${NC}"
    echo ""
    echo "Your ClickTok project is ready to deploy!"
    echo ""
    echo "Deployment options:"
    echo "  1. Git clone: git push && (on target) git clone <repo>"
    echo "  2. Folder copy: Copy entire ClickTok folder to target"
    echo "  3. Docker image: docker save clicktok:latest | gzip > clicktok.tar.gz"
    echo ""
    echo "On target computer:"
    echo "  1. Install Docker Desktop"
    echo "  2. Run: docker-compose up --build"
    echo ""
    exit 0
else
    echo -e "${RED}✗ NOT READY FOR DEPLOYMENT${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
    echo ""
    exit 1
fi
