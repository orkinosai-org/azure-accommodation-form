#!/bin/bash

# Azure Web App startup script for Python FastAPI application
echo "Starting Azure Accommodation Form FastAPI application..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Navigate to the application directory
cd /home/site/wwwroot

# Install dependencies if needed
pip install -r requirements.txt

# Start the FastAPI application with Gunicorn
echo "Starting Gunicorn server..."
gunicorn main:app \
    --bind=0.0.0.0:8000 \
    --workers=4 \
    --worker-class=uvicorn.workers.UvicornWorker \
    --timeout=120 \
    --keep-alive=2 \
    --max-requests=1000 \
    --max-requests-jitter=50 \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=-