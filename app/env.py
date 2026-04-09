import random
from app.models import Observation, Action, Reward
from app.tasks import TASKS
from app.graders import grade_task


class SupportOpsEnv:
    def __init__(self):
        self.current_task = None
        self.state_data = None
        self.steps = 0
        self.max_steps = 5

    # 🔁 Reset environment
    def reset(self):
        self.current_task = random.choice(TASKS)

        self.state_data = {
            "ticket_id": self.current_task.get("id", "T0"),
            "message": self.current_task.get("message", ""),
            "history": [],
            "status": "open"
        }

        self.steps = 0

        return Observation(**self.state_data)

    # ⚙️ Step function (SAFE + CLAMPED)
    def step(self, action: Action):
        self.steps += 1

        # ensure state exists
        if self.state_data is None:
            self.reset()

        # store actual response content
        self.state_data["history"].append(action.content or "")

        # 🎯 apply action logic
        if action.action_type == "respond":
            if "refund" in (action.content or "").lower():
                self.state_data["status"] = "closed"

        elif action.action_type == "close":
            self.state_data["status"] = "closed"

        elif action.action_type == "escalate":
            # stays open but escalated logically
            self.state_data["status"] = "open"

        # 🧠 grading (SAFE)
        try:
            reward_score, reason = grade_task(
                self.current_task,
                action,
                self.state_data
            )
        except Exception as e:
            reward_score, reason = 0.01, f"error: {str(e)}"   # ✅ NEVER 0.0

        # 🔥 FINAL CLAMP (MOST IMPORTANT LINE)
        if reward_score <= 0.0:
            reward_score = 0.01
        elif reward_score >= 1.0:
            reward_score = 0.99

        # 🎯 done condition
        done = (
            self.steps >= self.max_steps or
            self.state_data["status"] == "closed"
        )

        # 🧾 safe observation
        try:
            obs = Observation(**self.state_data)
        except Exception:
            obs = Observation(
                ticket_id="T0",
                message="fallback",
                history=[],
                status="open"
            )

        return obs, Reward(score=reward_score, reason=reason), done, {}

    # 📊 Get current state
    def state(self):
        return self.state_data or {
            "ticket_id": "T0",
            "message": "",
            "history": [],
            "status": "open"
        }

