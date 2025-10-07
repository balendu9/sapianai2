from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GlobalLeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    username: str
    average_score: float
    total_score: float
    quests_participated: int
    last_updated: str

class GlobalLeaderboardResponse(BaseModel):
    success: bool
    leaderboard: List[GlobalLeaderboardEntry]
    total_users: int

class DailyBonusConfig(BaseModel):
    rank_1_amount: float
    rank_2_amount: float
    rank_3_amount: float
    currency: str = "PI"

class DailyBonusResponse(BaseModel):
    success: bool
    message: str
    bonuses_created: int
    bonuses: List[dict]

class UserGlobalStats(BaseModel):
    success: bool
    user_id: str
    rank: int
    username: str
    average_score: float
    total_score: float
    quests_participated: int
    last_updated: str
