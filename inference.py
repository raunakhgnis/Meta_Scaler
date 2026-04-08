from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI
from app.env import SupportOpsEnv
from app.models import Action

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)

MODEL = os.getenv("MODEL_NAME")

env = SupportOpsEnv()


def run_task():
    obs = env.reset()
    total_reward = 0

    print("[START]", obs.model_dump())

    done = False

    while not done:
        prompt = f"""
You are a customer support agent.

Ticket: {obs.message}
History: {obs.history}
Status: {obs.status}

Return ONLY JSON:
{{"action_type": "...", "content": "..."}}
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            action_json = json.loads(response.choices[0].message.content)
            action = Action(**action_json)
        except:
            action = Action(
                action_type="respond",
                content="We are checking your issue."
            )

        obs, reward, done, _ = env.step(action)
        total_reward += reward.score

        print("[STEP]", {
            "action": action.model_dump(),
            "reward": reward.score,
            "done": done
        })

    print("[END]", {"total_reward": total_reward})


if __name__ == "__main__":
    for _ in range(3):
        run_task()