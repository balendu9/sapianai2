from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class DailyAIMessage(Base):
    __tablename__ = "daily_ai_messages"

    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=True)  # Optional - can be general message
    content = Column(String, nullable=False)
    message_type = Column(String, nullable=False, default="daily_reminder")  # daily_reminder, quest_promotion, etc.
    sent_at = Column(DateTime, default=func.now())
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # AI generation metadata
    ai_generation_metadata = Column(JSON, nullable=True)  # Store AI generation details
    
    # Relationships
    user = relationship("User")
    quest = relationship("Quest")
