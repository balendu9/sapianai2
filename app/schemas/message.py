from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class MessageCreate(BaseModel):
    user_id: str
    user_message: str

class MessageResponse(BaseModel):
    message_id: str
    quest_id: str
    user_id: Optional[str]
    content: str
    score: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AIResponse(BaseModel):
    user_message: MessageResponse
    ai_message: MessageResponse
    score: int
    score_breakdown: Dict[str, Any]
    feedback: str
    total_score: int
