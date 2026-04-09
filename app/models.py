from pydantic import BaseModel, field_validator
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
    Score is strictly in the open interval (0, 1) -- never 0.0 or 1.0.
    """
    score: float
    reason: str = ""

    @field_validator("score")
    @classmethod
    def clamp_score_range(cls, v):
        """Clamp score into (0, 1) exclusive -- never reject, always fix."""
        v = float(v)
        if v <= 0.0:
            return 0.01
        if v >= 1.0:
            return 0.99
        return round(v, 6)