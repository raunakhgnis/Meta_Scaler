"""FastAPI server for SupportOpsEnv.

Exposes the OpenEnv interface over HTTP: /reset, /step, /state, /tasks, /health.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from app.env import SupportOpsEnv
from app.models import Action, Observation
from app.tasks import TASKS
from app.graders import clamp_score


app = FastAPI(
    title="SupportOpsEnv",
    description="Customer support automation environment for AI agents",
    version="1.0.0",
    root_path="",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = SupportOpsEnv()


# ── Response Models ─────────────────────────────────────────────────

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


class TaskInfo(BaseModel):
    id: str
    difficulty: str
    description: str


# ── Endpoints ───────────────────────────────────────────────────────

@app.get("/")
def root():
    """Root endpoint -- confirms the server is running."""
    return {"status": "running", "environment": "SupportOpsEnv"}


@app.get("/health")
def health():
    """Health check endpoint for OpenEnv validation."""
    return {"status": "healthy"}


@app.get("/tasks", response_model=List[TaskInfo])
def list_tasks():
    """List all available tasks with their difficulty levels."""
    return [
        TaskInfo(
            id=t["id"],
            difficulty=t["difficulty"],
            description=t["description"],
        )
        for t in TASKS
    ]


@app.post("/reset", response_model=Observation)
def reset(request: ResetRequest = None):
    """Reset the environment, optionally selecting a specific task by ID."""
    task_id = request.task_id if request else None
    obs = env.reset(task_id=task_id)
    return obs


@app.post("/step", response_model=StepResponse)
def step(action: Action):
    """Execute one step in the environment."""
    obs, reward, done, info = env.step(action)

    # Final safety clamp at the API boundary
    safe_reward = clamp_score(reward.score)

    return StepResponse(
        observation=obs,
        reward=safe_reward,
        done=done,
        info=info,
    )


@app.get("/state")
def state():
    """Get the current environment state."""
    return env.state()