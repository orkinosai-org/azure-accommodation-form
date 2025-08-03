"""
Main FastAPI application entry point
"""

import os
import logging
import logging.config
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
from app.services.application_insights import get_insights_service

# Load environment variables
load_dotenv()

# Get settings and configure logging using .NET-style configuration
settings = get_settings()
logging_config = settings.get_logging_config()
logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Azure Accommodation Form application...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Application: {settings.application_settings.application_name}")
    logger.info(f"Application URL: {settings.application_settings.application_url}")
    
    # Initialize services
    
    # Initialize Application Insights
    insights_service = get_insights_service()
    insights_service.track_event("ApplicationStartup", {
        "environment": settings.environment,
        "application_name": settings.application_settings.application_name
    })
    
    # Test Azure Blob Storage connection if configured
    if settings.blob_storage_settings.connection_string:
        try:
            storage_service = AzureBlobStorageService()
            await storage_service.test_connection()
            logger.info("Azure Blob Storage connection verified")
            insights_service.track_event("StorageConnectionSuccess")
        except Exception as e:
            logger.warning(f"Azure Blob Storage connection failed: {e}")
            insights_service.track_exception(e, {"service": "blob_storage"})
    
    # Log Application Insights configuration
    if settings.application_insights.connection_string:
        logger.info("Application Insights configured")
    else:
        logger.info("Application Insights not configured")
    
    # Log email configuration
    if settings.email_settings.smtp_username:
        logger.info(f"Email service configured with SMTP server: {settings.email_settings.smtp_server}")
    else:
        logger.warning("Email service not fully configured")
    
    yield
    
    # Cleanup
    insights_service.track_event("ApplicationShutdown")
    insights_service.flush()
    logger.info("Shutting down Azure Accommodation Form application...")

# Create FastAPI application using settings from config
app_settings = settings.application_settings
app = FastAPI(
    title=app_settings.application_name,
    description="Secure web application for accommodation application processing",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    lifespan=lifespan
)

# Security middleware
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.allowed_hosts
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
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
    return {
        "status": "healthy", 
        "service": settings.application_settings.application_name,
        "version": "1.0.0",
        "environment": settings.environment
    }

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
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        ssl_keyfile=settings.ssl_keyfile,
        ssl_certfile=settings.ssl_certfile,
    )