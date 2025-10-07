from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.database import get_db
from app.models.leaderboard import Leaderboard
from app.models.user import User
from app.schemas.leaderboard import LeaderboardEntry

router = APIRouter()

@router.get("/quest/{quest_id}", response_model=List[LeaderboardEntry])
async def get_quest_leaderboard(
    quest_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get quest leaderboard by quest ID"""
    leaderboard = db.query(Leaderboard).filter(
        Leaderboard.quest_id == quest_id
    ).order_by(desc(Leaderboard.score)).limit(limit).all()
    
    # Get user details for each entry
    entries = []
    for entry in leaderboard:
        user = db.query(User).filter(User.user_id == entry.user_id).first()
        if user:
            entries.append(LeaderboardEntry(
                user_id=entry.user_id,
                username=user.username,
                score=entry.score,
                rank=entry.rank
            ))
    
    return entries

@router.get("/global", response_model=List[LeaderboardEntry])
async def get_global_leaderboard(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get global leaderboard (all quests combined)"""
    # Get users with their total scores
    users = db.query(User).order_by(desc(User.total_score)).limit(limit).all()
    
    entries = []
    for rank, user in enumerate(users, 1):
        entries.append(LeaderboardEntry(
            user_id=user.user_id,
            username=user.username,
            score=user.total_score,
            rank=rank
        ))
    
    return entries

@router.post("/quest/{quest_id}/update")
async def update_quest_leaderboard(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Update quest leaderboard (admin-only)"""
    # This would typically be called after quest ends
    # Calculate ranks based on quest participants
    from app.models.participant import QuestParticipant
    
    participants = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest_id
    ).order_by(desc(QuestParticipant.score)).all()
    
    # Update leaderboard entries
    for rank, participant in enumerate(participants, 1):
        # Check if entry exists
        existing_entry = db.query(Leaderboard).filter(
            Leaderboard.quest_id == quest_id,
            Leaderboard.user_id == participant.user_id
        ).first()
        
        if existing_entry:
            existing_entry.score = participant.score
            existing_entry.rank = rank
        else:
            new_entry = Leaderboard(
                quest_id=quest_id,
                user_id=participant.user_id,
                score=participant.score,
                rank=rank
            )
            db.add(new_entry)
    
    db.commit()
    
    return {"message": "Quest leaderboard updated successfully"}

@router.post("/global/update")
async def update_global_leaderboard(db: Session = Depends(get_db)):
    """Update global leaderboard (admin-only)"""
    # This would typically be called periodically
    # Calculate total scores for all users
    from app.models.participant import QuestParticipant
    from sqlalchemy import func
    
    # Get total scores per user
    user_scores = db.query(
        QuestParticipant.user_id,
        func.sum(QuestParticipant.score).label('total_score')
    ).group_by(QuestParticipant.user_id).all()
    
    # Update user total scores
    for user_id, total_score in user_scores:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.total_score = total_score
    
    db.commit()
    
    return {"message": "Global leaderboard updated successfully"}
