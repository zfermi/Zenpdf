#!/bin/bash
# Startup script for Railway deployment

set -e  # Exit on error

echo "🚀 Starting ZenPDF deployment..."

# Set default PORT if not provided
PORT=${PORT:-5000}

# Debug: Show environment configuration (without sensitive data)
echo "📋 Environment Configuration:"
echo "  - FLASK_ENV: ${FLASK_ENV:-not set}"
echo "  - PORT: $PORT"
if [ -n "$DATABASE_URL" ]; then
    echo "  - DATABASE_URL: postgresql://***@${DATABASE_URL#*@}"
else
    echo "  - DATABASE_URL: not set (will use SQLite)"
fi
if [ -n "$SECRET_KEY" ]; then
    echo "  - SECRET_KEY: configured (${#SECRET_KEY} chars)"
else
    echo "  - SECRET_KEY: not set (using default - INSECURE!)"
fi

# Initialize database on startup if not already done
echo ""
echo "📦 Ensuring database is initialized..."
python init_db.py || echo "⚠️  Database initialization had warnings (this may be normal)"

# Start gunicorn with production settings
echo ""
echo "🌐 Starting Gunicorn on port $PORT..."
exec gunicorn -c gunicorn.conf.py "app:create_app('production')"
