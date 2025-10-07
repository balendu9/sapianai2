from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.global_leaderboard_service import GlobalLeaderboardService
from app.schemas.global_leaderboard import GlobalLeaderboardResponse, DailyBonusConfig, DailyBonusResponse
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=GlobalLeaderboardResponse)
async def get_global_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get global leaderboard across all quests"""
    try:
        service = GlobalLeaderboardService(db)
        leaderboard = service.get_global_leaderboard(limit)
        
        return GlobalLeaderboardResponse(
            success=True,
            leaderboard=leaderboard,
            total_users=len(leaderboard)
        )
        
    except Exception as e:
        logger.error(f"Failed to get global leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get global leaderboard: {str(e)}")

@router.post("/update")
async def update_global_leaderboard(db: Session = Depends(get_db)):
    """Update global leaderboard (admin function)"""
    try:
        service = GlobalLeaderboardService(db)
        result = service.update_global_leaderboard()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Failed to update global leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update global leaderboard: {str(e)}")

@router.post("/daily-bonuses/process")
async def process_daily_bonuses(db: Session = Depends(get_db)):
    """Process daily bonuses for top 3 users (admin function)"""
    try:
        service = GlobalLeaderboardService(db)
        result = service.process_daily_bonuses()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Failed to process daily bonuses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process daily bonuses: {str(e)}")

@router.post("/daily-bonuses/config")
async def set_daily_bonus_config(
    config: DailyBonusConfig,
    db: Session = Depends(get_db)
):
    """Set daily bonus configuration (admin function)"""
    try:
        service = GlobalLeaderboardService(db)
        result = service.set_bonus_config(
            rank_1_amount=config.rank_1_amount,
            rank_2_amount=config.rank_2_amount,
            rank_3_amount=config.rank_3_amount,
            currency=config.currency
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Failed to set bonus config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set bonus config: {str(e)}")

@router.get("/daily-bonuses/config")
async def get_daily_bonus_config(db: Session = Depends(get_db)):
    """Get current daily bonus configuration"""
    try:
        service = GlobalLeaderboardService(db)
        result = service.get_bonus_config()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Failed to get bonus config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get bonus config: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_global_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's global leaderboard stats"""
    try:
        service = GlobalLeaderboardService(db)
        
        # Get user's global leaderboard entry
        user_entry = db.query(service.db.query(GlobalLeaderboard).filter(
            GlobalLeaderboard.user_id == user_id
        ).first())
        
        if not user_entry:
            raise HTTPException(status_code=404, detail="User not found in global leaderboard")
        
        return {
            "success": True,
            "user_id": user_id,
            "rank": user_entry.rank,
            "username": user_entry.username,
            "average_score": user_entry.average_score,
            "total_score": user_entry.total_score,
            "quests_participated": user_entry.quests_participated,
            "last_updated": user_entry.last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user global stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user global stats: {str(e)}")
