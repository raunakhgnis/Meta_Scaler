TASKS = [
    {
        "id": "T1",
        "difficulty": "easy",
        "message": "Hi, I'd like to know my order status.",
        "keywords": ["order", "status", "track"],
    },
    {
        "id": "T2",
        "difficulty": "medium",
        "message": "I received a damaged product and want a refund or replacement.",
        "keywords": ["damaged", "refund", "replace", "product"],
    },
    {
        "id": "T3",
        "difficulty": "hard",
        "message": "I was charged twice for my order, my account was suspended, and I can't reach anyone. This is urgent.",
        "keywords": ["charged", "twice", "suspended", "urgent", "account"],
    },
]

# TASKS = [
#     {
#         "id": "T1",
#         "difficulty": "easy",
#         "message": "I want to reset my password",
#         "expected": {
#             "intent": "password_reset",
#             "priority": "low",
#             "response_contains": "reset link",
#             "escalation": False
#         }
#     },
#     {
#         "id": "T2",
#         "difficulty": "medium",
#         "message": "My payment failed but money got deducted",
#         "expected": {
#             "intent": "payment_issue",
#             "priority": "high",
#             "response_contains": "refund",
#             "escalation": True
#         }
#     },
#     {
#         "id": "T3",
#         "difficulty": "hard",
#         "message": "Your app charged me twice and support is ignoring me!",
#         "expected": {
#             "intent": "billing_complaint",
#             "priority": "urgent",
#             "response_contains": "apology",
#             "tone": "empathetic",
#             "escalation": True
#         }
#     }
# ]