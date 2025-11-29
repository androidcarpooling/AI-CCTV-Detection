FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads results watchlist_photos

# Download InsightFace models (buffalo_l)
RUN python -c "import requests; requests.packages.urllib3.disable_warnings(); r = requests.get('https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip', verify=False, timeout=300); open('/tmp/buffalo_l.zip', 'wb').write(r.content)" && \
    mkdir -p ~/.insightface/models/buffalo_l && \
    cd ~/.insightface/models/buffalo_l && \
    unzip -q /tmp/buffalo_l.zip && \
    rm /tmp/buffalo_l.zip

# Expose port (Railway will set PORT env var)
EXPOSE ${PORT:-5000}

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web_app.py

# Run the application
CMD ["python", "web_app.py"]

