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
    reason: str