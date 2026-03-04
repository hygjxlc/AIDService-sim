"""FileInfo ORM Model"""
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class FileInfo(Base):
    """File information table"""
    __tablename__ = "file_info"
    
    file_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_time: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    
    def __repr__(self) -> str:
        return f"<FileInfo(file_id={self.file_id}, file_name={self.file_name})>"
