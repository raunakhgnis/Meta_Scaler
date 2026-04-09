"""Baseline inference script for SupportOpsEnv.

Uses the OpenAI-compatible API to run an LLM agent against all 3 tasks
and prints reproducible baseline scores.

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

if not API_KEY:
    print("[WARN] No API key found. Set HF_TOKEN or OPENAI_API_KEY.")
    print("[WARN] Running in fallback mode with default responses.")

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
    except Exception as e:
        print(f"  [LLM fallback] {type(e).__name__}: {e}")
        return json.dumps({
            "action_type": "respond",
            "content": "I apologize for the inconvenience. Let me help you with your issue. I will process your refund and resolve this matter."
        })


def parse_action(response_text: str) -> Action:
    """Parse LLM response into an Action, with fallback."""
    try:
        # Try to extract JSON from the response
        text = response_text.strip()
        # Handle markdown code blocks
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


# ── Main Loop ───────────────────────────────────────────────────────

def run_task(task_id: str) -> float:
    """Run a single task and return the final score."""
    obs = env.reset(task_id=task_id)
    step_scores = []

    print(f"\n{'='*60}")
    print(f"[TASK] {task_id} | Ticket: {obs.ticket_id}")
    print(f"[MSG]  {obs.message}")
    print(f"{'='*60}")

    done = False
    step_num = 0

    while not done:
        step_num += 1
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

        try:
            obs, reward, done, info = env.step(action)
            score = clamp_score(reward.score)
        except Exception as e:
            print(f"  [STEP ERROR] {e}")
            done = True
            score = 0.05

        step_scores.append(score)
        print(f"  [STEP {step_num}] action={action.action_type} | "
              f"reward={score:.4f} | done={done}")

    # Compute final task score
    if step_scores:
        avg = sum(step_scores) / len(step_scores)
    else:
        avg = 0.05

    final_score = clamp_score(avg)
    print(f"  [RESULT] task={task_id} | final_score={final_score:.4f}")
    return final_score


def main():
    """Run all tasks and print summary."""
    print("=" * 60)
    print("SupportOpsEnv — Baseline Inference")
    print(f"Model: {MODEL}")
    print(f"API:   {API_BASE}")
    print("=" * 60)

    results = {}
    for task in TASKS:
        task_id = task["id"]
        try:
            score = run_task(task_id)
        except Exception as e:
            print(f"  [TASK ERROR] {task_id}: {e}")
            score = 0.05
        results[task_id] = clamp_score(score)

    # Summary
    print(f"\n{'='*60}")
    print("BASELINE RESULTS")
    print(f"{'='*60}")
    for tid, sc in results.items():
        print(f"  {tid:8s} → {sc:.4f}")
    overall = sum(results.values()) / len(results) if results else 0.05
    print(f"  {'overall':8s} → {clamp_score(overall):.4f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
