"""Task definitions for SupportOpsEnv.

Each task represents a customer support ticket with a difficulty level.
Tasks are selectable by task_id during reset().
"""

TASKS = [
    {
        "id": "easy",
        "difficulty": "easy",
        "message": "Hi, I'd like to know my order status.",
        "keywords": ["order", "status", "track"],
        "description": "Simple order status inquiry - agent should respond politely with tracking information.",
    },
    {
        "id": "medium",
        "difficulty": "medium",
        "message": "I received a damaged product and want a refund or replacement.",
        "keywords": ["damaged", "refund", "replace", "product"],
        "description": "Product issue requiring resolution - agent must address the problem and offer refund/replacement.",
    },
    {
        "id": "hard",
        "difficulty": "hard",
        "message": "I was charged twice for my order, my account was suspended, and I can't reach anyone. This is urgent.",
        "keywords": ["charged", "twice", "suspended", "urgent", "account"],
        "description": "Multi-issue escalation - agent must handle billing, account, and communication issues efficiently.",
    },
]

# Quick lookup by task ID
TASK_BY_ID = {task["id"]: task for task in TASKS}