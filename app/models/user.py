from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=True)  # Optional display name
    email = Column(String(200), unique=True, nullable=True)  # Optional email
    created_at = Column(DateTime, default=func.now())
    total_score = Column(Float, default=0.0)
    quests_completed = Column(Integer, default=0)
    
    # Daily AI message tracking
    last_daily_ai_message = Column(DateTime, nullable=True)  # When user last received daily AI message
    daily_ai_messages_enabled = Column(Boolean, default=True)  # User can opt out
    last_activity = Column(DateTime, default=func.now())  # Last time user was active
    
    # Relationships
    participants = relationship("QuestParticipant", back_populates="user")
