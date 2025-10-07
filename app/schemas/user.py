from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    user_id: str  # Pi Network user ID - primary identifier
    username: Optional[str] = None  # Optional display name
    email: Optional[EmailStr] = None  # Optional email

class UserResponse(BaseModel):
    user_id: str
    username: Optional[str]
    email: Optional[str]
    created_at: datetime
    total_score: float
    quests_completed: int
    
    class Config:
        from_attributes = True
