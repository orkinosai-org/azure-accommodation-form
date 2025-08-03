#!/bin/bash
# Setup script for Azure Accommodation Form Python Application

set -e  # Exit on any error

echo "🚀 Setting up Azure Accommodation Form Python Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "⚠️  Warning: Python $python_version detected. Python 3.11+ is recommended."
fi

echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Test FastAPI import
echo "🧪 Testing FastAPI installation..."
python -c "import fastapi; print('✅ FastAPI', fastapi.__version__, 'installed successfully')"

# Test all main imports
echo "🧪 Testing main application imports..."
python -c "
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import uvicorn
print('✅ All FastAPI imports successful!')
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Copy and configure environment: cp .env.example .env"
echo "  3. Edit .env with your configuration"
echo "  4. Start the application: python main.py"
echo ""
echo "For development with auto-reload:"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000 --reload"