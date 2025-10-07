from pydantic import BaseModel
from datetime import datetime, date

class BonusClaim(BaseModel):
    user_id: str

class BonusResponse(BaseModel):
    bonus_id: str
    user_id: str
    bonus_date: date
    reward_amount: float
    claimed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
