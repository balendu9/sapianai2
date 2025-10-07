from sqlalchemy.orm import Session
from app.models.global_leaderboard import GlobalLeaderboard, GlobalDailyBonus, DailyBonusConfig
from app.models.participant import QuestParticipant
from app.models.quest import Quest
from app.models.wallet import UserWallet, WalletTransaction
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class GlobalLeaderboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def update_global_leaderboard(self) -> Dict[str, Any]:
        """Update global leaderboard with all users' average scores"""
        try:
            # Get all users with their quest participation data
            user_scores = self.db.query(
                QuestParticipant.user_id,
                QuestParticipant.username,
                func.sum(QuestParticipant.score).label('total_score'),
                func.count(QuestParticipant.quest_id).label('quests_participated')
            ).group_by(
                QuestParticipant.user_id, QuestParticipant.username
            ).all()
            
            # Clear existing global leaderboard
            self.db.query(GlobalLeaderboard).delete()
            
            # Create new global leaderboard entries
            global_entries = []
            for user_data in user_scores:
                average_score = user_data.total_score / user_data.quests_participated if user_data.quests_participated > 0 else 0
                
                global_entry = GlobalLeaderboard(
                    user_id=user_data.user_id,
                    username=user_data.username,
                    total_score=user_data.total_score,
                    quests_participated=user_data.quests_participated,
                    average_score=average_score,
                    last_updated=datetime.utcnow()
                )
                global_entries.append(global_entry)
                self.db.add(global_entry)
            
            self.db.commit()
            
            # Update ranks
            self._update_global_ranks()
            
            logger.info(f"Updated global leaderboard with {len(global_entries)} users")
            return {
                "success": True,
                "users_updated": len(global_entries),
                "message": "Global leaderboard updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to update global leaderboard: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _update_global_ranks(self):
        """Update ranks for global leaderboard"""
        try:
            # Get all users ordered by average score
            users = self.db.query(GlobalLeaderboard).order_by(
                desc(GlobalLeaderboard.average_score)
            ).all()
            
            # Update ranks
            for rank, user in enumerate(users, 1):
                user.rank = rank
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Failed to update global ranks: {str(e)}")
            self.db.rollback()
    
    def get_global_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get global leaderboard"""
        try:
            users = self.db.query(GlobalLeaderboard).order_by(
                desc(GlobalLeaderboard.average_score)
            ).limit(limit).all()
            
            leaderboard = []
            for user in users:
                leaderboard.append({
                    "rank": user.rank,
                    "user_id": user.user_id,
                    "username": user.username,
                    "average_score": round(user.average_score, 2),
                    "total_score": user.total_score,
                    "quests_participated": user.quests_participated,
                    "last_updated": user.last_updated.isoformat()
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Failed to get global leaderboard: {str(e)}")
            return []
    
    def process_daily_bonuses(self) -> Dict[str, Any]:
        """Process daily bonuses for top 3 global leaderboard users"""
        try:
            # Get bonus configuration
            config = self.db.query(DailyBonusConfig).filter(
                DailyBonusConfig.is_active == True
            ).first()
            
            if not config:
                return {"success": False, "error": "No active bonus configuration found"}
            
            # Get top 3 users
            top_users = self.db.query(GlobalLeaderboard).filter(
                GlobalLeaderboard.rank <= 3
            ).order_by(GlobalLeaderboard.rank).all()
            
            if len(top_users) < 3:
                return {"success": False, "error": "Not enough users in global leaderboard"}
            
            # Check if bonuses already processed today
            today = datetime.utcnow().date()
            existing_bonuses = self.db.query(GlobalDailyBonus).filter(
                func.date(GlobalDailyBonus.bonus_date) == today
            ).count()
            
            if existing_bonuses > 0:
                return {"success": False, "error": "Daily bonuses already processed today"}
            
            # Process bonuses for top 3
            bonus_amounts = {
                1: config.rank_1_amount,
                2: config.rank_2_amount,
                3: config.rank_3_amount
            }
            
            bonuses_created = []
            for user in top_users:
                # Create bonus record
                bonus = GlobalDailyBonus(
                    user_id=user.user_id,
                    rank=user.rank,
                    amount=bonus_amounts[user.rank],
                    currency=config.currency,
                    status="pending"
                )
                self.db.add(bonus)
                
                # Update user's wallet balance
                self._update_user_balance(
                    user.user_id, 
                    bonus_amounts[user.rank], 
                    f"Daily bonus for rank {user.rank}"
                )
                
                # Mark bonus as completed
                bonus.status = "completed"
                bonus.completed_at = datetime.utcnow()
                
                bonuses_created.append({
                    "user_id": user.user_id,
                    "username": user.username,
                    "rank": user.rank,
                    "amount": bonus_amounts[user.rank],
                    "currency": config.currency
                })
            
            self.db.commit()
            
            logger.info(f"Processed daily bonuses for {len(bonuses_created)} users")
            return {
                "success": True,
                "bonuses_created": len(bonuses_created),
                "bonuses": bonuses_created
            }
            
        except Exception as e:
            logger.error(f"Failed to process daily bonuses: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _update_user_balance(self, user_id: str, amount: float, description: str):
        """Update user's wallet balance with bonus amount"""
        try:
            # Get or create user wallet
            user_wallet = self.db.query(UserWallet).filter(
                UserWallet.user_id == user_id
            ).first()
            
            if not user_wallet:
                user_wallet = UserWallet(
                    user_id=user_id,
                    balance=0.0,
                    currency="PI"
                )
                self.db.add(user_wallet)
                self.db.flush()
            
            # Update balance
            user_wallet.balance += amount
            
            # Create transaction record
            transaction = WalletTransaction(
                wallet_id=user_wallet.wallet_id,
                transaction_type="daily_bonus",
                amount=amount,
                balance_before=user_wallet.balance - amount,
                balance_after=user_wallet.balance,
                description=description,
                transaction_metadata={
                    "bonus_type": "daily_global_leaderboard",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            self.db.add(transaction)
            
            logger.info(f"Updated user {user_id} balance: +{amount} (new balance: {user_wallet.balance})")
            
        except Exception as e:
            logger.error(f"Failed to update user balance: {str(e)}")
            raise e
    
    def set_bonus_config(self, rank_1_amount: float, rank_2_amount: float, rank_3_amount: float, currency: str = "PI") -> Dict[str, Any]:
        """Set daily bonus configuration (admin function)"""
        try:
            # Deactivate existing config
            self.db.query(DailyBonusConfig).update({"is_active": False})
            
            # Create new config
            config = DailyBonusConfig(
                rank_1_amount=rank_1_amount,
                rank_2_amount=rank_2_amount,
                rank_3_amount=rank_3_amount,
                currency=currency,
                is_active=True
            )
            self.db.add(config)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Daily bonus configuration updated",
                "config": {
                    "rank_1_amount": rank_1_amount,
                    "rank_2_amount": rank_2_amount,
                    "rank_3_amount": rank_3_amount,
                    "currency": currency
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to set bonus config: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_bonus_config(self) -> Dict[str, Any]:
        """Get current bonus configuration"""
        try:
            config = self.db.query(DailyBonusConfig).filter(
                DailyBonusConfig.is_active == True
            ).first()
            
            if not config:
                return {
                    "success": False,
                    "error": "No active bonus configuration found"
                }
            
            return {
                "success": True,
                "config": {
                    "rank_1_amount": config.rank_1_amount,
                    "rank_2_amount": config.rank_2_amount,
                    "rank_3_amount": config.rank_3_amount,
                    "currency": config.currency,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get bonus config: {str(e)}")
            return {"success": False, "error": str(e)}
