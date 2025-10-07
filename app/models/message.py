from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"))  # null for AI messages
    content = Column(Text, nullable=False)
    score = Column(Integer)
    created_at = Column(DateTime, default=func.now())
