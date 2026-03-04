"""Status Sync Service - Background task to sync task status from algorithm layer"""
import asyncio
from typing import Optional

from src.config import get_settings
from src.database.db import get_session
from src.database.task_repository import TaskRepository
from src.database.error_repository import ErrorLogRepository
from src.services.algorithm_client import get_client


class StatusSyncService:
    """Background service to sync task status from algorithm layer"""
    
    def __init__(self, interval_seconds: int = 10):
        self.interval = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the background sync task"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._sync_loop())
    
    async def stop(self):
        """Stop the background sync task"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _sync_loop(self):
        """Main sync loop"""
        while self._running:
            try:
                await self._sync_running_tasks()
            except Exception as e:
                # Log error but continue running
                print(f"Status sync error: {e}")
            
            await asyncio.sleep(self.interval)
    
    async def _sync_running_tasks(self):
        """Sync status for all running tasks"""
        db = get_session()
        try:
            task_repo = TaskRepository(db)
            error_repo = ErrorLogRepository(db)
            client = get_client()
            
            # Get all running tasks
            running_tasks = task_repo.get_tasks_by_status("running")
            
            for task in running_tasks:
                try:
                    # Query algorithm layer for status
                    status = await client.get_status(task.task_id)
                    
                    # Update if status changed
                    if status.status in ["finished", "failed", "stop"]:
                        task_repo.update_status(task.task_id, status.status)
                        
                        # Log error if failed
                        if status.status == "failed" and status.error_info:
                            error_repo.log_error(
                                task_id=task.task_id,
                                error_code=500,
                                error_message=status.error_info,
                                interface_name="status_sync"
                            )
                
                except Exception as e:
                    print(f"Error syncing task {task.task_id}: {e}")
        
        finally:
            db.close()


# Global service instance
_status_sync_service: Optional[StatusSyncService] = None


def get_status_sync_service() -> StatusSyncService:
    """Get global status sync service instance"""
    global _status_sync_service
    if _status_sync_service is None:
        _status_sync_service = StatusSyncService()
    return _status_sync_service
