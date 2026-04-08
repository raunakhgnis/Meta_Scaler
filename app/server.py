from fastapi import FastAPI
from pydantic import BaseModel
from app.env import SupportOpsEnv
from app.models import Action, Observation

app = FastAPI()
env = SupportOpsEnv()


# ✅ Step response model (IMPORTANT)
class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

@app.get("/")
def root():
    return {"status": "running"}


# ✅ Reset endpoint with proper schema
@app.post("/reset", response_model=Observation)
def reset():
    obs = env.reset()
    return obs   # ⚠️ NOT model_dump()


# ✅ Step endpoint with schema
@app.post("/step", response_model=StepResponse)
def step(action: Action):
    obs, reward, done, info = env.step(action)

    return {
        "observation": obs,   # ⚠️ NOT model_dump()
        "reward": reward.score,
        "done": done,
        "info": info
    }


# ✅ State endpoint
@app.get("/state")
def state():
    return env.state()


# from fastapi import FastAPI
# from app.env import SupportOpsEnv
# from app.models import Action

# app = FastAPI()
# env = SupportOpsEnv()


# @app.post("/reset")
# def reset():
#     obs = env.reset()
#     return obs.model_dump()


# @app.post("/step")
# def step(action: Action):
#     obs, reward, done, info = env.step(action)
#     return {
#         "observation": obs.model_dump(),
#         "reward": reward.score,
#         "done": done,
#         "info": info
#     }


# @app.get("/state")
# def state():
#     return env.state()