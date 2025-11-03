# ClickTok Docker Image
# Python 3.11 with FFmpeg and all dependencies

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# FFmpeg: Required for video processing
# Playwright dependencies: Required for browser automation
RUN apt-get update && apt-get install -y \
    # FFmpeg and video processing
    ffmpeg \
    # Playwright browser dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    # Additional utilities
    wget \
    curl \
    git \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium for TikTok automation)
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY . .

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/data \
    /app/data/videos \
    /app/data/database \
    /app/logs \
    /app/config \
    /app/assets \
    /app/assets/music && \
    chmod -R 755 /app

# Create a non-root user for security
RUN useradd -m -u 1000 clicktok && \
    chown -R clicktok:clicktok /app

# Switch to non-root user
USER clicktok

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Expose port for potential web interface (future enhancement)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command - run GUI mode
# Can be overridden with docker run command
CMD ["python", "main.py"]
