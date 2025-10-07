from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DailyAIMessageCreate(BaseModel):
    quest_id: Optional[str] = None
    message_type: str = "daily_reminder"

class DailyAIMessageResponse(BaseModel):
    message_id: str
    user_id: str
    quest_id: Optional[str]
    content: str
    message_type: str
    sent_at: datetime
    is_read: bool
    read_at: Optional[datetime]
    ai_generation_metadata: Optional[dict] = None

    class Config:
        from_attributes = True

class UserDailyAIMessageSettings(BaseModel):
    enabled: bool

class DailyAIMessageStats(BaseModel):
    total_users_enabled: int
    users_needing_message: int
    total_messages_sent: int
    messages_sent_today: int
    unread_messages: int
