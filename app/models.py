from pydantic import BaseModel, Field
from typing import Optional, List


class Observation(BaseModel):
    """Observation returned by the environment after each step or reset."""
    ticket_id: str
    message: str
    history: List[str]
    status: str


class Action(BaseModel):
    """Action sent by the agent to the environment."""
    action_type: str  # "respond", "escalate", "close"
    content: Optional[str] = None


class Reward(BaseModel):
    """Reward returned by the environment after each step.
    Score is strictly in the open interval (0, 1) — never 0.0 or 1.0.
    """
    score: float = Field(..., gt=0.0, lt=1.0)
    reason: str = ""