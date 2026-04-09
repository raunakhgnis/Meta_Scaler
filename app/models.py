from pydantic import BaseModel
from typing import Optional, List


class Observation(BaseModel):
    ticket_id: str
    message: str
    history: List[str]
    status: str  # open, resolved, escalated


class Action(BaseModel):
    action_type: str  # classify, respond, escalate, close
    content: Optional[str] = None


class Reward(BaseModel):
    score: float
    reason: str = ""

    @field_validator("score")
    def validate_score(cls, v):
        if v <= 0.0:
            return 0.01
        if v >= 1.0:
            return 0.99
        return v