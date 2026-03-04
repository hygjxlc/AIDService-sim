"""Task ID Generator"""
from sqlalchemy.orm import Session
from src.database.task_repository import TaskRepository


# Valid simulation types
VALID_SIMULATE_TYPES = [
    "LaWan",    # 拉弯工艺
    "CHOnYA",   # 冲压工艺
    "ZhuZao",   # 铸造工艺
    "ZhaZhi",   # 轧制工艺
    "ZHEWan",   # 折弯工艺
    "JIYA",     # 挤压工艺
]


def is_valid_simulate_type(simulate_type: str) -> bool:
    """Check if simulate type is valid"""
    return simulate_type in VALID_SIMULATE_TYPES


def generate_task_id(simulate_type: str, db: Session) -> str:
    """
    Generate a unique task ID in format: {simulateType}{8-digit sequence}
    Example: LaWan00000001
    """
    if not is_valid_simulate_type(simulate_type):
        raise ValueError(f"Invalid simulate type: {simulate_type}")
    
    repo = TaskRepository(db)
    max_seq = repo.get_max_sequence(simulate_type)
    next_seq = max_seq + 1
    
    # Format: simulateType + 8-digit zero-padded sequence
    task_id = f"{simulate_type}{next_seq:08d}"
    
    return task_id
