def clamp_score(score: float) -> float:
    """Strictly enforce (0, 1) exclusive."""
    return max(0.01, min(0.99, float(score)))


def grade_task(task, action, state) -> tuple[float, str]:
    try:
        difficulty = task.get("difficulty", "easy")
        content = (action.content or "").lower()
        score = 0.05  # baseline > 0.0

        if action.action_type == "respond":
            if "sorry" in content or "apologize" in content:
                score += 0.20
            if len(content.split()) > 5:
                score += 0.15

            if difficulty == "easy":
                # Easy: just responding politely is enough
                if "help" in content:
                    score += 0.40

            elif difficulty == "medium":
                # Medium: must address the specific issue
                keywords = task.get("keywords", [])
                matched = sum(1 for kw in keywords if kw in content)
                score += 0.15 * min(matched, 3)
                if "refund" in content or "replace" in content:
                    score += 0.25

            elif difficulty == "hard":
                # Hard: must resolve AND close correctly
                keywords = task.get("keywords", [])
                matched = sum(1 for kw in keywords if kw in content)
                score += 0.10 * min(matched, 4)
                if state.get("status") == "closed":
                    score += 0.20
                if len(state.get("history", [])) <= 2:
                    score += 0.15  # bonus for efficiency

        elif action.action_type == "escalate":
            score += 0.10 if difficulty == "hard" else 0.05

        elif action.action_type == "close":
            score += 0.15 if state.get("status") == "closed" else 0.05

        # Penalty for dragging on too long
        if len(state.get("history", [])) > 4:
            score -= 0.10

        return clamp_score(score), f"graded:{difficulty}"

    except Exception as e:
        return 0.05, f"error:{e}"

# def clamp_score(score: float) -> float:
#     if score <= 0.0:
#         return 0.01
#     if score >= 1.0:
#         return 0.99
#     return score


# def grade_task(task, action, state):
#     try:
#         score = 0.01

#         content = (action.content or "").lower()

#         if action.action_type == "respond":
#             if "sorry" in content:
#                 score += 0.3
#             if "refund" in content:
#                 score += 0.4
#             if len(content.split()) > 5:
#                 score += 0.2

#         elif action.action_type == "close":
#             score += 0.2

#         elif action.action_type == "escalate":
#             score += 0.2

#         if len(state.get("history", [])) > 3:
#             score -= 0.1

#         score = clamp_score(score)

#         return score, "graded"

#     except Exception as e:
#         return 0.01, f"error: {str(e)}"
