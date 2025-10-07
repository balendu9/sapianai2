from sqlalchemy.orm import Session
from app.models.credits import UserCredits, CreditTransaction
from app.models.quest import Quest
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import uuid

class CreditsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_credits(self, user_id: str, quest_id: str) -> Optional[UserCredits]:
        """Get user's credits for a specific quest"""
        return self.db.query(UserCredits).filter(
            UserCredits.user_id == user_id,
            UserCredits.quest_id == quest_id
        ).first()
    
    def create_user_credits(self, user_id: str, quest_id: str, daily_credits: int = 1) -> UserCredits:
        """Create initial credits for a user in a quest"""
        user_credits = UserCredits(
            user_id=user_id,
            quest_id=quest_id,
            daily_credits=daily_credits,
            credits_used_today=0,
            last_reset_date=datetime.utcnow()
        )
        self.db.add(user_credits)
        self.db.commit()
        self.db.refresh(user_credits)
        return user_credits
    
    def reset_daily_credits(self, user_id: str, quest_id: str) -> UserCredits:
        """Reset daily credits for a user (called at UTC 00:00)"""
        user_credits = self.get_user_credits(user_id, quest_id)
        
        if not user_credits:
            # Create new credits if they don't exist
            return self.create_user_credits(user_id, quest_id)
        
        # Check if credits need to be reset (new day)
        now = datetime.utcnow()
        if user_credits.last_reset_date.date() < now.date():
            # Reset credits for new day
            user_credits.credits_used_today = 0
            user_credits.last_reset_date = now
            self.db.commit()
            
            # Log the reset transaction
            self._log_credit_transaction(
                user_id=user_id,
                quest_id=quest_id,
                transaction_type="daily_reset",
                amount=user_credits.daily_credits,
                balance_before=0,
                balance_after=user_credits.daily_credits,
                description=f"Daily credits reset: {user_credits.daily_credits} credits"
            )
        
        return user_credits
    
    def can_send_message(self, user_id: str, quest_id: str) -> Dict[str, Any]:
        """Check if user can send a message (has credits)"""
        user_credits = self.get_user_credits(user_id, quest_id)
        
        if not user_credits:
            # Create credits for new user
            user_credits = self.create_user_credits(user_id, quest_id)
        
        # Reset credits if needed
        user_credits = self.reset_daily_credits(user_id, quest_id)
        
        available_credits = user_credits.daily_credits - user_credits.credits_used_today
        can_send = available_credits > 0
        
        return {
            "can_send": can_send,
            "available_credits": available_credits,
            "daily_credits": user_credits.daily_credits,
            "used_today": user_credits.credits_used_today,
            "next_reset": self._get_next_reset_time()
        }
    
    def spend_credit(self, user_id: str, quest_id: str, description: str = "Message sent") -> Dict[str, Any]:
        """Spend a credit for sending a message"""
        user_credits = self.get_user_credits(user_id, quest_id)
        
        if not user_credits:
            return {"success": False, "error": "No credits found for user"}
        
        # Reset credits if needed
        user_credits = self.reset_daily_credits(user_id, quest_id)
        
        # Check if user has credits
        if user_credits.credits_used_today >= user_credits.daily_credits:
            return {"success": False, "error": "No credits available"}
        
        # Spend the credit
        user_credits.credits_used_today += 1
        self.db.commit()
        
        # Log the transaction
        self._log_credit_transaction(
            user_id=user_id,
            quest_id=quest_id,
            transaction_type="spent",
            amount=-1,
            balance_before=user_credits.daily_credits - user_credits.credits_used_today + 1,
            balance_after=user_credits.daily_credits - user_credits.credits_used_today,
            description=description
        )
        
        return {
            "success": True,
            "available_credits": user_credits.daily_credits - user_credits.credits_used_today,
            "used_today": user_credits.credits_used_today
        }
    
    def add_credits(self, user_id: str, quest_id: str, amount: int, source: str = "purchase", description: str = None) -> Dict[str, Any]:
        """Add credits to user (from purchase or ad reward)"""
        user_credits = self.get_user_credits(user_id, quest_id)
        
        if not user_credits:
            user_credits = self.create_user_credits(user_id, quest_id)
        
        # Add credits to daily allowance
        user_credits.daily_credits += amount
        self.db.commit()
        
        # Log the transaction
        self._log_credit_transaction(
            user_id=user_id,
            quest_id=quest_id,
            transaction_type=source,
            amount=amount,
            balance_before=user_credits.daily_credits - amount,
            balance_after=user_credits.daily_credits,
            description=description or f"Credits added from {source}"
        )
        
        return {
            "success": True,
            "daily_credits": user_credits.daily_credits,
            "available_credits": user_credits.daily_credits - user_credits.credits_used_today
        }
    
    def set_quest_credit_limit(self, quest_id: str, daily_credits: int) -> bool:
        """Set daily credit limit for a quest (admin function)"""
        try:
            # Update all existing user credits for this quest
            self.db.query(UserCredits).filter(
                UserCredits.quest_id == quest_id
            ).update({"daily_credits": daily_credits})
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def _log_credit_transaction(
        self,
        user_id: str,
        quest_id: str,
        transaction_type: str,
        amount: int,
        balance_before: int,
        balance_after: int,
        description: str
    ):
        """Log a credit transaction"""
        transaction = CreditTransaction(
            user_id=user_id,
            quest_id=quest_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            transaction_metadata=json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "transaction_id": str(uuid.uuid4())
            })
        )
        self.db.add(transaction)
        self.db.commit()
    
    def _get_next_reset_time(self) -> str:
        """Get next credit reset time (UTC 00:00)"""
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        next_reset = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        return next_reset.isoformat()
    
    def get_quest_credit_stats(self, quest_id: str) -> Dict[str, Any]:
        """Get credit statistics for a quest"""
        total_users = self.db.query(UserCredits).filter(
            UserCredits.quest_id == quest_id
        ).count()
        
        active_users = self.db.query(UserCredits).filter(
            UserCredits.quest_id == quest_id,
            UserCredits.credits_used_today < UserCredits.daily_credits
        ).count()
        
        total_credits_used = self.db.query(UserCredits).filter(
            UserCredits.quest_id == quest_id
        ).with_entities(UserCredits.credits_used_today).all()
        
        total_used = sum(row[0] for row in total_credits_used)
        
        return {
            "quest_id": quest_id,
            "total_users": total_users,
            "active_users": active_users,
            "total_credits_used": total_used,
            "next_reset": self._get_next_reset_time()
        }
