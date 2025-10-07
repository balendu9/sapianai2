from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class SpinWheelPrize(BaseModel):
    name: str
    description: str
    type: str  # "inputs", "pi_tokens", "bonus_points"
    value: float  # Amount (inputs count, pi tokens, etc.)
    probability: float  # Probability of winning (0.0 to 1.0)
    rarity: str = "common"  # common, rare, epic, legendary

class SpinWheelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    max_spins_per_day: int = 3
    spin_cost: float = 0.0
    prizes: List[SpinWheelPrize]

class SpinWheelResponse(BaseModel):
    wheel_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    max_spins_per_day: int
    spin_cost: float
    prizes: List[Dict[str, Any]]
    created_at: datetime

class SpinResult(BaseModel):
    attempt_id: str
    prize_won: Dict[str, Any]
    input_reward: int
    pi_reward: float
    message: str

class SpinAttemptResponse(BaseModel):
    attempt_id: str
    user_id: str
    wheel_id: str
    prize_won: Dict[str, Any]
    spin_cost: float
    input_reward: int
    pi_reward: float
    created_at: datetime

class UserSpinStatus(BaseModel):
    user_id: str
    spins_used_today: int
    spins_remaining_today: int
    last_spin_at: Optional[datetime] = None
    can_spin: bool
