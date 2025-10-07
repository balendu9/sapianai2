from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class QuestCreate(BaseModel):
    title: str
    description: str
    context: str
    properties: Dict[str, Any]
    instructions: Dict[str, Any]
    additional_text: Dict[str, Any]
    distribution_rules: Dict[str, Any]
    profile_image_url: Optional[str] = None
    media_url: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    initial_pool: float = 1000.0
    treasury_percentage: float = 10.0
    user_percentage: float = 90.0

class QuestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    context: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    instructions: Optional[Dict[str, Any]] = None
    additional_text: Optional[Dict[str, Any]] = None
    distribution_rules: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class QuestResponse(BaseModel):
    quest_id: str
    title: str
    description: str
    context: str
    details: Dict[str, Any]
    profile_image_url: Optional[str]
    media_url: Optional[str]
    distribution_rules: Optional[Dict[str, Any]]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
