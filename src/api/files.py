"""File Upload Endpoint"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database.db import get_db
from src.database.task_repository import TaskRepository
from src.database.file_repository import FileRepository
from src.services.file_service import FileStorageService, validate_file, get_file_type
from src.utils.response import FileUploadResponse, ErrorCode

router = APIRouter()


@router.post("/uploadParamfiles", response_model=FileUploadResponse)
async def upload_files(
    TaskID: str = Form(...),
    api_key: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload parameter files for a task (TASK-008)"""
    task_repo = TaskRepository(db)
    file_repo = FileRepository(db)
    file_service = FileStorageService()
    
    # Check task exists
    task = task_repo.get_task(TaskID)
    if not task:
        return FileUploadResponse(
            code=ErrorCode.NOT_FOUND,
            message="任务不存在",
            taskID=TaskID,
            uploadFiles=[],
            failFiles=[]
        )
    
    upload_success = []
    upload_fail = []
    
    for upload_file in files:
        filename = upload_file.filename
        
        # Read file content
        try:
            content = await upload_file.read()
            file_size = len(content)
        except Exception as e:
            upload_fail.append({
                "filename": filename,
                "reason": f"读取失败: {str(e)}"
            })
            continue
        
        # Validate file
        is_valid, error_msg = validate_file(filename, file_size)
        if not is_valid:
            upload_fail.append({
                "filename": filename,
                "reason": error_msg
            })
            continue
        
        # Save file
        try:
            # Determine file type (required/optional)
            file_type = get_file_type(filename)
            
            # Save to disk
            file_path, size = file_service.save_file(TaskID, filename, content)
            
            # Save to database with file_type = required/optional
            file_repo.upsert_file(
                task_id=TaskID,
                file_name=filename,
                file_path=str(file_path),
                file_size=size,
                file_type=file_type
            )
            
            upload_success.append({
                "filename": filename,
                "size": size
            })
        
        except Exception as e:
            upload_fail.append({
                "filename": filename,
                "reason": f"保存失败: {str(e)}"
            })
    
    # Determine response code
    if len(upload_success) == 0 and len(upload_fail) > 0:
        code = ErrorCode.FILE_UPLOAD_FAIL
        message = "所有文件上传失败"
    elif len(upload_fail) > 0:
        code = 200
        message = "部分文件上传成功"
    else:
        code = 200
        message = "文件上传成功"
    
    return FileUploadResponse(
        code=code,
        message=message,
        taskID=TaskID,
        uploadFiles=upload_success,
        failFiles=upload_fail
    )
