@echo off
REM Setup script for Azure Accommodation Form Python Application (Windows)

echo 🚀 Setting up Azure Accommodation Form Python Application...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Test FastAPI import
echo 🧪 Testing FastAPI installation...
python -c "import fastapi; print('✅ FastAPI', fastapi.__version__, 'installed successfully')"

REM Test all main imports
echo 🧪 Testing main application imports...
python -c "from fastapi import FastAPI, Request, HTTPException; from fastapi.staticfiles import StaticFiles; from fastapi.templating import Jinja2Templates; from dotenv import load_dotenv; import uvicorn; print('✅ All FastAPI imports successful!')"

echo.
echo 🎉 Setup completed successfully!
echo.
echo To run the application:
echo   1. Activate the virtual environment: venv\Scripts\activate
echo   2. Copy and configure environment: copy .env.example .env
echo   3. Edit .env with your configuration
echo   4. Start the application: python main.py
echo.
echo For development with auto-reload:
echo   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo.
pause