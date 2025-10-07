from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class TreasuryInfo(BaseModel):
    total_treasury: float
    total_prize_pools: float
    rewards_distributed: float
    recent_transactions: List[Dict[str, Any]]

class TransactionHistory(BaseModel):
    transaction_id: str
    user_id: str
    type: str  # contribution, reward, etc.
    amount: float
    description: str
    created_at: datetime
