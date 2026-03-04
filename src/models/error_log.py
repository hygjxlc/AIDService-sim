"""ErrorLog ORM Model"""
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class ErrorLog(Base):
    """Error log table"""
    __tablename__ = "error_log"
    
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    error_code: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    error_time: Mapped[str] = mapped_column(Text, nullable=False)
    interface_name: Mapped[str] = mapped_column(String(64), nullable=False)
    
    def __repr__(self) -> str:
        return f"<ErrorLog(log_id={self.log_id}, error_code={self.error_code})>"
