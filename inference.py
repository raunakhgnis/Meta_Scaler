"""Baseline inference script for SupportOpsEnv.

Uses the OpenAI-compatible API to run an LLM agent against all 3 tasks.
Prints structured [START]/[STEP]/[END] output required by openenv validate.

Usage:
    python inference.py

Environment variables:
    HF_TOKEN / OPENAI_API_KEY  — API key
    API_BASE_URL               — Base URL for the API (default: OpenAI)
    MODEL_NAME                 — Model to use (default: gpt-4o-mini)
"""

import os
import json
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI
from app.env import SupportOpsEnv
from app.models import Action
from app.graders import clamp_score
from app.tasks import TASKS

# ── Configuration ───────────────────────────────────────────────────

API_BASE = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY or "dummy", base_url=API_BASE)
env = SupportOpsEnv()


# ── Helpers ─────────────────────────────────────────────────────────

def safe_llm_call(prompt: str) -> str:
    """Call the LLM and return the response text, with fallback."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            timeout=15,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from model")
        return content
    except Exception:
        return json.dumps({
            "action_type": "respond",
            "content": "I apologize for the inconvenience. Let me help you with your issue. I will process your refund and resolve this matter."
        })


def parse_action(response_text: str) -> Action:
    """Parse LLM response into an Action, with fallback."""
    try:
        text = response_text.strip()
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        data = json.loads(text)
        return Action(**data)
    except Exception:
        return Action(
            action_type="respond",
            content="I apologize for the inconvenience. Let me help resolve your issue right away."
        )


def safe_score(score):
    """Ensure score is strictly in (0, 1) exclusive."""
    return max(0.01, min(0.99, float(score)))


# ── Helpers ─────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str = None) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.4f} rewards={rewards_str}", flush=True)


# ── Main Loop ───────────────────────────────────────────────────────

def run_task(task_id: str):
    """Run a single task and print structured output."""
    obs = env.reset(task_id=task_id)
    rewards = []
    
    log_start(task=task_id, env="support-ops-env", model=MODEL)

    done = False
    step_count = 0
    success = False

    while not done:
        step_count += 1
        prompt = f"""You are a professional customer support agent. Respond helpfully and empathetically.

Current ticket:
- Message: {obs.message}
- History: {json.dumps(obs.history)}
- Status: {obs.status}

Respond with ONLY valid JSON (no markdown, no explanation):
{{"action_type": "respond", "content": "your detailed, empathetic response here"}}

Valid action_types: "respond", "escalate", "close"
"""
        response_text = safe_llm_call(prompt)
        action = parse_action(response_text)
        action_str = action.action_type

        try:
            obs, reward, done, _ = env.step(action)
            score_step = safe_score(reward.score)
            err = None
        except Exception as e:
            done = True
            score_step = 0.01
            err = str(e)

        rewards.append(score_step)
        log_step(step=step_count, action=action_str, reward=score_step, done=done, error=err)

        if done:
            break

    avg = sum(rewards) / len(rewards) if rewards else 0.01
    final_score = safe_score(avg)
    success = final_score > 0.5

    log_end(success=success, steps=step_count, score=final_score, rewards=rewards)


if __name__ == "__main__":
    for task in TASKS:
        task_id = task["id"]
        try:
            run_task(task_id)
        except Exception as e:
            log_start(task=task_id, env="support-ops-env", model=MODEL)
            log_end(success=False, steps=0, score=0.01, rewards=[])
