#!/bin/bash
# Startup script for Railway deployment

# Set default PORT if not provided
PORT=${PORT:-5000}

# Start gunicorn with production settings
exec gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app('production')"
