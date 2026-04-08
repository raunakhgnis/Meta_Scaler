def grade_task(task, action, state):
    try:
        score = 0.0
        expected = task.get("expected", {})

        content = (action.content or "").lower()

        # ✅ Intent classification
        if action.action_type == "classify":
            if expected.get("intent", "") in content:
                score += 0.3

        # ✅ Improved response scoring
        # ✅ Better semantic matching
        if action.action_type == "respond":
            content_words = content.split()

            # flexible matching
            if any(word in content for word in ["sorry", "apologize", "apology"]):
                score += 0.3   # empathy

            if any(word in content for word in ["refund", "link", "support"]):
                score += 0.3   # helpfulness

            # bonus for detailed response
            if len(content_words) > 6:
                score += 0.2
        # if action.action_type == "respond":
        #     keywords = expected.get("response_contains", "").lower().split()

        #     # partial keyword match
        #     match_count = sum(1 for word in keywords if word in content)
        #     if len(keywords) > 0:
        #         score += 0.3 * (match_count / len(keywords))

        #     # empathy bonus
        #     if any(word in content for word in ["sorry", "apologize", "apology"]):
        #         score += 0.2

        #     # helpfulness bonus
        #     if any(word in content for word in ["refund", "link", "support"]):
        #         score += 0.2

        # ✅ Escalation
        if action.action_type == "escalate":
            if expected.get("escalation", False):
                score += 0.3

        # ✅ Close action
        if action.action_type == "close":
            score += 0.2

        # ✅ Penalty for too many steps
        if len(state.get("history", [])) > 4:
            score -= 0.2

        return max(0.0, min(1.0, score)), "graded"

    except Exception as e:
        return 0.0, f"error: {str(e)}"

# def grade_task(task, action, state):
#     try:
#         score = 0.0
#         expected = task.get("expected", {})

#         content = (action.content or "").lower()

#         # Intent classification
#         if action.action_type == "classify":
#             if expected.get("intent", "") in content:
#                 score += 0.3

#         # Response quality (IMPROVED)
#         if action.action_type == "respond":
#             keywords = expected.get("response_contains", "").lower()

#             if any(word in content for word in keywords.split()):
#                 score += 0.3

#             # bonus for good response
#             if len(content) > 20:
#                 score += 0.1

#             if "sorry" in content:
#                 score += 0.1

#         # Escalation
#         if action.action_type == "escalate":
#             if expected.get("escalation", False):
#                 score += 0.3

#         # Close
#         if action.action_type == "close":
#             score += 0.2

#         return min(1.0, score), "graded"

#     except Exception as e:
#         return 0.0, f"error: {str(e)}"

