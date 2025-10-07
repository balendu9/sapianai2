from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreditStatus(BaseModel):
    quest_id: str
    user_id: str
    can_send: bool
    available_credits: int
    daily_credits: int
    used_today: int
    next_reset: str

class CreditPurchase(BaseModel):
    amount: int
    payment_method: Optional[str] = "pi"  # pi, ton, usdt, etc.
    transaction_id: Optional[str] = None

class CreditResponse(BaseModel):
    success: bool
    message: str
    available_credits: int
    daily_credits: int

class CreditTransaction(BaseModel):
    transaction_id: str
    user_id: str
    quest_id: str
    transaction_type: str
    amount: int
    balance_before: int
    balance_after: int
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
