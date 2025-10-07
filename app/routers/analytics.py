from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, Any

from app.database import get_db
from app.models.quest import Quest
from app.models.participant import QuestParticipant
from app.models.user import User
from app.models.pool import QuestPool
from app.models.admin import AdminUser
from app.routers.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_platform_analytics(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform analytics (admin-only)"""
    
    # Total users
    total_users = db.query(User).count()
    
    # Total quests
    total_quests = db.query(Quest).count()
    active_quests = db.query(Quest).filter(
        Quest.start_date <= datetime.now(),
        Quest.end_date >= datetime.now()
    ).count()
    
    # Total participants
    total_participants = db.query(QuestParticipant).count()
    
    # Total treasury
    total_treasury = db.query(func.sum(QuestPool.split_to_treasury)).scalar() or 0
    total_prize_pools = db.query(func.sum(QuestPool.split_to_pool)).scalar() or 0
    
    # Participation over time (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    participation_data = db.query(
        func.date(QuestParticipant.joined_at).label('date'),
        func.count(QuestParticipant.qp_id).label('count')
    ).filter(
        QuestParticipant.joined_at >= thirty_days_ago
    ).group_by(func.date(QuestParticipant.joined_at)).all()
    
    # Treasury growth over time
    treasury_growth = db.query(
        func.date(QuestPool.created_at).label('date'),
        func.sum(QuestPool.split_to_treasury).label('treasury'),
        func.sum(QuestPool.split_to_pool).label('pools')
    ).filter(
        QuestPool.created_at >= thirty_days_ago
    ).group_by(func.date(QuestPool.created_at)).all()
    
    # Average scores per quest
    quest_scores = db.query(
        Quest.title,
        func.avg(QuestParticipant.score).label('avg_score'),
        func.count(QuestParticipant.qp_id).label('participant_count')
    ).join(QuestParticipant).group_by(Quest.quest_id, Quest.title).all()
    
    return {
        "overview": {
            "total_users": total_users,
            "total_quests": total_quests,
            "active_quests": active_quests,
            "total_participants": total_participants,
            "total_treasury": total_treasury,
            "total_prize_pools": total_prize_pools
        },
        "participation_over_time": [
            {"date": str(date), "count": count}
            for date, count in participation_data
        ],
        "treasury_growth": [
            {
                "date": str(date),
                "treasury": float(treasury),
                "pools": float(pools)
            }
            for date, treasury, pools in treasury_growth
        ],
        "quest_performance": [
            {
                "quest_title": title,
                "avg_score": float(avg_score),
                "participant_count": participant_count
            }
            for title, avg_score, participant_count in quest_scores
        ]
    }
