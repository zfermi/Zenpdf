# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js (needed for Tailwind CSS)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy package files for Node.js dependencies
COPY package*.json ./

# Install Node.js dependencies (Tailwind CSS)
RUN npm install

# Copy Tailwind configuration and input CSS
COPY tailwind.config.js ./
COPY static/input.css ./static/

# Build Tailwind CSS
RUN npm run build:css

# Copy Python requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Railway will set PORT env var)
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Run the application
CMD ["python", "app.py"]
