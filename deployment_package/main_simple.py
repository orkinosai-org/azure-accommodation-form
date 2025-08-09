"""
Simplified main application for testing
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Azure Accommodation Form",
    description="Secure web application for accommodation application processing",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified for testing
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Static files and templates
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    templates = Jinja2Templates(directory="app/templates")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")
    templates = None

@app.get("/")
async def root(request: Request):
    """Main landing page"""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Root page accessed from IP: {client_ip}")
    
    if templates:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "client_ip": client_ip}
        )
    else:
        return {
            "message": "Azure Accommodation Form",
            "status": "running",
            "client_ip": client_ip
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for Azure App Service"""
    return {"status": "healthy", "service": "azure-accommodation-form"}

@app.post("/api/auth/verify-certificate")
async def verify_certificate_simple(request: Request):
    """Simplified certificate verification"""
    return {
        "status": "verified",
        "message": "Certificate authentication successful (development mode)",
        "client_ip": request.client.host if request.client else "unknown"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development",
    )