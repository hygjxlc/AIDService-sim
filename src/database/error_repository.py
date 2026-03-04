"""Error Repository - CRUD operations for error_log table"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.error_log import ErrorLog


class ErrorLogRepository:
    """Repository for ErrorLog CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_error(
        self,
        task_id: str,
        error_code: int,
        error_message: str,
        interface_name: str
    ) -> ErrorLog:
        """Log an error"""
        now = datetime.now().isoformat()
        
        error_log = ErrorLog(
            task_id=task_id,
            error_code=error_code,
            error_message=error_message,
            error_time=now,
            interface_name=interface_name
        )
        self.db.add(error_log)
        self.db.commit()
        self.db.refresh(error_log)
        return error_log
    
    def get_error(self, log_id: int) -> Optional[ErrorLog]:
        """Get error by ID"""
        return self.db.query(ErrorLog).filter(ErrorLog.log_id == log_id).first()
    
    def get_errors_by_task(self, task_id: str) -> List[ErrorLog]:
        """Get all errors for a task"""
        return self.db.query(ErrorLog).filter(ErrorLog.task_id == task_id).all()
    
    def get_latest_error(self, task_id: str) -> Optional[ErrorLog]:
        """Get the most recent error for a task"""
        return self.db.query(ErrorLog).filter(
            ErrorLog.task_id == task_id
        ).order_by(ErrorLog.log_id.desc()).first()
    
    def delete_errors_by_task(self, task_id: str) -> int:
        """Delete all errors for a task, return count of deleted errors"""
        count = self.db.query(ErrorLog).filter(ErrorLog.task_id == task_id).delete()
        self.db.commit()
        return count
