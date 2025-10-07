from sqlalchemy.orm import Session
from app.models.ads import AdReward, AdConfig, AdVerification
from app.models.credits import UserCredits, CreditTransaction
from app.models.wallet import UserWallet, WalletTransaction
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class AdsService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_ad_verification(self, user_id: str, quest_id: str, ad_provider: str = "google") -> Dict[str, Any]:
        """Create ad verification token for user"""
        try:
            # Check if user can watch ads (cooldown, daily limit)
            can_watch = self._can_user_watch_ad(user_id, quest_id)
            if not can_watch["can_watch"]:
                return can_watch
            
            # Get ad configuration
            ad_config = self.db.query(AdConfig).filter(
                and_(
                    AdConfig.ad_provider == ad_provider,
                    AdConfig.is_active == True
                )
            ).first()
            
            if not ad_config:
                return {"success": False, "error": "No active ad configuration found"}
            
            # Create verification token
            verification_token = str(uuid.uuid4())
            verification = AdVerification(
                user_id=user_id,
                ad_provider=ad_provider,
                ad_unit_id=ad_config.ad_unit_id,
                verification_token=verification_token,
                status="pending"
            )
            self.db.add(verification)
            self.db.commit()
            
            return {
                "success": True,
                "verification_token": verification_token,
                "ad_unit_id": ad_config.ad_unit_id,
                "reward_amount": ad_config.reward_per_ad,
                "expires_at": verification.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create ad verification: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def verify_ad_completion(self, verification_token: str, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify ad completion and reward user"""
        try:
            # Get verification record
            verification = self.db.query(AdVerification).filter(
                and_(
                    AdVerification.verification_token == verification_token,
                    AdVerification.status == "pending",
                    AdVerification.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not verification:
                return {"success": False, "error": "Invalid or expired verification token"}
            
            # Verify with ad provider (simplified - in real implementation, call provider API)
            is_valid = self._verify_with_provider(verification.ad_provider, verification_data)
            if not is_valid:
                verification.status = "failed"
                self.db.commit()
                return {"success": False, "error": "Ad verification failed"}
            
            # Mark verification as successful
            verification.status = "verified"
            verification.verified_at = datetime.utcnow()
            verification.verification_data = verification_data
            
            # Create ad reward
            ad_reward = AdReward(
                user_id=verification.user_id,
                quest_id=verification.quest_id if hasattr(verification, 'quest_id') else None,
                ad_provider=verification.ad_provider,
                ad_unit_id=verification.ad_unit_id,
                reward_amount=1.0,  # Default 1 credit
                status="verified"
            )
            self.db.add(ad_reward)
            
            # Reward user with credits
            reward_result = self._reward_user_credits(
                verification.user_id,
                quest_id=verification.quest_id if hasattr(verification, 'quest_id') else None,
                amount=1.0,
                source="ad_reward"
            )
            
            if reward_result["success"]:
                ad_reward.status = "completed"
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "Ad reward claimed successfully",
                    "credits_earned": 1.0,
                    "new_balance": reward_result.get("available_credits", 0)
                }
            else:
                ad_reward.status = "failed"
                self.db.commit()
                return {"success": False, "error": "Failed to reward credits"}
                
        except Exception as e:
            logger.error(f"Failed to verify ad completion: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _can_user_watch_ad(self, user_id: str, quest_id: str) -> Dict[str, Any]:
        """Check if user can watch ads (cooldown, daily limit)"""
        try:
            # Get ad configuration
            ad_config = self.db.query(AdConfig).filter(AdConfig.is_active == True).first()
            if not ad_config:
                return {"can_watch": False, "error": "No ad configuration found"}
            
            # Check daily limit
            today = datetime.utcnow().date()
            ads_today = self.db.query(AdReward).filter(
                and_(
                    AdReward.user_id == user_id,
                    func.date(AdReward.created_at) == today,
                    AdReward.status == "completed"
                )
            ).count()
            
            if ads_today >= ad_config.daily_limit_per_user:
                return {
                    "can_watch": False, 
                    "error": f"Daily ad limit reached ({ad_config.daily_limit_per_user})",
                    "ads_watched_today": ads_today,
                    "daily_limit": ad_config.daily_limit_per_user
                }
            
            # Check cooldown
            last_ad = self.db.query(AdReward).filter(
                and_(
                    AdReward.user_id == user_id,
                    AdReward.status == "completed"
                )
            ).order_by(AdReward.created_at.desc()).first()
            
            if last_ad:
                cooldown_end = last_ad.created_at + timedelta(minutes=ad_config.cooldown_minutes)
                if datetime.utcnow() < cooldown_end:
                    remaining_minutes = int((cooldown_end - datetime.utcnow()).total_seconds() / 60)
                    return {
                        "can_watch": False,
                        "error": f"Ad cooldown active. Try again in {remaining_minutes} minutes",
                        "cooldown_remaining": remaining_minutes
                    }
            
            return {
                "can_watch": True,
                "ads_watched_today": ads_today,
                "daily_limit": ad_config.daily_limit_per_user,
                "cooldown_minutes": ad_config.cooldown_minutes
            }
            
        except Exception as e:
            logger.error(f"Failed to check ad eligibility: {str(e)}")
            return {"can_watch": False, "error": str(e)}
    
    def _verify_with_provider(self, ad_provider: str, verification_data: Dict[str, Any]) -> bool:
        """Verify ad completion with provider (simplified implementation)"""
        # In real implementation, this would call the actual ad provider API
        # For now, we'll simulate verification
        
        if ad_provider == "google":
            # Simulate Google AdMob verification
            return verification_data.get("ad_loaded", False) and verification_data.get("ad_completed", False)
        elif ad_provider == "unity":
            # Simulate Unity Ads verification
            return verification_data.get("placement_id") and verification_data.get("rewarded", False)
        else:
            # Default verification
            return verification_data.get("verified", False)
    
    def _reward_user_credits(self, user_id: str, quest_id: str, amount: float, source: str) -> Dict[str, Any]:
        """Reward user with credits for watching ad"""
        try:
            from app.services.credits_service import CreditsService
            
            credits_service = CreditsService(self.db)
            
            # Add credits to user
            result = credits_service.add_credits(
                user_id=user_id,
                quest_id=quest_id,
                amount=amount,
                source=source,
                description=f"Credits earned from watching ad"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to reward user credits: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_ad_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's ad watching statistics"""
        try:
            today = datetime.utcnow().date()
            
            # Get today's ads
            ads_today = self.db.query(AdReward).filter(
                and_(
                    AdReward.user_id == user_id,
                    func.date(AdReward.created_at) == today,
                    AdReward.status == "completed"
                )
            ).count()
            
            # Get total ads
            total_ads = self.db.query(AdReward).filter(
                and_(
                    AdReward.user_id == user_id,
                    AdReward.status == "completed"
                )
            ).count()
            
            # Get ad configuration
            ad_config = self.db.query(AdConfig).filter(AdConfig.is_active == True).first()
            
            return {
                "success": True,
                "ads_watched_today": ads_today,
                "total_ads_watched": total_ads,
                "daily_limit": ad_config.daily_limit_per_user if ad_config else 10,
                "remaining_today": (ad_config.daily_limit_per_user - ads_today) if ad_config else (10 - ads_today),
                "cooldown_minutes": ad_config.cooldown_minutes if ad_config else 5
            }
            
        except Exception as e:
            logger.error(f"Failed to get user ad stats: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def set_ad_config(self, ad_provider: str, ad_unit_id: str, reward_per_ad: float, 
                     daily_limit: int, cooldown_minutes: int) -> Dict[str, Any]:
        """Set ad configuration (admin function)"""
        try:
            # Deactivate existing configs
            self.db.query(AdConfig).update({"is_active": False})
            
            # Create new config
            config = AdConfig(
                ad_provider=ad_provider,
                ad_unit_id=ad_unit_id,
                reward_per_ad=reward_per_ad,
                daily_limit_per_user=daily_limit,
                cooldown_minutes=cooldown_minutes,
                is_active=True
            )
            self.db.add(config)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Ad configuration updated",
                "config": {
                    "ad_provider": ad_provider,
                    "ad_unit_id": ad_unit_id,
                    "reward_per_ad": reward_per_ad,
                    "daily_limit_per_user": daily_limit,
                    "cooldown_minutes": cooldown_minutes
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to set ad config: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
