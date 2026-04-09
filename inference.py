from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI
from app.env import SupportOpsEnv
from app.models import Action

# ✅ Safe env loading
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

        # handle empty response
        if not content:
            raise ValueError("Empty response")

        return content

    except Exception as e:
        # fallback response
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

        # ✅ SAFE LLM CALL
        response_text = safe_llm_call(prompt)

        # ✅ SAFE PARSE
        action = parse_action(response_text)

        try:
            obs, reward, done, _ = env.step(action)
        except Exception:
            # fallback env step
            done = True
            reward = type("obj", (), {"score": 0.0})()
            obs = obs

        total_reward += reward.score

        print("[STEP]", {
            "action": action.model_dump(),
            "reward": reward.score,
            "done": done
        })

    print("[END]", {"total_reward": total_reward})


if __name__ == "__main__":
    for _ in range(3):
        try:
            run_task()
        except Exception as e:
            print("[END]", {"total_reward": 0.0, "error": str(e)})

# from dotenv import load_dotenv
# load_dotenv()

# import os
# import json
# from openai import OpenAI
# from app.env import SupportOpsEnv
# from app.models import Action

# # ✅ Correct environment variables
# API_BASE = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
# MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# client = OpenAI(
#     api_key=os.getenv("HF_TOKEN"),   # 🔥 FIXED (MANDATORY)
#     base_url=API_BASE
# )

# env = SupportOpsEnv()


# def run_task():
#     obs = env.reset()
#     total_reward = 0

#     print("[START]", obs.model_dump())

#     done = False

#     while not done:
#         prompt = f"""
# You are a customer support agent.

# Ticket: {obs.message}
# History: {obs.history}
# Status: {obs.status}

# Return ONLY JSON:
# {{"action_type": "...", "content": "..."}}
# """

#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=[{"role": "user", "content": prompt}]
#         )

#         try:
#             action_json = json.loads(response.choices[0].message.content)
#             action = Action(**action_json)
#         except:
#             action = Action(
#                 action_type="respond",
#                 content="We are checking your issue."
#             )

#         obs, reward, done, _ = env.step(action)
#         total_reward += reward.score

#         print("[STEP]", {
#             "action": action.model_dump(),
#             "reward": reward.score,
#             "done": done
#         })

#     print("[END]", {"total_reward": total_reward})


# if __name__ == "__main__":
#     for _ in range(3):
#         run_task()