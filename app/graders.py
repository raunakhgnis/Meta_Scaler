def clamp_score(score: float) -> float:
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return score


def grade_task(task, action, state):
    try:
        score = 0.01

        content = (action.content or "").lower()

        if action.action_type == "respond":
            if "sorry" in content:
                score += 0.3
            if "refund" in content:
                score += 0.4
            if len(content.split()) > 5:
                score += 0.2

        elif action.action_type == "close":
            score += 0.2

        elif action.action_type == "escalate":
            score += 0.2

        if len(state.get("history", [])) > 3:
            score -= 0.1

        score = clamp_score(score)

        return score, "graded"

    except Exception as e:
        return 0.01, f"error: {str(e)}"
