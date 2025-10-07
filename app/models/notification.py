from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  # Pi Network user ID
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # quest_win, quest_end, new_quest, bonus, special
    quest_id = Column(String, nullable=True)  # Optional - for quest-related notifications
    is_read = Column(Boolean, default=False)
    notification_metadata = Column(JSON, default=dict)  # Additional data (reward amount, quest details, etc.)
    created_at = Column(DateTime, default=func.now())
    read_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "quest_id": self.quest_id,
            "is_read": self.is_read,
            "metadata": self.notification_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }
