#!/bin/bash
# ClickTok Docker Setup Verification Script

set -e

echo "=========================================="
echo "  ClickTok Docker Setup Verification"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Test function
test_step() {
    echo -n "Testing: $1... "
}

pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}"
    if [ ! -z "$1" ]; then
        echo "  Error: $1"
    fi
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠ WARNING${NC}"
    if [ ! -z "$1" ]; then
        echo "  Warning: $1"
    fi
}

# Test 1: Docker installed
test_step "Docker installation"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    pass
    echo "  $DOCKER_VERSION"
else
    fail "Docker not found. Please install Docker Desktop."
fi

# Test 2: Docker running
test_step "Docker daemon running"
if docker info &> /dev/null; then
    pass
else
    fail "Docker daemon not running. Please start Docker Desktop."
fi

# Test 3: Docker Compose installed
test_step "Docker Compose installation"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    pass
    echo "  $COMPOSE_VERSION"
else
    fail "Docker Compose not found."
fi

# Test 4: Required files exist
echo ""
echo "Checking required files..."
test_step "Dockerfile"
[ -f "Dockerfile" ] && pass || fail "Dockerfile missing"

test_step "docker-compose.yml"
[ -f "docker-compose.yml" ] && pass || fail "docker-compose.yml missing"

test_step ".dockerignore"
[ -f ".dockerignore" ] && pass || fail ".dockerignore missing"

test_step "docker-entrypoint.sh"
[ -f "docker-entrypoint.sh" ] && pass || fail "docker-entrypoint.sh missing"

test_step "requirements.txt"
[ -f "requirements.txt" ] && pass || fail "requirements.txt missing"

test_step "main.py"
[ -f "main.py" ] && pass || fail "main.py missing"

# Test 5: Docker Compose config valid
echo ""
test_step "Docker Compose configuration"
if docker-compose config &> /dev/null; then
    pass
else
    fail "docker-compose.yml has errors"
fi

# Test 6: Build Docker image
echo ""
echo "Building Docker image (this may take a few minutes)..."
test_step "Docker image build"
if docker-compose build &> /tmp/docker-build.log; then
    pass
else
    fail "Build failed. Check /tmp/docker-build.log"
fi

# Test 7: Verify image exists
test_step "Docker image created"
if docker images | grep -q "clicktok"; then
    pass
else
    fail "Image not found in docker images"
fi

# Test 8: Test FFmpeg in container
echo ""
echo "Testing container dependencies..."
test_step "FFmpeg availability"
if docker-compose run --rm clicktok ffmpeg -version &> /dev/null; then
    pass
else
    fail "FFmpeg not available in container"
fi

# Test 9: Test Python in container
test_step "Python availability"
if docker-compose run --rm clicktok python --version &> /dev/null; then
    PYTHON_VERSION=$(docker-compose run --rm clicktok python --version 2>&1)
    pass
    echo "  $PYTHON_VERSION"
else
    fail "Python not available in container"
fi

# Test 10: Test Python dependencies
test_step "Python dependencies"
if docker-compose run --rm clicktok python -c "import moviepy, playwright, requests, bs4, PIL, numpy" &> /dev/null; then
    pass
else
    fail "Some Python dependencies missing"
fi

# Test 11: Check credentials setup
echo ""
test_step "Credentials configuration"
if [ -f "config/credentials.json" ]; then
    pass
else
    warn "config/credentials.json not found (OK for demo mode)"
fi

# Test 12: Check assets directory
test_step "Assets directory"
if [ -d "assets" ]; then
    pass
else
    warn "assets directory not found"
fi

# Summary
echo ""
echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "Failed: ${RED}$FAILED${NC}"
else
    echo -e "Failed: $FAILED"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Your Docker setup is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Start the application:"
    echo "     docker-compose up"
    echo ""
    echo "  2. Or use the quick-start script:"
    echo "     ./docker-start.sh"
    echo ""
    echo "  3. Read the documentation:"
    echo "     cat DOCKER_README.md"
    echo ""
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please fix the issues above before running ClickTok."
    echo "See DOCKER_README.md for troubleshooting."
    exit 1
fi

echo "=========================================="
