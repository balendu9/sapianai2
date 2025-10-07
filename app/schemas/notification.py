from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    notification_type: str  # quest_win, quest_end, new_quest, bonus, special
    quest_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class NotificationResponse(BaseModel):
    notification_id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    quest_id: Optional[str] = None
    is_read: bool
    metadata: Dict[str, Any]
    created_at: datetime
    read_at: Optional[datetime] = None

class NotificationMarkRead(BaseModel):
    notification_ids: List[str]

class BulkNotificationCreate(BaseModel):
    user_ids: List[str]  # For sending to multiple users
    title: str
    message: str
    notification_type: str
    quest_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class AdminSpecialNotification(BaseModel):
    target_type: str  # "all_users", "specific_users", "quest_participants"
    user_ids: Optional[List[str]] = None  # Required if target_type is "specific_users"
    quest_id: Optional[str] = None  # Required if target_type is "quest_participants"
    title: str
    message: str
    notification_type: str = "special"
    metadata: Optional[Dict[str, Any]] = {}
