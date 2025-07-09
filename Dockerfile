# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Chromium (for Selenium)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports for Flask API and Streamlit
EXPOSE 5000 8501

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting Product Price Comparison Tool..."\n\
echo "Available options:"\n\
echo "1. Flask API: python main.py serve"\n\
echo "2. Streamlit UI: streamlit run streamlit_app.py"\n\
echo "3. CLI: python main.py"\n\
echo ""\n\
echo "Starting Flask API on port 5000..."\n\
python main.py serve\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["/app/start.sh"] 