FROM ubuntu:22.04

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    chromium-browser \
    chromium-chromedriver \
    wget \
    curl \
    gnupg \
    unzip \
    git \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome path
ENV CHROMEDRIVER_DIR=/usr/bin
ENV PATH=$CHROMEDRIVER_DIR:$PATH

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Run the bot
CMD ["python3", "bot.py"]
