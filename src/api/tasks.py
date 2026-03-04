"""Task Management Endpoints"""
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.database.db import get_db
from src.services.task_service import TaskService
from src.utils.response import (
    BaseResponse, ErrorCode, TaskCreateResponse,
    TaskVerifyResponse, TaskStatusResponse
)

router = APIRouter()


class TaskCreateRequest(BaseModel):
    """Request body for task creation"""
    simulateType: str
    taskName: str
    api_key: str


class TaskRequest(BaseModel):
    """Request body for task operations"""
    TaskID: str
    api_key: str


@router.post("/newTaskCreate", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest, db: Session = Depends(get_db)):
    """Create a new simulation task (TASK-007)"""
    service = TaskService(db)
    
    success, message, task_id = service.create_task(
        request.simulateType,
        request.taskName
    )
    
    if success:
        return TaskCreateResponse.success(task_id=task_id, message=message)
    else:
        return TaskCreateResponse.error(
            ErrorCode.TASK_CREATE_FAIL,
            message=message
        )


@router.post("/newTaskverify", response_model=TaskVerifyResponse)
async def verify_task(request: TaskRequest, db: Session = Depends(get_db)):
    """Verify task file completeness (TASK-009)"""
    service = TaskService(db)
    
    task_exists, ready, missing_files = service.verify_task(request.TaskID)
    
    if not task_exists:
        return TaskVerifyResponse.error(
            ErrorCode.NOT_FOUND,
            message="任务不存在",
            task_id=request.TaskID,
            ready=False,
            missingFiles=[]
        )
    
    return TaskVerifyResponse(
        code=200,
        message="校验完成",
        taskID=request.TaskID,
        ready=ready,
        missingFiles=missing_files
    )


@router.post("/startTask", response_model=BaseResponse)
async def start_task(request: TaskRequest, db: Session = Depends(get_db)):
    """Start simulation task (TASK-010)"""
    service = TaskService(db)
    
    success, message, status = service.start_task(request.TaskID)
    
    if success:
        return BaseResponse.success(
            task_id=request.TaskID,
            message=message,
            status=status
        )
    else:
        # Task not found
        if "不存在" in message:
            return BaseResponse.error(
                ErrorCode.NOT_FOUND,
                message=message,
                task_id=request.TaskID
            )
        # Cannot start
        return BaseResponse.error(
            ErrorCode.UNAUTHORIZED,
            message=message,
            task_id=request.TaskID,
            status=status
        )


@router.post("/stopTask", response_model=BaseResponse)
async def stop_task(request: TaskRequest, db: Session = Depends(get_db)):
    """Stop simulation task (TASK-011)"""
    service = TaskService(db)
    
    success, message, status = service.stop_task(request.TaskID)
    
    if not success and "不存在" in message:
        return BaseResponse.error(
            ErrorCode.NOT_FOUND,
            message=message,
            task_id=request.TaskID
        )
    
    return BaseResponse.success(
        task_id=request.TaskID,
        message=message,
        status=status
    )


@router.post("/deleteTask", response_model=BaseResponse)
async def delete_task(request: TaskRequest, db: Session = Depends(get_db)):
    """Delete simulation task (TASK-012)"""
    service = TaskService(db)
    
    success, message = service.delete_task(request.TaskID)
    
    if success:
        return BaseResponse.success(
            task_id=request.TaskID,
            message=message
        )
    else:
        if "不存在" in message:
            return BaseResponse.error(
                ErrorCode.NOT_FOUND,
                message=message,
                task_id=request.TaskID
            )
        return BaseResponse.error(
            ErrorCode.TASK_DELETE_FAIL,
            message=message,
            task_id=request.TaskID
        )


@router.post("/queryTaskStatus", response_model=TaskStatusResponse)
async def query_task_status(request: TaskRequest, db: Session = Depends(get_db)):
    """Query task status (TASK-013)"""
    service = TaskService(db)
    
    status, extra = service.query_status(request.TaskID)
    
    return TaskStatusResponse(
        code=200,
        message="查询成功",
        taskID=request.TaskID,
        status=status,
        extra=extra
    )


@router.post("/fetachTaskResult")
async def fetch_task_result(request: TaskRequest, db: Session = Depends(get_db)):
    """Fetch task result file (TASK-014)"""
    service = TaskService(db)
    
    success, message, file_path = service.get_result_file(request.TaskID)
    
    if not success:
        return BaseResponse.error(
            ErrorCode.NOT_FOUND,
            message=message,
            task_id=request.TaskID
        )
    
    # Return file
    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]
    )
