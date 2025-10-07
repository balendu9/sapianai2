from pydantic import BaseModel
from typing import Optional

class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    score: int
    rank: Optional[int] = None
