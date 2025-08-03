"""
Main FastAPI application entry point
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from dotenv import load_dotenv
import uvicorn

from app.api.routes import auth, form, admin
from app.core.config import get_settings
from app.core.security import get_current_ip
from app.services.storage import AzureBlobStorageService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Azure Accommodation Form application...")
    
    # Initialize services
    settings = get_settings()
    
    # Test Azure Blob Storage connection if configured
    if settings.azure_storage_connection_string:
        try:
            storage_service = AzureBlobStorageService()
            await storage_service.test_connection()
            logger.info("Azure Blob Storage connection verified")
        except Exception as e:
            logger.warning(f"Azure Blob Storage connection failed: {e}")
    
    yield
    
    logger.info("Shutting down Azure Accommodation Form application...")

# Create FastAPI application
app = FastAPI(
    title="Azure Accommodation Form",
    description="Secure web application for accommodation application processing",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
    lifespan=lifespan
)

# Security middleware
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(form.router, prefix="/api/form", tags=["form"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root(request: Request):
    """Main landing page"""
    client_ip = get_current_ip(request)
    logger.info(f"Root page accessed from IP: {client_ip}")
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "client_ip": client_ip}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for Azure App Service"""
    return {"status": "healthy", "service": "azure-accommodation-form"}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return templates.TemplateResponse(
        "500.html",
        {"request": request},
        status_code=500
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development",
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE"),
    )