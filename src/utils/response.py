"""Response utilities and error codes"""
from enum import IntEnum
from typing import Any, Optional, Dict
from pydantic import BaseModel


class ErrorCode(IntEnum):
    """System error codes"""
    SUCCESS = 200
    TASK_CREATE_FAIL = 301
    FILE_MISSING = 302
    FILE_UPLOAD_FAIL = 303
    UNAUTHORIZED = 401
    TASK_STOP_FAIL = 402
    TASK_DELETE_FAIL = 403
    NOT_FOUND = 404
    ALGORITHM_ERROR = 500


ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.TASK_CREATE_FAIL: "任务创建失败",
    ErrorCode.FILE_MISSING: "工作文件缺失",
    ErrorCode.FILE_UPLOAD_FAIL: "上传文件失败",
    ErrorCode.UNAUTHORIZED: "API Key认证失败，无效的密钥",
    ErrorCode.TASK_STOP_FAIL: "任务停止失败",
    ErrorCode.TASK_DELETE_FAIL: "任务删除失败",
    ErrorCode.NOT_FOUND: "获取结果失败",
    ErrorCode.ALGORITHM_ERROR: "算法内部运行错误",
}


class BaseResponse(BaseModel):
    """Unified response format"""
    code: int = 200
    message: str = "操作成功"
    taskID: Optional[str] = None
    
    class Config:
        extra = "allow"
    
    @classmethod
    def success(cls, task_id: Optional[str] = None, message: str = None, **extra) -> "BaseResponse":
        """Create success response"""
        return cls(
            code=ErrorCode.SUCCESS,
            message=message or ERROR_MESSAGES[ErrorCode.SUCCESS],
            taskID=task_id,
            **extra
        )
    
    @classmethod
    def error(cls, error_code: ErrorCode, message: str = None, task_id: Optional[str] = None, **extra) -> "BaseResponse":
        """Create error response"""
        return cls(
            code=error_code,
            message=message or ERROR_MESSAGES.get(error_code, "未知错误"),
            taskID=task_id,
            **extra
        )


class TaskCreateResponse(BaseResponse):
    """Response for task creation"""
    pass


class FileUploadResponse(BaseResponse):
    """Response for file upload"""
    uploadFiles: list = []
    failFiles: list = []


class TaskVerifyResponse(BaseResponse):
    """Response for task verification"""
    ready: bool = False
    missingFiles: list = []


class TaskStatusResponse(BaseResponse):
    """Response for task status query"""
    status: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response for health check - 符合规格文档要求"""
    code: int = 200
    status: str = "OK"
    message: str = "服务正常"
    timestamp: str = ""
    version: str = "1.0.0"
    python: str = ""
    sqlite: str = ""
    algorithm: str = ""
