"""Health Check Endpoint"""
import sys
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import text

from src.database.db import get_engine
from src.utils.response import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check - no authentication required"""
    response = HealthResponse(
        code=200,
        status="OK",
        message="服务正常",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    
    # Check SQLite
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        response.sqlite = "connected"
    except Exception as e:
        response.code = 500
        response.status = "DEGRADED"
        response.message = f"数据库连接异常: {str(e)}"
        response.sqlite = f"error: {str(e)}"
    
    # Check algorithm layer (placeholder for now)
    response.algorithm = "mock_mode"
    
    return response
