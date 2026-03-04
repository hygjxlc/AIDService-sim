"""API Router - Central router for all endpoints"""
from fastapi import APIRouter

api_router = APIRouter()

# Import endpoint modules
from src.api.health import router as health_router
from src.api.tasks import router as tasks_router
from src.api.files import router as files_router
from src.api.callback import router as callback_router

# Include routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(tasks_router, tags=["Tasks"])
api_router.include_router(files_router, tags=["Files"])
api_router.include_router(callback_router, tags=["Internal"])
