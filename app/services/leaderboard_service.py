from sqlalchemy.orm import Session
from app.models.quest import Quest, QuestStatus
from app.models.participant import QuestParticipant
from app.models.leaderboard import Leaderboard
from app.models.pool import QuestPool
from app.models.reward import QuestReward
from sqlalchemy import func, desc
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class LeaderboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def update_leaderboard(self, quest_id: str) -> Dict[str, Any]:
        """Update leaderboard for a quest and check for 100% completion"""
        try:
            # Get quest
            quest = self.db.query(Quest).filter(Quest.quest_id == quest_id).first()
            if not quest:
                return {"success": False, "error": "Quest not found"}
            
            # Check if quest is already ended
            if quest.status == QuestStatus.ENDED:
                return {"success": True, "message": "Quest already ended", "quest_ended": True}
            
            # Get all participants with their scores
            participants = self.db.query(QuestParticipant).filter(
                QuestParticipant.quest_id == quest_id
            ).order_by(desc(QuestParticipant.score), QuestParticipant.last_reply_at).all()
            
            if not participants:
                return {"success": True, "message": "No participants found"}
            
            # Check for 100% completion
            max_score = max(p.score for p in participants) if participants else 0
            quest_ended = max_score >= 100
            
            if quest_ended:
                # End the quest
                quest.status = QuestStatus.ENDED
                quest.end_date = datetime.now()
                self.db.commit()
                
                # Process rewards for final leaderboard
                self._process_final_rewards(quest_id, participants)
                
                logger.info(f"Quest {quest_id} ended due to 100% completion by user with score {max_score}")
            
            # Update leaderboard
            self._update_leaderboard_entries(quest_id, participants)
            
            return {
                "success": True,
                "quest_ended": quest_ended,
                "max_score": max_score,
                "participant_count": len(participants),
                "leaderboard_updated": True
            }
            
        except Exception as e:
            logger.error(f"Failed to update leaderboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_leaderboard(self, quest_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get current leaderboard for a quest"""
        try:
            # Get leaderboard entries
            leaderboard_entries = self.db.query(Leaderboard).filter(
                Leaderboard.quest_id == quest_id
            ).order_by(desc(Leaderboard.score), Leaderboard.rank).limit(limit).all()
            
            leaderboard = []
            for entry in leaderboard_entries:
                leaderboard.append({
                    "rank": entry.rank,
                    "user_id": entry.user_id,
                    "score": entry.score,
                    "username": entry.username,
                    "last_reply_at": entry.last_reply_at.isoformat() if entry.last_reply_at else None,
                    "total_messages": entry.total_messages
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {str(e)}")
            return []
    
    def _update_leaderboard_entries(self, quest_id: str, participants: List[QuestParticipant]):
        """Update leaderboard entries based on current participant scores"""
        try:
            # Clear existing leaderboard entries
            self.db.query(Leaderboard).filter(Leaderboard.quest_id == quest_id).delete()
            
            # Create new leaderboard entries
            for rank, participant in enumerate(participants, 1):
                leaderboard_entry = Leaderboard(
                    quest_id=quest_id,
                    user_id=participant.user_id,
                    username=participant.username,
                    score=participant.score,
                    rank=rank,
                    last_reply_at=participant.last_reply_at,
                    total_messages=len(participant.reply_log) if participant.reply_log else 0
                )
                self.db.add(leaderboard_entry)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update leaderboard entries: {str(e)}")
            self.db.rollback()
    
    def _process_final_rewards(self, quest_id: str, participants: List[QuestParticipant]):
        """Process final rewards when quest ends"""
        try:
            # Get quest distribution rules
            quest = self.db.query(Quest).filter(Quest.quest_id == quest_id).first()
            if not quest or not quest.distribution_rules:
                return
            
            distribution_rules = quest.distribution_rules
            rank_distribution = distribution_rules.get("rank_distribution", {})
            
            # Calculate total quest pool
            initial_pool = distribution_rules.get("initial_pool", 0)
            user_pool_contributions = self.db.query(func.sum(QuestPool.split_to_pool)).filter(
                QuestPool.quest_id == quest_id
            ).scalar() or 0
            
            total_quest_pool = initial_pool + user_pool_contributions
            
            # Calculate rewards for each range
            reward_percentages = self._calculate_range_rewards(participants, rank_distribution)
            
            # Process rewards based on final leaderboard
            for rank, participant in enumerate(participants, 1):
                reward_percentage = reward_percentages.get(rank, 0.0)
                if reward_percentage > 0:
                    reward_amount = total_quest_pool * (reward_percentage / 100)
                    
                    # Update user's wallet balance automatically
                    self._update_user_balance(participant.user_id, reward_amount, quest_id)
                    
                    # Create reward record
                    reward = QuestReward(
                        quest_id=quest_id,
                        user_id=participant.user_id,
                        amount=reward_amount,
                        rank=rank,
                        percentage=reward_percentage,
                        status="completed"  # Automatically completed
                    )
                    self.db.add(reward)
            
            self.db.commit()
            logger.info(f"Processed final rewards for quest {quest_id} - Total pool: {total_quest_pool}")
            
        except Exception as e:
            logger.error(f"Failed to process final rewards: {str(e)}")
            self.db.rollback()
    
    def _calculate_range_rewards(self, participants: List[QuestParticipant], rank_distribution: Dict[str, Any]) -> Dict[int, float]:
        """Calculate reward percentages for each rank based on actual participants in ranges"""
        # Default distribution if not specified
        default_distribution = {
            "1": 50.0,     # 1st place gets 50%
            "2-13": 40.0,  # 2nd-13th place split 40% among actual participants
            "14-50": 10.0  # 14th-50th place split 10% among actual participants
        }
        
        # Use provided distribution or default
        distribution = rank_distribution or default_distribution
        
        # Initialize reward percentages for each rank
        reward_percentages = {}
        
        # Process each distribution rule
        for key, total_percentage in distribution.items():
            if "-" in key:
                # Range format (e.g., "2-13": 40.0)
                start, end = map(int, key.split("-"))
                
                # Count actual participants in this range
                participants_in_range = []
                for rank, participant in enumerate(participants, 1):
                    if start <= rank <= end:
                        participants_in_range.append(rank)
                
                # If there are participants in this range, split the percentage among them
                if participants_in_range:
                    individual_percentage = total_percentage / len(participants_in_range)
                    for rank in participants_in_range:
                        reward_percentages[rank] = individual_percentage
                        
                    logger.info(f"Range {key}: {len(participants_in_range)} participants, {total_percentage}% split = {individual_percentage}% each")
                        
            elif key.isdigit():
                # Exact rank match (e.g., "1": 50.0)
                rank = int(key)
                if rank <= len(participants):
                    reward_percentages[rank] = total_percentage
                    logger.info(f"Rank {rank}: {total_percentage}%")
        
        return reward_percentages
    
    def _update_user_balance(self, user_id: str, reward_amount: float, quest_id: str):
        """Update user's wallet balance with reward amount"""
        try:
            from app.models.wallet import UserWallet, WalletTransaction
            from app.models.user import User
            
            # Get or create user wallet
            user_wallet = self.db.query(UserWallet).filter(
                UserWallet.user_id == user_id
            ).first()
            
            if not user_wallet:
                # Create new wallet for user
                user_wallet = UserWallet(
                    user_id=user_id,
                    balance=0.0,
                    currency="PI"  # Default currency
                )
                self.db.add(user_wallet)
                self.db.flush()  # Get the wallet_id
            
            # Update balance
            user_wallet.balance += reward_amount
            
            # Create transaction record
            transaction = WalletTransaction(
                wallet_id=user_wallet.wallet_id,
                transaction_type="reward",
                amount=reward_amount,
                balance_before=user_wallet.balance - reward_amount,
                balance_after=user_wallet.balance,
                description=f"Quest reward from quest {quest_id}",
                transaction_metadata={
                    "quest_id": quest_id,
                    "reward_type": "quest_completion",
                    "timestamp": datetime.now().isoformat()
                }
            )
            self.db.add(transaction)
            
            logger.info(f"Updated user {user_id} balance: +{reward_amount} (new balance: {user_wallet.balance})")
            
        except Exception as e:
            logger.error(f"Failed to update user balance: {str(e)}")
            raise e
    
    def get_quest_status(self, quest_id: str) -> Dict[str, Any]:
        """Get current quest status and leaderboard info"""
        try:
            quest = self.db.query(Quest).filter(Quest.quest_id == quest_id).first()
            if not quest:
                return {"success": False, "error": "Quest not found"}
            
            # Get leaderboard
            leaderboard = self.get_leaderboard(quest_id, limit=10)
            
            # Get participant count
            participant_count = self.db.query(QuestParticipant).filter(
                QuestParticipant.quest_id == quest_id
            ).count()
            
            # Get max score
            max_score = self.db.query(func.max(QuestParticipant.score)).filter(
                QuestParticipant.quest_id == quest_id
            ).scalar() or 0
            
            return {
                "success": True,
                "quest_id": quest_id,
                "status": quest.status,
                "max_score": max_score,
                "participant_count": participant_count,
                "leaderboard": leaderboard,
                "quest_ended": quest.status == QuestStatus.ENDED
            }
            
        except Exception as e:
            logger.error(f"Failed to get quest status: {str(e)}")
            return {"success": False, "error": str(e)}
