#!/bin/bash
# Startup script for Railway deployment

set -e  # Exit on error

echo "🚀 Starting ZenPDF deployment..."

# Set default PORT if not provided
PORT=${PORT:-5000}

# Initialize database on startup if not already done
echo "📦 Ensuring database is initialized..."
python init_db.py || echo "⚠️  Database initialization had warnings (this may be normal)"

# Start gunicorn with production settings
echo "🌐 Starting Gunicorn on port $PORT..."
exec gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - "app:create_app('production')"
