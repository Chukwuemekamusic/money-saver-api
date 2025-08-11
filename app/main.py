from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api.routes import auth_router, savings_router, email_router
from app.services.scheduler_service import scheduler_service

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler_service.start()
    yield
    # Shutdown
    scheduler_service.shutdown()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI backend for Money Saver App with Supabase Auth and Email Reminders",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(savings_router, prefix=f"{settings.API_V1_STR}/savings")
app.include_router(email_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Money Saver API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    try:
        # Basic health check
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "environment": "development" if settings.DEBUG else "production",
            "supabase": {
                "configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY),
                "url": settings.SUPABASE_URL if settings.SUPABASE_URL else "not configured"
            }
        }
        
        # Test Supabase connection
        try:
            from app.core.supabase import get_supabase_client
            supabase = get_supabase_client()
            health_data["supabase"]["status"] = "connected"
        except Exception as e:
            health_data["supabase"]["status"] = f"error: {str(e)}"
        
        # Test database connectivity
        health_data["database"] = {
            "configured": bool(settings.DATABASE_URL),
            "url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "not configured"
        }
        
        try:
            from app.core.database import health_check_db
            db_healthy = await health_check_db()
            health_data["database"]["status"] = "connected" if db_healthy else "connection failed"
        except Exception as e:
            health_data["database"]["status"] = f"error: {str(e)}"
        
        # Email service status
        health_data["email_service"] = {
            "enabled": settings.EMAIL_ENABLED,
            "configured": bool(settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD and settings.EMAIL_FROM),
            "reminder_schedule": f"{settings.REMINDER_DAY} at {settings.REMINDER_HOUR:02d}:{settings.REMINDER_MINUTE:02d} UTC"
        }
        
        # Scheduler status
        health_data["scheduler"] = {
            "running": scheduler_service.scheduler.running if scheduler_service.scheduler else False
        }
        
        return health_data
        
    except Exception as e:
        # Return unhealthy status
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )