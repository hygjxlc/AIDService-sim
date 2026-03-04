"""TaskInfo ORM Model"""
from datetime import datetime
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class TaskInfo(Base):
    """Task information table"""
    __tablename__ = "task_info"
    
    task_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    simulate_type: Mapped[str] = mapped_column(String(16), nullable=False)
    task_name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="created")
    create_time: Mapped[str] = mapped_column(Text, nullable=False)
    update_time: Mapped[str] = mapped_column(Text, nullable=False)
    
    def __repr__(self) -> str:
        return f"<TaskInfo(task_id={self.task_id}, status={self.status})>"
