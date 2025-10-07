from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class QuestPool(Base):
    __tablename__ = "quest_pools"
    
    pool_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False)
    source = Column(String(50), nullable=False)  # user_payment, admin_fund, bonus_event
    amount = Column(Float, nullable=False)
    split_to_pool = Column(Float, nullable=False)
    split_to_treasury = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
