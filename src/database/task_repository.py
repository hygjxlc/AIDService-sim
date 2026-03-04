"""Task Repository - CRUD operations for task_info table"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.task import TaskInfo


class TaskRepository:
    """Repository for TaskInfo CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, task_id: str, simulate_type: str, task_name: str) -> TaskInfo:
        """Create a new task"""
        now = datetime.now().isoformat()
        task = TaskInfo(
            task_id=task_id,
            simulate_type=simulate_type,
            task_name=task_name,
            status="created",
            create_time=now,
            update_time=now
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task by ID"""
        return self.db.query(TaskInfo).filter(TaskInfo.task_id == task_id).first()
    
    def get_all_tasks(self) -> List[TaskInfo]:
        """Get all tasks"""
        return self.db.query(TaskInfo).all()
    
    def get_tasks_by_status(self, status: str) -> List[TaskInfo]:
        """Get all tasks with specific status"""
        return self.db.query(TaskInfo).filter(TaskInfo.status == status).all()
    
    def update_status(self, task_id: str, status: str) -> Optional[TaskInfo]:
        """Update task status"""
        task = self.get_task(task_id)
        if task:
            task.status = status
            task.update_time = datetime.now().isoformat()
            self.db.commit()
            self.db.refresh(task)
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task by ID"""
        task = self.get_task(task_id)
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False
    
    def get_max_sequence(self, simulate_type: str) -> int:
        """Get maximum sequence number for a simulate type"""
        # Query tasks with this simulate_type and extract sequence
        tasks = self.db.query(TaskInfo).filter(
            TaskInfo.simulate_type == simulate_type
        ).all()
        
        max_seq = 0
        prefix_len = len(simulate_type)
        
        for task in tasks:
            try:
                seq_str = task.task_id[prefix_len:]
                seq = int(seq_str)
                if seq > max_seq:
                    max_seq = seq
            except (ValueError, IndexError):
                continue
        
        return max_seq
    
    def task_exists(self, task_id: str) -> bool:
        """Check if task exists"""
        return self.db.query(TaskInfo).filter(TaskInfo.task_id == task_id).count() > 0
