from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class GlobalLeaderboard(Base):
    """Global leaderboard across all quests"""
    __tablename__ = "global_leaderboard"
    
    user_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    total_score = Column(Float, default=0.0)  # Sum of all quest scores
    quests_participated = Column(Integer, default=0)  # Number of quests participated
    average_score = Column(Float, default=0.0)  # total_score / quests_participated
    last_updated = Column(DateTime, default=datetime.utcnow)
    rank = Column(Integer, default=0)
    
    # Relationship to daily bonuses
    daily_bonuses = relationship("GlobalDailyBonus", back_populates="user")

class GlobalDailyBonus(Base):
    """Daily bonus rewards for top 3 global leaderboard"""
    __tablename__ = "daily_bonuses"
    
    bonus_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("global_leaderboard.user_id"), nullable=False, index=True)
    bonus_date = Column(DateTime, default=datetime.utcnow)
    rank = Column(Integer, nullable=False)  # 1, 2, or 3
    amount = Column(Float, nullable=False)
    currency = Column(String, default="PI")
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship to global leaderboard
    user = relationship("GlobalLeaderboard", back_populates="daily_bonuses")

class DailyBonusConfig(Base):
    """Admin configuration for daily bonus amounts"""
    __tablename__ = "daily_bonus_config"
    
    config_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rank_1_amount = Column(Float, default=100.0)  # 1st place daily bonus
    rank_2_amount = Column(Float, default=50.0)   # 2nd place daily bonus
    rank_3_amount = Column(Float, default=25.0)   # 3rd place daily bonus
    currency = Column(String, default="PI")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
