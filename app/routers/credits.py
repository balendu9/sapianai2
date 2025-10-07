from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.credits_service import CreditsService
from app.schemas.credits import CreditStatus, CreditPurchase, CreditResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{quest_id}/status/{user_id}", response_model=CreditStatus)
async def get_credit_status(
    quest_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's credit status for a quest"""
    try:
        credits_service = CreditsService(db)
        status = credits_service.can_send_message(user_id, quest_id)
        
        return CreditStatus(
            quest_id=quest_id,
            user_id=user_id,
            can_send=status["can_send"],
            available_credits=status["available_credits"],
            daily_credits=status["daily_credits"],
            used_today=status["used_today"],
            next_reset=status["next_reset"]
        )
    except Exception as e:
        logger.error(f"Failed to get credit status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get credit status: {str(e)}")

@router.post("/{quest_id}/purchase/{user_id}", response_model=CreditResponse)
async def purchase_credits(
    quest_id: str,
    user_id: str,
    purchase_data: CreditPurchase,
    db: Session = Depends(get_db)
):
    """Purchase additional credits for a quest"""
    try:
        credits_service = CreditsService(db)
        
        # In a real implementation, this would integrate with payment system
        # For now, we'll just add the credits
        result = credits_service.add_credits(
            user_id=user_id,
            quest_id=quest_id,
            amount=purchase_data.amount,
            source="purchase",
            description=f"Purchased {purchase_data.amount} credits"
        )
        
        if result["success"]:
            return CreditResponse(
                success=True,
                message=f"Successfully purchased {purchase_data.amount} credits",
                available_credits=result["available_credits"],
                daily_credits=result["daily_credits"]
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to purchase credits")
            
    except Exception as e:
        logger.error(f"Failed to purchase credits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to purchase credits: {str(e)}")

@router.post("/{quest_id}/ad-reward/{user_id}", response_model=CreditResponse)
async def claim_ad_reward(
    quest_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Claim credits from watching an ad"""
    try:
        credits_service = CreditsService(db)
        
        # Give 1 credit for watching an ad
        result = credits_service.add_credits(
            user_id=user_id,
            quest_id=quest_id,
            amount=1,
            source="ad_reward",
            description="Credits earned from watching ad"
        )
        
        if result["success"]:
            return CreditResponse(
                success=True,
                message="Successfully earned 1 credit from ad",
                available_credits=result["available_credits"],
                daily_credits=result["daily_credits"]
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to claim ad reward")
            
    except Exception as e:
        logger.error(f"Failed to claim ad reward: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to claim ad reward: {str(e)}")

@router.get("/{quest_id}/stats")
async def get_quest_credit_stats(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Get credit statistics for a quest (admin function)"""
    try:
        credits_service = CreditsService(db)
        stats = credits_service.get_quest_credit_stats(quest_id)
        return stats
    except Exception as e:
        logger.error(f"Failed to get quest credit stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quest credit stats: {str(e)}")

@router.put("/{quest_id}/limit")
async def set_quest_credit_limit(
    quest_id: str,
    daily_credits: int,
    db: Session = Depends(get_db)
):
    """Set daily credit limit for a quest (admin function)"""
    try:
        if daily_credits < 0:
            raise HTTPException(status_code=400, detail="Daily credits must be positive")
        
        credits_service = CreditsService(db)
        success = credits_service.set_quest_credit_limit(quest_id, daily_credits)
        
        if success:
            return {
                "success": True,
                "message": f"Quest credit limit set to {daily_credits} per day",
                "quest_id": quest_id,
                "daily_credits": daily_credits
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set credit limit")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set credit limit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set credit limit: {str(e)}")
