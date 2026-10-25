FROM python:3.11-bullseye

WORKDIR /app

# Install system dependencies including Chrome
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-driver \
    build-essential \
    libssl-dev \
    libffi-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome paths
ENV CHROMEDRIVER_DIR=/usr/bin
ENV PATH=$CHROMEDRIVER_DIR:$PATH

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Run bot
CMD ["python3", "bot.py"]
