from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.payment_splitter import PaymentSplitter
from app.models.quest import Quest
from app.models.participant import QuestParticipant

router = APIRouter()

class PaymentRequest(BaseModel):
    user_id: str
    quest_id: str
    amount: float
    payment_type: str = "extra_input"  # extra_input, premium_feature, etc.

class PaymentResponse(BaseModel):
    success: bool
    message: str
    split_details: dict
    new_pool_totals: dict

@router.post("/process-payment", response_model=PaymentResponse)
async def process_user_payment(
    payment: PaymentRequest,
    db: Session = Depends(get_db)
):
    """Process a user payment and split between treasury and pool"""
    
    try:
        # Validate quest exists and is active
        quest = db.query(Quest).filter(Quest.quest_id == payment.quest_id).first()
        if not quest:
            raise HTTPException(status_code=404, detail="Quest not found")
        
        # Validate user is participating in quest
        participant = db.query(QuestParticipant).filter(
            QuestParticipant.quest_id == payment.quest_id,
            QuestParticipant.user_id == payment.user_id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=400, detail="User not participating in this quest")
        
        # Process payment split
        split_details = PaymentSplitter.split_payment(
            db=db,
            quest_id=payment.quest_id,
            user_id=payment.user_id,
            payment_amount=payment.amount,
            source="user_payment"
        )
        
        # Get updated pool totals
        pool_totals = PaymentSplitter.get_quest_pool_totals(db, payment.quest_id)
        
        return PaymentResponse(
            success=True,
            message=f"Payment of ${payment.amount} processed successfully",
            split_details=split_details,
            new_pool_totals=pool_totals
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

@router.get("/quest/{quest_id}/pool-totals")
async def get_quest_pool_totals(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Get current pool totals for a quest"""
    
    try:
        totals = PaymentSplitter.get_quest_pool_totals(db, quest_id)
        return totals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pool totals: {str(e)}")

@router.get("/platform/totals")
async def get_platform_totals(db: Session = Depends(get_db)):
    """Get platform-wide treasury and pool totals"""
    
    try:
        totals = PaymentSplitter.get_platform_totals(db)
        return totals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform totals: {str(e)}")
