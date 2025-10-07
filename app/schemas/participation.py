from pydantic import BaseModel
from datetime import datetime

class ParticipationCreate(BaseModel):
    user_id: str

class ParticipationResponse(BaseModel):
    qp_id: str
    quest_id: str
    user_id: str
    score: int
    joined_at: datetime
    
    class Config:
        from_attributes = True
