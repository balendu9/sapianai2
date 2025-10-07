from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AdVerificationRequest(BaseModel):
    verification_token: str
    verification_data: Dict[str, Any]

class AdVerificationResponse(BaseModel):
    success: bool
    verification_token: Optional[str] = None
    ad_unit_id: Optional[str] = None
    reward_amount: Optional[float] = None
    expires_at: Optional[str] = None
    message: Optional[str] = None
    credits_earned: Optional[float] = None
    new_balance: Optional[float] = None

class AdStatsResponse(BaseModel):
    success: bool
    ads_watched_today: int
    total_ads_watched: int
    daily_limit: int
    remaining_today: int
    cooldown_minutes: int

class AdConfigRequest(BaseModel):
    ad_provider: str  # google, unity, ironSource, etc.
    ad_unit_id: str
    reward_per_ad: float
    daily_limit_per_user: int
    cooldown_minutes: int

class AdEligibilityResponse(BaseModel):
    can_watch: bool
    error: Optional[str] = None
    ads_watched_today: Optional[int] = None
    daily_limit: Optional[int] = None
    cooldown_remaining: Optional[int] = None
