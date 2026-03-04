"""File Storage Service"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple, List

from src.config import get_settings


# Required files for simulation tasks
REQUIRED_FILES = [
    "config.yml",
    "feature_line_ref_0.stp",
    "feature_line_ref_1.stp",
    "left_boundary.txt",
    "materials.csv",
    "mould_section.stp",
    "strip_section.stp",
]

# Optional files
OPTIONAL_FILES = [
    "product.stp",
    "mesh.jnl",
    "support_side_mould_x.stp",
    "support_up_mould_x.stp",  # 上模整形板文件
    "rubber_section.stp",
]

# Allowed file extensions
ALLOWED_EXTENSIONS = ["stp", "txt", "csv", "yml", "jnl"]

# Max file size in bytes (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


class FileStorageService:
    """Service for managing task files"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_path = Path(self.settings.storage.base_path)
    
    def ensure_task_dir(self, task_id: str) -> Path:
        """Create task directory if not exists, return path"""
        task_dir = self.base_path / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir
    
    def get_task_dir(self, task_id: str) -> Path:
        """Get task directory path"""
        return self.base_path / task_id
    
    def save_file(self, task_id: str, filename: str, content: bytes) -> Tuple[Path, int]:
        """
        Save file to task directory
        Returns: (file_path, file_size)
        """
        task_dir = self.ensure_task_dir(task_id)
        file_path = task_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path, len(content)
    
    def delete_task_dir(self, task_id: str) -> bool:
        """Delete task directory and all its contents"""
        task_dir = self.get_task_dir(task_id)
        if task_dir.exists():
            shutil.rmtree(task_dir)
            return True
        return False
    
    def get_result_file(self, task_id: str) -> Optional[Path]:
        """Find result .stp file in task's result directory"""
        task_dir = self.get_task_dir(task_id)
        result_dir = task_dir / "result"
        
        if not result_dir.exists():
            return None
        
        # Find .stp files in result directory
        stp_files = list(result_dir.glob("*.stp"))
        if stp_files:
            return stp_files[0]
        
        return None
    
    def file_exists(self, task_id: str, filename: str) -> bool:
        """Check if file exists in task directory"""
        file_path = self.get_task_dir(task_id) / filename
        return file_path.exists()
    
    def list_files(self, task_id: str) -> List[str]:
        """List all files in task directory"""
        task_dir = self.get_task_dir(task_id)
        if not task_dir.exists():
            return []
        
        return [f.name for f in task_dir.iterdir() if f.is_file()]


def validate_file(filename: str, size: int) -> Tuple[bool, str]:
    """
    Validate file for upload
    Returns: (is_valid, error_message)
    """
    # Check extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"不支持的文件格式: {ext}"
    
    # Check if filename is in allowed list (case-insensitive)
    filename_lower = filename.lower()
    all_allowed = [f.lower() for f in REQUIRED_FILES + OPTIONAL_FILES]
    
    # Also allow files matching pattern support_side_mould_*.stp
    is_support_file = filename_lower.startswith("support_side_mould_") and filename_lower.endswith(".stp")
    
    if filename_lower not in all_allowed and not is_support_file:
        return False, f"不在允许的文件列表中: {filename}"
    
    # Check file size
    if size > MAX_FILE_SIZE:
        return False, f"文件大小超过限制(100MB): {size / (1024*1024):.2f}MB"
    
    return True, ""


def get_missing_files(uploaded_files: List[str]) -> List[str]:
    """Get list of missing required files"""
    uploaded_lower = [f.lower() for f in uploaded_files]
    missing = []
    
    for required in REQUIRED_FILES:
        if required.lower() not in uploaded_lower:
            missing.append(required)
    
    return missing


def get_file_type(filename: str) -> str:
    """
    Determine if file is required or optional
    Returns: 'required', 'optional', or 'unknown'
    """
    filename_lower = filename.lower()
    
    # Check required files (case-insensitive)
    required_lower = [f.lower() for f in REQUIRED_FILES]
    if filename_lower in required_lower:
        return "required"
    
    # Check optional files (case-insensitive)
    optional_lower = [f.lower() for f in OPTIONAL_FILES]
    if filename_lower in optional_lower:
        return "optional"
    
    # Check pattern match for support files
    if filename_lower.startswith("support_side_mould_") and filename_lower.endswith(".stp"):
        return "optional"
    if filename_lower.startswith("support_up_mould_") and filename_lower.endswith(".stp"):
        return "optional"
    
    return "unknown"
