from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class QuestReward(Base):
    __tablename__ = "quest_rewards"
    
    reward_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    rank = Column(Integer, nullable=False)
    percent = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    distributed_at = Column(DateTime, default=func.now())
