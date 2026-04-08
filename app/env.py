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
            "history": [],
            "status": "open"
        }

        self.steps = 0

        return Observation(
            ticket_id=self.current_task["id"],
            message=self.current_task["message"],
            history=[],
            status="open"
        )

    # ⚙️ Step function (SAFE + NO CRASH)
    def step(self, action: Action):
        self.steps += 1

        # ✅ Safe grading
        try:
            reward_score, reason = grade_task(
                self.current_task,
                action,
                self.state_data
            )
        except Exception as e:
            reward_score, reason = 0.0, f"error: {str(e)}"

        # ✅ Safe state updates
        try:
            if self.state_data is None:
                self.state_data = {"history": [], "status": "open"}

            self.state_data["history"].append(action.action_type)

            if action.action_type == "close":
                self.state_data["status"] = "resolved"
            elif action.action_type == "escalate":
                self.state_data["status"] = "escalated"

        except Exception as e:
            # fallback safety
            self.state_data = {"history": [], "status": "open"}

        # ✅ Done condition
        done = (
            self.steps >= self.max_steps or
            self.state_data.get("status") != "open"
        )

        # ✅ Safe observation creation
        try:
            obs = Observation(
                ticket_id=self.current_task.get("id", "unknown"),
                message=self.current_task.get("message", ""),
                history=self.state_data.get("history", []),
                status=self.state_data.get("status", "open")
            )
        except Exception:
            # fallback observation
            obs = Observation(
                ticket_id="error",
                message="error",
                history=[],
                status="open"
            )

        return obs, Reward(score=reward_score, reason=reason), done, {}

    # 📊 Get current state
    def state(self):
        return self.state_data