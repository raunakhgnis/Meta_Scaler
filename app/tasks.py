TASKS = [
    {
        "id": "T1",
        "difficulty": "easy",
        "message": "I want to reset my password",
        "expected": {
            "intent": "password_reset",
            "priority": "low",
            "response_contains": "reset link",
            "escalation": False
        }
    },
    {
        "id": "T2",
        "difficulty": "medium",
        "message": "My payment failed but money got deducted",
        "expected": {
            "intent": "payment_issue",
            "priority": "high",
            "response_contains": "refund",
            "escalation": True
        }
    },
    {
        "id": "T3",
        "difficulty": "hard",
        "message": "Your app charged me twice and support is ignoring me!",
        "expected": {
            "intent": "billing_complaint",
            "priority": "urgent",
            "response_contains": "apology",
            "tone": "empathetic",
            "escalation": True
        }
    }
]