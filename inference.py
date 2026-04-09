from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI
from app.env import SupportOpsEnv
from app.models import Action

API_BASE = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("HF_TOKEN")

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

env = SupportOpsEnv()


def safe_llm_call(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            timeout=10
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Empty response")

        return content

    except Exception:
        return json.dumps({
            "action_type": "respond",
            "content": "We are checking your issue."
        })


def parse_action(response_text):
    try:
        return Action(**json.loads(response_text))
    except Exception:
        return Action(
            action_type="respond",
            content="We are checking your issue."
        )


def safe_score(score):
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return score


def run_task():
    obs = env.reset()
    total_reward = 0.01

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

        response_text = safe_llm_call(prompt)
        action = parse_action(response_text)

        try:
            obs, reward, done, _ = env.step(action)
            score = safe_score(reward.score)

        except Exception:
            done = True
            score = 0.01
            obs = obs

        total_reward += score

        print("[STEP]", {
            "action": action.model_dump(),
            "reward": score,
            "done": done
        })

    print("[END]", {"total_reward": safe_score(total_reward)})


if __name__ == "__main__":
    for _ in range(3):
        try:
            run_task()
        except Exception as e:
            print("[END]", {
                "total_reward": 0.01,
                "error": str(e)
            })

