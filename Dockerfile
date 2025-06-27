FROM python:3.11-slim

# Install system dependencies including Chrome and ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    postgresql-client \
    wget \
    gnupg \
    xvfb \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome repository and install Chrome + ChromeDriver
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        google-chrome-stable \
        chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links for chromedriver
RUN ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && chromedriver --version

# Set display environment variable for Xvfb
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh .

# Copy application code
COPY . .

# Set execute permissions for scripts
RUN chmod +x docker-entrypoint.sh wait-for-it.sh

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5000

# Run the application
CMD ["./docker-entrypoint.sh", "python", "run.py"] 