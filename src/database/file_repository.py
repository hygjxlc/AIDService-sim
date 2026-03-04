"""File Repository - CRUD operations for file_info table"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.file import FileInfo


class FileRepository:
    """Repository for FileInfo CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def upsert_file(
        self,
        task_id: str,
        file_name: str,
        file_path: str,
        file_size: int,
        file_type: str
    ) -> FileInfo:
        """Insert or update file record (upsert by task_id + file_name)"""
        now = datetime.now().isoformat()
        
        # Check if file already exists
        existing = self.db.query(FileInfo).filter(
            FileInfo.task_id == task_id,
            FileInfo.file_name == file_name
        ).first()
        
        if existing:
            # Update existing record
            existing.file_path = file_path
            existing.file_size = file_size
            existing.upload_time = now
            existing.file_type = file_type
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Insert new record
            file_info = FileInfo(
                task_id=task_id,
                file_name=file_name,
                file_path=file_path,
                file_size=file_size,
                upload_time=now,
                file_type=file_type
            )
            self.db.add(file_info)
            self.db.commit()
            self.db.refresh(file_info)
            return file_info
    
    def get_file(self, file_id: int) -> Optional[FileInfo]:
        """Get file by ID"""
        return self.db.query(FileInfo).filter(FileInfo.file_id == file_id).first()
    
    def get_files_by_task(self, task_id: str) -> List[FileInfo]:
        """Get all files for a task"""
        return self.db.query(FileInfo).filter(FileInfo.task_id == task_id).all()
    
    def get_file_by_name(self, task_id: str, file_name: str) -> Optional[FileInfo]:
        """Get specific file by task ID and file name"""
        return self.db.query(FileInfo).filter(
            FileInfo.task_id == task_id,
            FileInfo.file_name == file_name
        ).first()
    
    def delete_file(self, file_id: int) -> bool:
        """Delete file by ID"""
        file_info = self.get_file(file_id)
        if file_info:
            self.db.delete(file_info)
            self.db.commit()
            return True
        return False
    
    def delete_files_by_task(self, task_id: str) -> int:
        """Delete all files for a task, return count of deleted files"""
        count = self.db.query(FileInfo).filter(FileInfo.task_id == task_id).delete()
        self.db.commit()
        return count
    
    def get_uploaded_file_names(self, task_id: str) -> List[str]:
        """Get list of uploaded file names for a task"""
        files = self.get_files_by_task(task_id)
        return [f.file_name for f in files]
