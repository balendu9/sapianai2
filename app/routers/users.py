from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models.user import User
from app.models.input import QuestInput
from app.schemas.user import UserResponse, UserCreate

router = APIRouter()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Input validation
    if not user.user_id or len(user.user_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    if user.username and len(user.username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username cannot be empty if provided")
    
    if user.username and len(user.username) > 100:
        raise HTTPException(status_code=400, detail="Username too long (max 100 characters)")
    
    if user.email and len(user.email) > 200:
        raise HTTPException(status_code=400, detail="Email too long (max 200 characters)")
    
    # Check if user_id already exists (Pi Network user ID is primary)
    existing_user = db.query(User).filter(User.user_id == user.user_id).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")
    
    # Check if username already exists (only if provided)
    if user.username:
        existing_username = db.query(User).filter(User.username == user.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists (only if provided)
    if user.email:
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user = User(
        user_id=user.user_id,  # Pi Network user ID - primary identifier
        username=user.username,  # Optional display name
        email=user.email  # Optional email
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.get("/{user_id}/inputs")
async def get_user_inputs(user_id: str, db: Session = Depends(get_db)):
    """Get user's input status and history"""
    # Get today's inputs
    today = date.today()
    today_inputs = db.query(QuestInput).filter(
        QuestInput.user_id == user_id,
        QuestInput.input_date == today
    ).all()
    
    # Calculate remaining free inputs (assuming 2 free per day)
    free_inputs_used = sum(
        input.count for input in today_inputs 
        if input.input_type == "free"
    )
    free_inputs_remaining = max(0, 2 - free_inputs_used)
    
    # Get input history
    input_history = db.query(QuestInput).filter(
        QuestInput.user_id == user_id
    ).order_by(QuestInput.created_at.desc()).limit(50).all()
    
    return {
        "user_id": user_id,
        "free_inputs_remaining": free_inputs_remaining,
        "today_inputs": len(today_inputs),
        "input_history": [
            {
                "input_id": input.input_id,
                "quest_id": input.quest_id,
                "input_type": input.input_type,
                "count": input.count,
                "payment_amount": input.payment_amount,
                "input_date": input.input_date,
                "created_at": input.created_at
            }
            for input in input_history
        ]
    }

@router.post("/{user_id}/inputs/claim")
async def claim_daily_inputs(user_id: str, db: Session = Depends(get_db)):
    """Claim daily free inputs"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already claimed today
    today = date.today()
    existing_claim = db.query(QuestInput).filter(
        QuestInput.user_id == user_id,
        QuestInput.input_date == today,
        QuestInput.input_type == "free"
    ).first()
    
    if existing_claim:
        raise HTTPException(status_code=400, detail="Daily free inputs already claimed")
    
    # Create free input record
    free_input = QuestInput(
        user_id=user_id,
        quest_id="global",  # Global free inputs
        input_date=today,
        input_type="free",
        count=2,  # 2 free inputs per day
        payment_amount=0.0
    )
    
    try:
        db.add(free_input)
        db.commit()
        return {
            "message": "Daily free inputs claimed successfully",
            "free_inputs_granted": 2
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to claim daily inputs: {str(e)}")
