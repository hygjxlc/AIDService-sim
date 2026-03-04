"""API Key Authentication Middleware"""
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json

from src.config import get_settings
from src.utils.response import BaseResponse, ErrorCode


# Paths that don't require authentication
EXCLUDED_PATHS = [
    "/api/v1/health",
    "/api/v1/internal/callback",  # 内部回调接口使用独立token认证
    "/docs",
    "/redoc",
    "/openapi.json",
]


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for API Key authentication"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
            return await call_next(request)
        
        # Get API key from request
        api_key = await self._extract_api_key(request)
        
        # Validate API key
        settings = get_settings()
        if not api_key or api_key != settings.auth.api_key:
            return JSONResponse(
                status_code=200,
                content=BaseResponse.error(
                    ErrorCode.UNAUTHORIZED,
                    message="API Key认证失败，无效的密钥"
                ).model_dump()
            )
        
        return await call_next(request)
    
    async def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request body or query params"""
        # Try query parameter first
        api_key = request.query_params.get("api_key")
        if api_key:
            return api_key
        
        # Try to parse JSON body for POST requests
        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                try:
                    body = await request.body()
                    if body:
                        data = json.loads(body)
                        api_key = data.get("api_key")
                        # Store body for later use by endpoints
                        request.state._body = body
                        return api_key
                except (json.JSONDecodeError, Exception):
                    pass
            
            elif "multipart/form-data" in content_type:
                # For multipart, api_key should be in form field
                # This will be handled by endpoint parameters
                form = await request.form()
                api_key = form.get("api_key")
                return api_key
        
        return None


class ApiKeyAuthProvider:
    """API Key authentication provider (extensible interface)"""
    
    def __init__(self, valid_key: str):
        self._valid_key = valid_key
    
    def validate(self, key: str) -> bool:
        """Validate an API key"""
        return key == self._valid_key


def get_auth_provider() -> ApiKeyAuthProvider:
    """Get authentication provider instance"""
    settings = get_settings()
    return ApiKeyAuthProvider(settings.auth.api_key)
