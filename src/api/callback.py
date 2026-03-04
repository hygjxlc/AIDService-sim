"""Internal Callback Handler for Algorithm Layer"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.config import get_settings
from src.database.db import get_db
from src.database.task_repository import TaskRepository
from src.database.error_repository import ErrorLogRepository

router = APIRouter()


class CallbackRequest(BaseModel):
    """Callback request from algorithm layer"""
    task_id: str
    event_type: str  # "finished" or "failed"
    result_file_path: Optional[str] = None
    error_message: Optional[str] = None
    internal_token: str  # Internal auth token


@router.post("/internal/callback")
async def algorithm_callback(request: CallbackRequest, db: Session = Depends(get_db)):
    """
    Callback endpoint for algorithm layer (TASK-017)
    Receives simulation completion or failure notifications
    """
    # Validate internal token from configuration
    settings = get_settings()
    if request.internal_token != settings.internal.callback_token:
        return {"success": False, "message": "Invalid token"}
    
    task_repo = TaskRepository(db)
    error_repo = ErrorLogRepository(db)
    
    # Check task exists
    task = task_repo.get_task(request.task_id)
    if not task:
        return {"success": False, "message": "Task not found"}
    
    if request.event_type == "finished":
        # Update task status to finished
        task_repo.update_status(request.task_id, "finished")
        return {"success": True, "message": "Task marked as finished"}
    
    elif request.event_type == "failed":
        # Update task status to failed
        task_repo.update_status(request.task_id, "failed")
        
        # Log error
        error_repo.log_error(
            task_id=request.task_id,
            error_code=500,
            error_message=request.error_message or "Unknown error",
            interface_name="algorithm_callback"
        )
        return {"success": True, "message": "Task marked as failed"}
    
    return {"success": False, "message": f"Unknown event type: {request.event_type}"}
