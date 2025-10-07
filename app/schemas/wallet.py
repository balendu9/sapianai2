from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REWARD = "reward"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WalletResponse(BaseModel):
    wallet_id: str
    user_id: str
    balance: float
    total_earned: float
    total_withdrawn: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WalletTransactionResponse(BaseModel):
    transaction_id: str
    wallet_id: str
    user_id: str
    transaction_type: TransactionType
    amount: float
    balance_before: float
    balance_after: float
    status: TransactionStatus
    pi_transaction_id: Optional[str]
    quest_id: Optional[str]
    description: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class WithdrawalRequest(BaseModel):
    amount: float
    pi_user_id: str  # Pi Network user ID for withdrawal
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 10.50,
                "pi_user_id": "pi_user_12345"
            }
        }

class WithdrawalResponse(BaseModel):
    transaction_id: str
    amount: float
    status: TransactionStatus
    pi_transaction_id: Optional[str]
    message: str

class RewardDistribution(BaseModel):
    user_id: str
    quest_id: str
    amount: float
    percentage: float
    description: str

class WalletBalance(BaseModel):
    user_id: str
    balance: float
    total_earned: float
    total_withdrawn: float
    pending_withdrawals: float
