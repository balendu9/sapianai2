from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Leaderboard(Base):
    __tablename__ = "leaderboards"
    
    leaderboard_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quest_id = Column(String, ForeignKey("quests.quest_id"))  # null for global
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    score = Column(Integer, default=0)
    rank = Column(Integer)
    updated_at = Column(DateTime, default=func.now())
