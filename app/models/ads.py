from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timedelta
import uuid

class AdReward(Base):
    """Ad reward tracking and verification"""
    __tablename__ = "ad_rewards"
    
    reward_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False, index=True)
    ad_provider = Column(String, nullable=False)  # google, unity, ironSource, etc.
    ad_unit_id = Column(String, nullable=False)  # Ad unit identifier
    reward_amount = Column(Float, default=1.0)  # Credits earned
    currency = Column(String, default="credits")
    status = Column(String, default="pending")  # pending, verified, completed, failed
    verification_data = Column(JSON)  # Ad provider verification data
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    
    # Relationship to quest
    quest = relationship("Quest", back_populates="ad_rewards")

class AdConfig(Base):
    """Ad configuration and limits"""
    __tablename__ = "ad_config"
    
    config_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ad_provider = Column(String, nullable=False)  # google, unity, etc.
    ad_unit_id = Column(String, nullable=False)
    reward_per_ad = Column(Float, default=1.0)  # Credits per ad
    daily_limit_per_user = Column(Integer, default=10)  # Max ads per user per day
    cooldown_minutes = Column(Integer, default=5)  # Cooldown between ads
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdVerification(Base):
    """Ad verification tracking"""
    __tablename__ = "ad_verifications"
    
    verification_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    ad_provider = Column(String, nullable=False)
    ad_unit_id = Column(String, nullable=False)
    verification_token = Column(String, nullable=False)  # Unique token for verification
    status = Column(String, default="pending")  # pending, verified, expired, failed
    verification_data = Column(JSON)  # Provider-specific verification data
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
