from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class NotificationType(str, enum.Enum):
    """通知类型"""
    INFO = "info"       # 信息
    WARNING = "warning" # 警告
    TODO = "todo"       # 待办


class Notification(Base):
    """通知"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)  # 标题
    content = Column(Text, nullable=True)  # 内容
    type = Column(SQLEnum(NotificationType), default=NotificationType.INFO)  # 类型
    is_read = Column(Boolean, default=False)  # 已读状态
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"