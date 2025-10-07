from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class UserCredits(Base):
    """Track daily credits per user per quest"""
    __tablename__ = "user_credits"
    
    credit_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False, index=True)
    daily_credits = Column(Integer, default=1)  # Credits per day for this quest
    credits_used_today = Column(Integer, default=0)  # Credits used today
    last_reset_date = Column(DateTime, default=datetime.utcnow)  # Last time credits were reset
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to quest
    quest = relationship("Quest", back_populates="user_credits")

class CreditTransaction(Base):
    """Track credit transactions (earned, spent, purchased)"""
    __tablename__ = "credit_transactions"
    
    transaction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False, index=True)
    transaction_type = Column(String, nullable=False)  # 'daily_reset', 'purchase', 'ad_reward', 'spent'
    amount = Column(Integer, nullable=False)  # Positive for earned, negative for spent
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    transaction_metadata = Column(String, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to quest
    quest = relationship("Quest", back_populates="credit_transactions")

# Add the import for uuid
import uuid
