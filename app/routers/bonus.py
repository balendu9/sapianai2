from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models.bonus import DailyBonus
from app.models.user import User
from app.schemas.bonus import BonusResponse, BonusClaim

router = APIRouter()

@router.get("/", response_model=List[BonusResponse])
async def get_daily_bonuses(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get daily bonuses (active/eligible only)"""
    today = date.today()
    
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get today's bonus
    today_bonus = db.query(DailyBonus).filter(
        DailyBonus.user_id == user_id,
        DailyBonus.bonus_date == today
    ).first()
    
    if not today_bonus:
        # Create new daily bonus
        today_bonus = DailyBonus(
            user_id=user_id,
            bonus_date=today,
            reward_amount=10.0,  # Default daily bonus amount
            claimed=False
        )
        db.add(today_bonus)
        db.commit()
        db.refresh(today_bonus)
    
    return [BonusResponse(
        bonus_id=today_bonus.bonus_id,
        user_id=today_bonus.user_id,
        bonus_date=today_bonus.bonus_date,
        reward_amount=today_bonus.reward_amount,
        claimed=today_bonus.claimed,
        created_at=today_bonus.created_at
    )]

@router.post("/claim", response_model=BonusResponse)
async def claim_daily_bonus(
    bonus_claim: BonusClaim,
    db: Session = Depends(get_db)
):
    """Claim daily bonus"""
    today = date.today()
    
    # Check if user exists
    user = db.query(User).filter(User.user_id == bonus_claim.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get today's bonus
    today_bonus = db.query(DailyBonus).filter(
        DailyBonus.user_id == bonus_claim.user_id,
        DailyBonus.bonus_date == today
    ).first()
    
    if not today_bonus:
        raise HTTPException(status_code=404, detail="No daily bonus available")
    
    if today_bonus.claimed:
        raise HTTPException(status_code=400, detail="Daily bonus already claimed")
    
    # Claim the bonus
    today_bonus.claimed = True
    db.commit()
    
    # Note: Bonus integration with Pi Network would be handled here
    # For now, the bonus is tracked in the database
    
    return BonusResponse(
        bonus_id=today_bonus.bonus_id,
        user_id=today_bonus.user_id,
        bonus_date=today_bonus.bonus_date,
        reward_amount=today_bonus.reward_amount,
        claimed=today_bonus.claimed,
        created_at=today_bonus.created_at
    )
