from sqlalchemy.orm import Session
from app.models.pool import QuestPool
from app.models.quest import Quest
from typing import Dict, Any

class PaymentSplitter:
    """Handles splitting user payments between treasury and user pool"""
    
    @staticmethod
    def split_payment(
        db: Session,
        quest_id: str,
        user_id: str,
        payment_amount: float,
        source: str = "user_payment"
    ) -> Dict[str, float]:
        """
        Split a user payment between treasury and user pool
        
        Args:
            db: Database session
            quest_id: Quest ID
            user_id: User ID
            payment_amount: Amount paid by user
            source: Payment source (user_payment, admin_fund, bonus_event)
            
        Returns:
            Dict with split amounts
        """
        # Get quest to retrieve distribution rules
        quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        
        # Get treasury and user percentages from quest distribution rules
        distribution_rules = quest.distribution_rules or {}
        treasury_percentage = distribution_rules.get("treasury_percentage", 10.0)
        user_percentage = distribution_rules.get("user_percentage", 90.0)
        
        # Calculate split amounts
        treasury_amount = payment_amount * (treasury_percentage / 100)
        pool_amount = payment_amount * (user_percentage / 100)
        
        # Create quest pool record
        pool_record = QuestPool(
            quest_id=quest_id,
            source=source,
            amount=payment_amount,
            split_to_treasury=treasury_amount,
            split_to_pool=pool_amount
        )
        
        db.add(pool_record)
        db.commit()
        
        return {
            "total_amount": payment_amount,
            "treasury_amount": treasury_amount,
            "pool_amount": pool_amount,
            "treasury_percentage": treasury_percentage,
            "user_percentage": user_percentage
        }
    
    @staticmethod
    def get_quest_pool_totals(db: Session, quest_id: str) -> Dict[str, float]:
        """Get total treasury and pool amounts for a quest"""
        
        # Calculate totals from quest_pools table
        treasury_total = db.query(
            db.func.sum(QuestPool.split_to_treasury)
        ).filter(QuestPool.quest_id == quest_id).scalar() or 0
        
        pool_total = db.query(
            db.func.sum(QuestPool.split_to_pool)
        ).filter(QuestPool.quest_id == quest_id).scalar() or 0
        
        return {
            "quest_id": quest_id,
            "total_treasury": treasury_total,
            "total_pool": pool_total,
            "total_collected": treasury_total + pool_total
        }
    
    @staticmethod
    def get_platform_totals(db: Session) -> Dict[str, float]:
        """Get total treasury and pool amounts across all quests"""
        
        # Calculate platform-wide totals
        treasury_total = db.query(
            db.func.sum(QuestPool.split_to_treasury)
        ).scalar() or 0
        
        pool_total = db.query(
            db.func.sum(QuestPool.split_to_pool)
        ).scalar() or 0
        
        return {
            "platform_treasury": treasury_total,
            "platform_pools": pool_total,
            "platform_total": treasury_total + pool_total
        }
