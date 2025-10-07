from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REWARD = "reward"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class UserWallet(Base):
    __tablename__ = "user_wallets"
    
    wallet_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True)  # Pi Network user ID
    balance = Column(Float, default=0.0, nullable=False)  # Available balance for withdrawal
    total_earned = Column(Float, default=0.0, nullable=False)  # Total ever earned
    total_withdrawn = Column(Float, default=0.0, nullable=False)  # Total withdrawn
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("WalletTransaction", back_populates="wallet")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    transaction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_id = Column(String, ForeignKey("user_wallets.wallet_id"), nullable=False)
    user_id = Column(String, nullable=False)  # Pi Network user ID
    transaction_type = Column(String, nullable=False)  # 'deposit', 'withdrawal', 'reward'
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    status = Column(String, default="pending")  # 'pending', 'completed', 'failed', 'cancelled'
    pi_transaction_id = Column(String)  # Pi Network transaction ID for withdrawals
    quest_id = Column(String)  # Associated quest for rewards
    description = Column(Text)
    transaction_metadata = Column(JSON)  # Additional transaction data
    created_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime)
    
    # Relationships
    wallet = relationship("UserWallet", back_populates="transactions")
