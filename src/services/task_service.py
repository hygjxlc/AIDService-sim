"""Task Business Service"""
import re
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from src.database.task_repository import TaskRepository
from src.database.file_repository import FileRepository
from src.database.error_repository import ErrorLogRepository
from src.utils.task_id_generator import generate_task_id, is_valid_simulate_type
from src.services.file_service import FileStorageService, get_missing_files


# Task name validation pattern: 1-64 chars, letters/numbers/underscore
TASK_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{1,64}$")


class TaskService:
    """Business logic service for task operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.file_repo = FileRepository(db)
        self.error_repo = ErrorLogRepository(db)
        self.file_service = FileStorageService()
    
    def validate_create_params(self, simulate_type: str, task_name: str) -> Tuple[bool, str]:
        """Validate task creation parameters"""
        # Check simulate type
        if not is_valid_simulate_type(simulate_type):
            return False, f"无效的仿真类型: {simulate_type}"
        
        # Check task name
        if not TASK_NAME_PATTERN.match(task_name):
            return False, "任务名称格式错误(1-64字符,仅字母/数字/下划线)"
        
        return True, ""
    
    def create_task(self, simulate_type: str, task_name: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new task
        Returns: (success, message, task_id)
        """
        # Validate parameters
        is_valid, error_msg = self.validate_create_params(simulate_type, task_name)
        if not is_valid:
            return False, error_msg, None
        
        try:
            # Generate task ID
            task_id = generate_task_id(simulate_type, self.db)
            
            # Create task directory
            self.file_service.ensure_task_dir(task_id)
            
            # Create task record
            self.task_repo.create_task(task_id, simulate_type, task_name)
            
            return True, "任务创建成功", task_id
        
        except Exception as e:
            return False, f"任务创建失败: {str(e)}", None
    
    def verify_task(self, task_id: str) -> Tuple[bool, bool, list]:
        """
        Verify task file completeness
        Returns: (task_exists, ready, missing_files)
        """
        # Check task exists
        task = self.task_repo.get_task(task_id)
        if not task:
            return False, False, []
        
        # Get uploaded files
        uploaded_files = self.file_repo.get_uploaded_file_names(task_id)
        
        # Check missing files
        missing = get_missing_files(uploaded_files)
        ready = len(missing) == 0
        
        return True, ready, missing
    
    def start_task(self, task_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Start simulation task
        Returns: (success, message, status)
        """
        # Check task exists
        task = self.task_repo.get_task(task_id)
        if not task:
            return False, "任务不存在", None
        
        # Check status
        if task.status not in ["created", "stop"]:
            return False, f"任务状态无法启动: {task.status}", task.status
        
        # Verify files
        uploaded_files = self.file_repo.get_uploaded_file_names(task_id)
        missing = get_missing_files(uploaded_files)
        if missing:
            return False, f"缺少必需文件: {', '.join(missing)}", task.status
        
        # TODO: Call algorithm layer to start simulation
        # For now, just update status
        self.task_repo.update_status(task_id, "running")
        
        return True, "任务启动成功", "running"
    
    def stop_task(self, task_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Stop simulation task
        Returns: (success, message, status)
        """
        # Check task exists
        task = self.task_repo.get_task(task_id)
        if not task:
            return False, "任务不存在", None
        
        # Check status
        if task.status != "running":
            return True, "操作无效", task.status
        
        # TODO: Call algorithm layer to stop simulation
        # For now, just update status
        self.task_repo.update_status(task_id, "stop")
        
        return True, "任务停止成功", "stop"
    
    def delete_task(self, task_id: str) -> Tuple[bool, str]:
        """
        Delete simulation task
        Returns: (success, message)
        """
        # Check task exists
        task = self.task_repo.get_task(task_id)
        if not task:
            return False, "任务不存在"
        
        # If running, stop first
        if task.status == "running":
            # TODO: Call algorithm layer to stop
            pass
        
        try:
            # Delete task directory
            self.file_service.delete_task_dir(task_id)
            
            # Delete file records
            self.file_repo.delete_files_by_task(task_id)
            
            # Delete error logs
            self.error_repo.delete_errors_by_task(task_id)
            
            # Delete task record
            self.task_repo.delete_task(task_id)
            
            return True, "任务删除成功"
        
        except Exception as e:
            return False, f"任务删除失败: {str(e)}"
    
    def query_status(self, task_id: str) -> Tuple[str, Optional[dict]]:
        """
        Query task status
        Returns: (status, extra_info)
        """
        task = self.task_repo.get_task(task_id)
        if not task:
            return "not_exist", None
        
        extra = None
        
        if task.status == "running":
            # TODO: Get progress from algorithm layer
            extra = {"cycle": 0, "errorInfo": None}
        
        elif task.status == "failed":
            # Get latest error
            error = self.error_repo.get_latest_error(task_id)
            if error:
                extra = {
                    "error_code": error.error_code,
                    "error_message": error.error_message,
                    "error_time": error.error_time
                }
        
        return task.status, extra
    
    def get_result_file(self, task_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Get task result file path
        Returns: (success, message, file_path)
        """
        task = self.task_repo.get_task(task_id)
        if not task:
            return False, "任务不存在", None
        
        if task.status != "finished":
            return False, f"任务未完成: {task.status}", None
        
        result_file = self.file_service.get_result_file(task_id)
        if not result_file:
            return False, "结果文件不存在", None
        
        return True, "获取成功", str(result_file)
