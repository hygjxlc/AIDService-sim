"""AID-Service Main Application"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.database.db import init_db
from src.utils.response import BaseResponse, ErrorCode
from src.utils.logger import setup_logging, get_system_logger
from src.services.auth import AuthMiddleware
from src.services.status_sync import get_status_sync_service
from src.services.backup_service import get_backup_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Setup logging
    setup_logging()
    logger = get_system_logger()
    
    # Startup
    settings = get_settings()
    init_db(settings.database.path)
    logger.info(f"AID-Service started. Database: {settings.database.path}")
    
    # Start background services
    status_sync = get_status_sync_service()
    backup_service = get_backup_service()
    
    await status_sync.start()
    await backup_service.start()
    logger.info("Background services started")
    
    yield
    
    # Shutdown
    logger.info("AID-Service shutting down...")
    await status_sync.stop()
    await backup_service.stop()
    logger.info("Background services stopped")


app = FastAPI(
    title="AID-Service",
    description="金属加工仿真系统服务端",
    version="1.0.0",
    lifespan=lifespan
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    from src.utils.logger import get_error_logger
    logger = get_error_logger()
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=200,
        content=BaseResponse.error(
            ErrorCode.ALGORITHM_ERROR,
            message="服务内部错误"
        ).model_dump()
    )


# Import and include routers
from src.api.router import api_router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
