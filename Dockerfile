FROM python:3.11-slim-buster

WORKDIR /app

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libnss3 libfontconfig libatk-bridge2.0-0 libxkbcommon-x11-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm-dev libasound2 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose the dashboard port
EXPOSE 5000

# Command to run the main application (scheduler)
CMD ["python", "main.py"]
