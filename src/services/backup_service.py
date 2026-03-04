"""Backup Service - Automatic database backup"""
import os
import shutil
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from src.config import get_settings


class BackupService:
    """Service for automatic database backup"""
    
    def __init__(self, interval_hours: int = 1, retention_hours: int = 24):
        self.interval = interval_hours * 3600  # Convert to seconds
        self.retention = retention_hours * 3600
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the backup service"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._backup_loop())
    
    async def stop(self):
        """Stop the backup service"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _backup_loop(self):
        """Main backup loop"""
        while self._running:
            try:
                await self._run_backup()
                await self._cleanup_old_backups()
            except Exception as e:
                print(f"Backup error: {e}")
            
            await asyncio.sleep(self.interval)
    
    async def _run_backup(self):
        """Perform database backup"""
        settings = get_settings()
        
        db_path = Path(settings.database.path)
        backup_dir = Path(settings.database.backup_path)
        
        if not db_path.exists():
            return
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"aid_service_{timestamp}.db"
        backup_path = backup_dir / backup_filename
        
        # Ensure backup directory exists
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
    
    async def _cleanup_old_backups(self):
        """Remove backup files older than retention period"""
        settings = get_settings()
        backup_dir = Path(settings.database.backup_path)
        
        if not backup_dir.exists():
            return
        
        cutoff_time = datetime.now() - timedelta(seconds=self.retention)
        
        for backup_file in backup_dir.glob("aid_service_*.db"):
            try:
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    backup_file.unlink()
                    print(f"Removed old backup: {backup_file}")
            except Exception as e:
                print(f"Error cleaning up backup {backup_file}: {e}")


# Global service instance
_backup_service: Optional[BackupService] = None


def get_backup_service() -> BackupService:
    """Get global backup service instance"""
    global _backup_service
    if _backup_service is None:
        _backup_service = BackupService()
    return _backup_service
