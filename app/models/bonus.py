from sqlalchemy import Column, String, Date, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class DailyBonus(Base):
    __tablename__ = "daily_bonus"
    
    bonus_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    bonus_date = Column(Date, nullable=False)
    reward_amount = Column(Float, default=0.0)
    claimed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
