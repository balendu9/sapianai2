from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.participant import QuestParticipant
from app.models.quest import Quest
from app.models.user import User
from app.models.message import ChatMessage
from app.schemas.participation import ParticipationCreate, ParticipationResponse

router = APIRouter()

@router.post("/{quest_id}/join", response_model=ParticipationResponse)
async def join_quest(
    quest_id: str,
    participation: ParticipationCreate,
    db: Session = Depends(get_db)
):
    """User joins a quest"""
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Check if quest is active
    now = datetime.now()
    if quest.start_date and quest.start_date > now:
        raise HTTPException(status_code=400, detail="Quest has not started yet")
    if quest.end_date and quest.end_date < now:
        raise HTTPException(status_code=400, detail="Quest has ended")
    
    # Check if user exists
    user = db.query(User).filter(User.user_id == participation.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already participating
    existing_participation = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest_id,
        QuestParticipant.user_id == participation.user_id
    ).first()
    
    if existing_participation:
        raise HTTPException(status_code=400, detail="User is already participating in this quest")
    
    # Create participation
    participant = QuestParticipant(
        quest_id=quest_id,
        user_id=participation.user_id,
        score=0,
        reply_log=[]
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    return ParticipationResponse(
        qp_id=participant.qp_id,
        quest_id=participant.quest_id,
        user_id=participant.user_id,
        score=participant.score,
        joined_at=participant.joined_at
    )

@router.get("/{quest_id}/participants", response_model=List[ParticipationResponse])
async def get_quest_participants(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Get quest participants"""
    participants = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest_id
    ).all()
    
    return [
        ParticipationResponse(
            qp_id=p.qp_id,
            quest_id=p.quest_id,
            user_id=p.user_id,
            score=p.score,
            joined_at=p.joined_at
        )
        for p in participants
    ]

@router.delete("/{quest_id}/leave")
async def leave_quest(
    quest_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """User leaves quest"""
    participant = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest_id,
        QuestParticipant.user_id == user_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="User is not participating in this quest")
    
    db.delete(participant)
    db.commit()
    
    return {"message": "Successfully left the quest"}

@router.get("/{quest_id}/opening-message")
async def get_quest_opening_message(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Get the opening AI message for a quest"""
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Get the opening AI message (first message with user_id=None)
    opening_message = db.query(ChatMessage).filter(
        ChatMessage.quest_id == quest_id,
        ChatMessage.user_id == None
    ).order_by(ChatMessage.created_at.asc()).first()
    
    if not opening_message:
        raise HTTPException(status_code=404, detail="Quest opening message not found")
    
    return {
        "quest_id": quest_id,
        "opening_message": {
            "message_id": opening_message.message_id,
            "content": opening_message.content,
            "created_at": opening_message.created_at,
            "is_ai": True
        }
    }
