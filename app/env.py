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
            "ticket_id": self.current_task["id"],
            "message": self.current_task["message"],
            "history": [],
            "status": "open"
        }

        self.steps = 0

        return Observation(**self.state_data)

    # ⚙️ Step function
    def step(self, action: Action):
        self.steps += 1

        # 🧠 Ensure state exists
        if self.state_data is None:
            self.reset()

        # ✅ Append ACTUAL response content (IMPORTANT FIX)
        self.state_data["history"].append(action.content)

        # 🎯 Apply action logic
        if action.action_type == "respond":
            if "refund" in action.content.lower():
                self.state_data["status"] = "closed"

        elif action.action_type == "close":
            self.state_data["status"] = "closed"

        elif action.action_type == "escalate":
            self.state_data["status"] = "open"  # keep open but escalated logically

        # ✅ Reward grading
        try:
            reward_score, reason = grade_task(
                self.current_task,
                action,
                self.state_data
            )
        except Exception as e:
            reward_score, reason = 0.0, f"error: {str(e)}"

        # ✅ Done condition
        done = (
            self.steps >= self.max_steps or
            self.state_data["status"] == "closed"
        )

        # ✅ Clean observation
        obs = Observation(**self.state_data)

        return obs, Reward(score=reward_score, reason=reason), done, {}

    # 📊 Get current state
    def state(self):
        return self.state_data