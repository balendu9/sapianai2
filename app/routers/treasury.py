from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.pool import QuestPool
from app.models.reward import QuestReward
from app.schemas.treasury import TreasuryInfo, TransactionHistory

router = APIRouter()

@router.get("/", response_model=TreasuryInfo)
async def get_treasury_info(db: Session = Depends(get_db)):
    """Get treasury info (balances, reserves, inflows/outflows)"""
    
    # Calculate total treasury from all quest pools
    treasury_total = db.query(func.sum(QuestPool.split_to_treasury)).scalar() or 0
    
    # Calculate total prize pools
    prize_pools_total = db.query(func.sum(QuestPool.split_to_pool)).scalar() or 0
    
    # Calculate total rewards distributed
    rewards_distributed = db.query(func.sum(QuestReward.amount)).scalar() or 0
    
    # Get recent transactions (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_transactions = db.query(QuestPool).filter(
        QuestPool.created_at >= thirty_days_ago
    ).order_by(desc(QuestPool.created_at)).limit(50).all()
    
    return TreasuryInfo(
        total_treasury=treasury_total,
        total_prize_pools=prize_pools_total,
        rewards_distributed=rewards_distributed,
        recent_transactions=[
            {
                "pool_id": transaction.pool_id,
                "quest_id": transaction.quest_id,
                "source": transaction.source,
                "amount": transaction.amount,
                "split_to_treasury": transaction.split_to_treasury,
                "split_to_pool": transaction.split_to_pool,
                "created_at": transaction.created_at
            }
            for transaction in recent_transactions
        ]
    )

@router.get("/transactions/{user_id}", response_model=List[TransactionHistory])
async def get_user_transaction_history(
    user_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get user's transaction history"""
    
    # Get user's quest pool contributions (through quest participation)
    from app.models.participant import QuestParticipant
    
    user_quest_ids = db.query(QuestParticipant.quest_id).filter(
        QuestParticipant.user_id == user_id
    ).subquery()
    
    pool_contributions = db.query(QuestPool).filter(
        QuestPool.quest_id.in_(user_quest_ids)
    ).order_by(desc(QuestPool.created_at)).limit(limit).all()
    
    # Get user's rewards received
    rewards_received = db.query(QuestReward).filter(
        QuestReward.user_id == user_id
    ).order_by(desc(QuestReward.distributed_at)).limit(limit).all()
    
    transactions = []
    
    # Add pool contributions
    for contribution in pool_contributions:
        transactions.append(TransactionHistory(
            transaction_id=contribution.pool_id,
            user_id=user_id,
            type="contribution",
            amount=contribution.amount,
            description=f"Contribution to quest pool",
            created_at=contribution.created_at
        ))
    
    # Add rewards received
    for reward in rewards_received:
        transactions.append(TransactionHistory(
            transaction_id=reward.reward_id,
            user_id=user_id,
            type="reward",
            amount=reward.amount,
            description=f"Reward for rank {reward.rank} in quest",
            created_at=reward.distributed_at
        ))
    
    # Sort by date
    transactions.sort(key=lambda x: x.created_at, reverse=True)
    
    return transactions[:limit]
