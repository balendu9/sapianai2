from sqlalchemy import Column, String, Date, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class QuestInput(Base):
    __tablename__ = "quest_inputs"
    
    input_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    input_date = Column(Date, nullable=False)
    input_type = Column(String(20), nullable=False)  # free, paid, ad, spin
    count = Column(Integer, default=0)
    payment_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
