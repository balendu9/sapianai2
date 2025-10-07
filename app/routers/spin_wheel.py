from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, date
import random

from app.database import get_db
from app.models.spin_wheel import SpinWheel, SpinAttempt
from app.models.user import User
from app.models.input import QuestInput
from app.models.wallet import UserWallet, WalletTransaction, TransactionType, TransactionStatus
from app.models.admin import AdminUser
from app.schemas.spin_wheel import (
    SpinWheelCreate, SpinWheelResponse, SpinResult, SpinAttemptResponse, UserSpinStatus
)
from app.routers.auth import get_current_admin

router = APIRouter()

@router.get("/wheels", response_model=List[SpinWheelResponse])
async def get_active_spin_wheels(db: Session = Depends(get_db)):
    """Get all active spin wheels"""
    wheels = db.query(SpinWheel).filter(SpinWheel.is_active == True).all()
    return [SpinWheelResponse(**{
        "wheel_id": wheel.wheel_id,
        "name": wheel.name,
        "description": wheel.description,
        "is_active": wheel.is_active,
        "max_spins_per_day": wheel.max_spins_per_day,
        "spin_cost": wheel.spin_cost,
        "prizes": wheel.prizes,
        "created_at": wheel.created_at
    }) for wheel in wheels]

@router.get("/{user_id}/status", response_model=UserSpinStatus)
async def get_user_spin_status(user_id: str, db: Session = Depends(get_db)):
    """Get user's spin wheel status"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get active wheel (assuming one active wheel for now)
    wheel = db.query(SpinWheel).filter(SpinWheel.is_active == True).first()
    if not wheel:
        return UserSpinStatus(
            user_id=user_id,
            spins_used_today=0,
            spins_remaining_today=0,
            last_spin_at=None,
            can_spin=False
        )
    
    # Count spins used today
    today = date.today()
    spins_used_today = db.query(func.count(SpinAttempt.attempt_id)).filter(
        SpinAttempt.user_id == user_id,
        func.date(SpinAttempt.created_at) == today
    ).scalar() or 0
    
    spins_remaining_today = max(0, wheel.max_spins_per_day - spins_used_today)
    
    # Get last spin time
    last_spin = db.query(SpinAttempt).filter(
        SpinAttempt.user_id == user_id
    ).order_by(desc(SpinAttempt.created_at)).first()
    
    last_spin_at = last_spin.created_at if last_spin else None
    
    # Check if user can spin
    can_spin = spins_remaining_today > 0
    
    # If spin costs Pi tokens, check wallet balance
    if wheel.spin_cost > 0:
        wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
        if not wallet or wallet.balance < wheel.spin_cost:
            can_spin = False
    
    return UserSpinStatus(
        user_id=user_id,
        spins_used_today=spins_used_today,
        spins_remaining_today=spins_remaining_today,
        last_spin_at=last_spin_at,
        can_spin=can_spin
    )

@router.post("/{user_id}/spin/{wheel_id}", response_model=SpinResult)
async def spin_wheel(
    user_id: str,
    wheel_id: str,
    db: Session = Depends(get_db)
):
    """Spin the wheel for rewards"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get wheel
    wheel = db.query(SpinWheel).filter(
        SpinWheel.wheel_id == wheel_id,
        SpinWheel.is_active == True
    ).first()
    if not wheel:
        raise HTTPException(status_code=404, detail="Spin wheel not found or inactive")
    
    # Check if user can spin today
    today = date.today()
    spins_used_today = db.query(func.count(SpinAttempt.attempt_id)).filter(
        SpinAttempt.user_id == user_id,
        func.date(SpinAttempt.created_at) == today
    ).scalar() or 0
    
    if spins_used_today >= wheel.max_spins_per_day:
        raise HTTPException(status_code=400, detail="Daily spin limit reached")
    
    # Check wallet balance if spin costs Pi tokens
    if wheel.spin_cost > 0:
        wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
        if not wallet:
            wallet = UserWallet(user_id=user_id, balance=0.0)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        
        if wallet.balance < wheel.spin_cost:
            raise HTTPException(status_code=400, detail="Insufficient balance for spin")
    
    try:
        # Spin the wheel
        prize = spin_wheel_logic(wheel.prizes)
        
        # Deduct spin cost from wallet if applicable
        if wheel.spin_cost > 0:
            wallet.balance -= wheel.spin_cost
            
            # Create transaction record
            transaction = WalletTransaction(
                wallet_id=wallet.wallet_id,
                user_id=user_id,
                transaction_type=TransactionType.WITHDRAWAL,
                amount=wheel.spin_cost,
                balance_before=wallet.balance + wheel.spin_cost,
                balance_after=wallet.balance,
                status=TransactionStatus.COMPLETED,
                description=f"Spin wheel cost - {wheel.name}",
                transaction_metadata={
                    "wheel_id": wheel_id,
                    "spin_type": "wheel_cost",
                    "spent_at": datetime.now().isoformat()
                },
                processed_at=datetime.now()
            )
            db.add(transaction)
        
        # Add Pi token rewards to wallet if applicable
        pi_reward = 0.0
        if prize["type"] == "pi_tokens":
            pi_reward = prize["value"]
            if pi_reward > 0:
                wallet.balance += pi_reward
                wallet.total_earned += pi_reward
                
                # Create transaction record for reward
                reward_transaction = WalletTransaction(
                    wallet_id=wallet.wallet_id,
                    user_id=user_id,
                    transaction_type=TransactionType.DEPOSIT,
                    amount=pi_reward,
                    balance_before=wallet.balance - pi_reward,
                    balance_after=wallet.balance,
                    status=TransactionStatus.COMPLETED,
                    description=f"Spin wheel reward - {prize['name']}",
                    transaction_metadata={
                        "wheel_id": wheel_id,
                        "reward_type": "pi_tokens",
                        "prize_won": prize,
                        "earned_at": datetime.now().isoformat()
                    },
                    processed_at=datetime.now()
                )
                db.add(reward_transaction)
        
        # Add input rewards
        input_reward = 0
        if prize["type"] == "inputs":
            input_reward = int(prize["value"])
            if input_reward > 0:
                # Create input record
                spin_input = QuestInput(
                    user_id=user_id,
                    quest_id="global",  # Global inputs from spin
                    input_date=today,
                    input_type="spin",
                    count=input_reward,
                    payment_amount=0.0
                )
                db.add(spin_input)
        
        # Record the spin attempt
        spin_attempt = SpinAttempt(
            user_id=user_id,
            wheel_id=wheel_id,
            prize_won=prize,
            spin_cost=wheel.spin_cost,
            input_reward=input_reward,
            pi_reward=pi_reward
        )
        db.add(spin_attempt)
        
        db.commit()
        db.refresh(spin_attempt)
        
        # Create result message
        message = f"Congratulations! You won: {prize['name']}"
        if input_reward > 0:
            message += f" (+{input_reward} inputs)"
        if pi_reward > 0:
            message += f" (+{pi_reward} Pi tokens)"
        
        return SpinResult(
            attempt_id=spin_attempt.attempt_id,
            prize_won=prize,
            input_reward=input_reward,
            pi_reward=pi_reward,
            message=message
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Spin failed: {str(e)}")

@router.get("/{user_id}/history", response_model=List[SpinAttemptResponse])
async def get_user_spin_history(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's spin history"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    attempts = db.query(SpinAttempt).filter(
        SpinAttempt.user_id == user_id
    ).order_by(desc(SpinAttempt.created_at)).limit(limit).all()
    
    return [SpinAttemptResponse(**{
        "attempt_id": attempt.attempt_id,
        "user_id": attempt.user_id,
        "wheel_id": attempt.wheel_id,
        "prize_won": attempt.prize_won,
        "spin_cost": attempt.spin_cost,
        "input_reward": attempt.input_reward,
        "pi_reward": attempt.pi_reward,
        "created_at": attempt.created_at
    }) for attempt in attempts]

# Admin endpoints

@router.post("/admin/create-wheel", response_model=SpinWheelResponse)
async def create_spin_wheel(
    wheel_data: SpinWheelCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new spin wheel (admin only)"""
    
    # Validate prizes probabilities sum to 1.0
    total_probability = sum(prize.probability for prize in wheel_data.prizes)
    if abs(total_probability - 1.0) > 0.001:
        raise HTTPException(status_code=400, detail="Prize probabilities must sum to 1.0")
    
    wheel = SpinWheel(
        name=wheel_data.name,
        description=wheel_data.description,
        max_spins_per_day=wheel_data.max_spins_per_day,
        spin_cost=wheel_data.spin_cost,
        prizes=[prize.dict() for prize in wheel_data.prizes]
    )
    
    try:
        db.add(wheel)
        db.commit()
        db.refresh(wheel)
        
        return SpinWheelResponse(**{
            "wheel_id": wheel.wheel_id,
            "name": wheel.name,
            "description": wheel.description,
            "is_active": wheel.is_active,
            "max_spins_per_day": wheel.max_spins_per_day,
            "spin_cost": wheel.spin_cost,
            "prizes": wheel.prizes,
            "created_at": wheel.created_at
        })
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create spin wheel: {str(e)}")

def spin_wheel_logic(prizes: List[dict]) -> dict:
    """Logic for spinning the wheel and determining the prize"""
    if not prizes:
        raise ValueError("No prizes available")
    
    # Generate random number between 0 and 1
    random_value = random.random()
    
    # Find the prize based on cumulative probability
    cumulative_probability = 0.0
    for prize in prizes:
        cumulative_probability += prize["probability"]
        if random_value <= cumulative_probability:
            return prize
    
    # Fallback to last prize (should not happen with proper probabilities)
    return prizes[-1]
