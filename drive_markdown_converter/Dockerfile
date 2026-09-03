# Use lightweight modern Python runtime
FROM python:3.11-slim

# Install system dependencies for document and PDF rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy microservice application files
COPY . .

# Run continuous 24/7 daemon
CMD ["python", "main.py", "--daemon"]
