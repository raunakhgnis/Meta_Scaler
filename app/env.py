"""SupportOpsEnv — Customer support automation environment.

Implements the OpenEnv interface: reset(), step(), state().
"""

import random
from app.models import Observation, Action, Reward
from app.tasks import TASKS, TASK_BY_ID
from app.graders import grade_task, clamp_score


class SupportOpsEnv:
    """Customer support ticket resolution environment.

    The agent receives a customer support ticket and must resolve it
    through a sequence of actions (respond, escalate, close).
    """

    def __init__(self):
        self.current_task = None
        self.state_data = None
        self.steps = 0
        self.max_steps = 5
        self._done = False

    def reset(self, task_id: str = None) -> Observation:
        """Reset the environment and start a new episode.

        Args:
            task_id: Optional task identifier ("easy", "medium", "hard").
                     If None, a random task is selected.

        Returns:
            Initial observation for the episode.
        """
        if task_id and task_id in TASK_BY_ID:
            self.current_task = TASK_BY_ID[task_id]
        else:
            self.current_task = random.choice(TASKS)

        self.state_data = {
            "ticket_id": self.current_task["id"],
            "message": self.current_task["message"],
            "history": [],
            "status": "open",
        }
        self.steps = 0
        self._done = False

        return Observation(**self.state_data)

    def step(self, action: Action) -> tuple:
        """Execute one step in the environment.

        Args:
            action: The agent's action (action_type + content).

        Returns:
            (observation, reward, done, info) tuple.
        """
        self.steps += 1

        # Guard: auto-reset if no state exists
        if self.state_data is None:
            self.reset()

        # Guard: episode already finished
        if self._done:
            return (
                Observation(**self.state_data),
                Reward(score=0.01, reason="episode_already_done"),
                True,
                {},
            )

        # Record the agent's response in conversation history
        self.state_data["history"].append(action.content or "")

        # Apply action effects to environment state
        if action.action_type == "respond":
            # Certain keywords in the response can close the ticket
            content_lower = (action.content or "").lower()
            if any(w in content_lower for w in ("refund", "resolved", "fixed")):
                self.state_data["status"] = "closed"

        elif action.action_type == "close":
            self.state_data["status"] = "closed"

        elif action.action_type == "escalate":
            pass  # stays open but escalated logically

        # Grade the action
        try:
            reward_score, reason = grade_task(
                self.current_task, action, self.state_data
            )
        except Exception as e:
            reward_score, reason = 0.05, f"grader_error:{e}"

        # Final safety clamp — guarantees (0, 1) exclusive
        reward_score = clamp_score(reward_score)

        # Determine if episode is done
        self._done = (
            self.steps >= self.max_steps
            or self.state_data["status"] == "closed"
        )

        # Build safe observation
        try:
            obs = Observation(**self.state_data)
        except Exception:
            obs = Observation(
                ticket_id="T0", message="fallback", history=[], status="open"
            )

        return obs, Reward(score=reward_score, reason=reason), self._done, {}

    def state(self) -> dict:
        """Return the current environment state."""
        return self.state_data or {
            "ticket_id": "",
            "message": "",
            "history": [],
            "status": "open",
        }
