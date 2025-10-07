from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.leaderboard_service import LeaderboardService
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{quest_id}/live")
async def get_live_leaderboard(
    quest_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get real-time leaderboard for a quest"""
    try:
        leaderboard_service = LeaderboardService(db)
        
        # Get current leaderboard
        leaderboard = leaderboard_service.get_leaderboard(quest_id, limit)
        
        # Get quest status
        quest_status = leaderboard_service.get_quest_status(quest_id)
        
        return {
            "success": True,
            "quest_id": quest_id,
            "leaderboard": leaderboard,
            "quest_status": quest_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get live leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get live leaderboard: {str(e)}")

@router.post("/{quest_id}/update")
async def update_leaderboard(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Manually update leaderboard for a quest"""
    try:
        leaderboard_service = LeaderboardService(db)
        result = leaderboard_service.update_leaderboard(quest_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to update leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update leaderboard: {str(e)}")

@router.get("/{quest_id}/status")
async def get_quest_status(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Get quest status and leaderboard info"""
    try:
        leaderboard_service = LeaderboardService(db)
        result = leaderboard_service.get_quest_status(quest_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get quest status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quest status: {str(e)}")

@router.get("/{quest_id}/top/{limit}")
async def get_top_participants(
    quest_id: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Get top N participants for a quest"""
    try:
        leaderboard_service = LeaderboardService(db)
        leaderboard = leaderboard_service.get_leaderboard(quest_id, limit)
        
        return {
            "success": True,
            "quest_id": quest_id,
            "top_participants": leaderboard,
            "count": len(leaderboard)
        }
        
    except Exception as e:
        logger.error(f"Failed to get top participants: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get top participants: {str(e)}")

# Add datetime import
from datetime import datetime
