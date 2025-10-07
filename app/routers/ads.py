from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ads_service import AdsService
from app.schemas.ads import AdVerificationRequest, AdVerificationResponse, AdStatsResponse, AdConfigRequest
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/verify", response_model=AdVerificationResponse)
async def create_ad_verification(
    user_id: str,
    quest_id: str,
    ad_provider: str = "google",
    db: Session = Depends(get_db)
):
    """Create ad verification token for user"""
    try:
        service = AdsService(db)
        result = service.create_ad_verification(user_id, quest_id, ad_provider)
        
        if result["success"]:
            return AdVerificationResponse(
                success=True,
                verification_token=result["verification_token"],
                ad_unit_id=result["ad_unit_id"],
                reward_amount=result["reward_amount"],
                expires_at=result["expires_at"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create ad verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create ad verification: {str(e)}")

@router.post("/complete", response_model=AdVerificationResponse)
async def verify_ad_completion(
    verification_request: AdVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify ad completion and reward user"""
    try:
        service = AdsService(db)
        result = service.verify_ad_completion(
            verification_request.verification_token,
            verification_request.verification_data
        )
        
        if result["success"]:
            return AdVerificationResponse(
                success=True,
                message=result["message"],
                credits_earned=result["credits_earned"],
                new_balance=result["new_balance"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify ad completion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify ad completion: {str(e)}")

@router.get("/stats/{user_id}", response_model=AdStatsResponse)
async def get_user_ad_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's ad watching statistics"""
    try:
        service = AdsService(db)
        result = service.get_user_ad_stats(user_id)
        
        if result["success"]:
            return AdStatsResponse(
                success=True,
                ads_watched_today=result["ads_watched_today"],
                total_ads_watched=result["total_ads_watched"],
                daily_limit=result["daily_limit"],
                remaining_today=result["remaining_today"],
                cooldown_minutes=result["cooldown_minutes"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user ad stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user ad stats: {str(e)}")

@router.post("/config")
async def set_ad_config(
    config: AdConfigRequest,
    db: Session = Depends(get_db)
):
    """Set ad configuration (admin function)"""
    try:
        service = AdsService(db)
        result = service.set_ad_config(
            ad_provider=config.ad_provider,
            ad_unit_id=config.ad_unit_id,
            reward_per_ad=config.reward_per_ad,
            daily_limit=config.daily_limit_per_user,
            cooldown_minutes=config.cooldown_minutes
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Failed to set ad config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set ad config: {str(e)}")

@router.get("/config")
async def get_ad_config(db: Session = Depends(get_db)):
    """Get current ad configuration"""
    try:
        service = AdsService(db)
        result = service.get_ad_config()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Failed to get ad config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ad config: {str(e)}")

@router.get("/eligibility/{user_id}")
async def check_ad_eligibility(
    user_id: str,
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Check if user can watch ads"""
    try:
        service = AdsService(db)
        result = service._can_user_watch_ad(user_id, quest_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to check ad eligibility: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check ad eligibility: {str(e)}")
