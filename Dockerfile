FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     libpq-dev     curl     postgresql-client     && rm -rf /var/lib/apt/lists/*

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
CMD ["python", "run.py"] 