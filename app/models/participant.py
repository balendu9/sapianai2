from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class QuestParticipant(Base):
    __tablename__ = "quest_participants"
    
    qp_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    score = Column(Integer, default=0)
    reply_log = Column(JSON, default=list)  # History of replies with scores
    joined_at = Column(DateTime, default=func.now())
    last_reply_at = Column(DateTime)
    last_hint_sent = Column(DateTime)
    
    # Relationships
    quest = relationship("Quest", back_populates="participants")
    user = relationship("User", back_populates="participants")
