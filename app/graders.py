"""Graders for SupportOpsEnv tasks.

Every grader returns a score strictly in (0.0, 1.0) — never the boundary values.
The clamp_score helper guarantees this invariant.
"""


def clamp_score(score: float) -> float:
    """Clamp score to the open interval (0.0, 1.0).

    Uses 0.01 and 0.99 as boundary replacements so that the validator
    never sees exactly 0.0 or 1.0.
    """
    if not isinstance(score, (int, float)):
        return 0.05
    score = float(score)
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return round(score, 4)  # avoid floating-point noise


def grade_task(task: dict, action, state: dict) -> tuple:
    """Grade an agent action for a given task.

    Returns:
        (score, reason) where score is in (0.0, 1.0).
    """
    try:
        difficulty = task.get("difficulty", "easy")
        content = (action.content or "").lower().strip()
        action_type = (action.action_type or "").lower().strip()
        score = 0.05  # baseline — always > 0.0

        # ── Common quality signals ──────────────────────────────────
        if action_type == "respond":
            # Empathy bonus
            if any(w in content for w in ("sorry", "apologize", "apologies", "understand")):
                score += 0.15

            # Substantive response bonus (more than a few words)
            word_count = len(content.split())
            if word_count > 5:
                score += 0.10
            if word_count > 15:
                score += 0.05

            # ── Difficulty-specific grading ──────────────────────────
            if difficulty == "easy":
                # Easy: polite, helpful response is enough
                if any(w in content for w in ("help", "assist", "track", "status", "order")):
                    score += 0.40
                if "happy to" in content or "glad to" in content:
                    score += 0.10

            elif difficulty == "medium":
                # Medium: must acknowledge the damage and offer remedy
                keywords = task.get("keywords", [])
                matched = sum(1 for kw in keywords if kw in content)
                score += 0.12 * min(matched, 3)
                if "refund" in content or "replace" in content:
                    score += 0.20

            elif difficulty == "hard":
                # Hard: must address multiple issues, resolve efficiently
                keywords = task.get("keywords", [])
                matched = sum(1 for kw in keywords if kw in content)
                score += 0.08 * min(matched, 4)
                if state.get("status") == "closed":
                    score += 0.15
                # Efficiency bonus — resolving quickly is rewarded
                history_len = len(state.get("history", []))
                if history_len <= 2:
                    score += 0.12
                elif history_len <= 3:
                    score += 0.06

        elif action_type == "escalate":
            score += 0.10 if difficulty == "hard" else 0.05

        elif action_type == "close":
            if state.get("status") == "closed":
                score += 0.15
            else:
                score += 0.03  # premature close gets minimal credit

        # ── Penalty for dragging on too long ────────────────────────
        history_len = len(state.get("history", []))
        if history_len > 4:
            score -= 0.08
        if history_len > 6:
            score -= 0.08  # cumulative penalty

        return clamp_score(score), f"graded:{difficulty}"

    except Exception as e:
        return 0.05, f"grader_error:{e}"
