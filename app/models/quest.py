from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from enum import Enum

class QuestStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    STALLED = "stalled"

class Quest(Base):
    __tablename__ = "quests"
    
    quest_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    context = Column(Text)
    details = Column(JSON)  # stores properties, instructions, additional_text
    profile_image_url = Column(Text)
    media_url = Column(Text)
    distribution_rules = Column(JSON)  # distribution rules JSON
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Quest status management
    status = Column(String, default=QuestStatus.ACTIVE)  # active, ended, stalled
    is_paused = Column(Boolean, default=False)
    paused_at = Column(DateTime, nullable=True)
    paused_duration = Column(Integer, default=0)  # Total paused time in seconds
    original_end_date = Column(DateTime, nullable=True)  # Store original end date before pauses
    
    # Relationships
    participants = relationship("QuestParticipant", back_populates="quest")
    user_credits = relationship("UserCredits", back_populates="quest")
    credit_transactions = relationship("CreditTransaction", back_populates="quest")
    ad_rewards = relationship("AdReward", back_populates="quest")
