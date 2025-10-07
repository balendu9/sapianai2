from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class SpinWheel(Base):
    __tablename__ = "spin_wheels"
    
    wheel_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    max_spins_per_day = Column(Integer, default=3)
    spin_cost = Column(Float, default=0.0)  # Cost in Pi tokens
    prizes = Column(JSON, nullable=False, default=list)  # List of prizes with probabilities
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SpinAttempt(Base):
    __tablename__ = "spin_attempts"
    
    attempt_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  # Pi Network user ID
    wheel_id = Column(String, ForeignKey("spin_wheels.wheel_id"), nullable=False)
    prize_won = Column(JSON, nullable=False)  # Details of the prize won
    spin_cost = Column(Float, default=0.0)
    input_reward = Column(Integer, default=0)  # Inputs earned from spin
    pi_reward = Column(Float, default=0.0)  # Pi tokens earned from spin
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    wheel = relationship("SpinWheel")
