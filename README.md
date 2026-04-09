---
title: support-ops-env
emoji: 🎧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# SupportOpsEnv 🎧

A real-world **customer support ticket resolution** environment for training and evaluating AI agents via the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) interface.

## Motivation

Customer support is one of the most common real-world tasks that AI agents are being deployed for. This environment simulates realistic support ticket scenarios where an agent must:

- **Understand** the customer's problem from their message
- **Respond** with empathy, relevance, and accuracy
- **Resolve** the issue efficiently (minimize back-and-forth)
- **Escalate** or **close** tickets appropriately

Unlike toy environments, SupportOpsEnv rewards nuanced agent behavior — empathy, keyword relevance, brevity, and correct resolution — making it directly applicable to evaluating production support agents.

---

## Environment API

### `POST /reset`

Start a new episode. Optionally specify a task.

**Request body** (optional):
```json
{"task_id": "easy"}
```

**Response** — `Observation`:
```json
{
  "ticket_id": "easy",
  "message": "Hi, I'd like to know my order status.",
  "history": [],
  "status": "open"
}
```

### `POST /step`

Send an agent action and receive the next observation + reward.

**Request body** — `Action`:
```json
{
  "action_type": "respond",
  "content": "I'm sorry for the inconvenience. Let me look up your order status right away."
}
```

**Response** — `StepResponse`:
```json
{
  "observation": {
    "ticket_id": "easy",
    "message": "Hi, I'd like to know my order status.",
    "history": ["I'm sorry for the inconvenience..."],
    "status": "open"
  },
  "reward": 0.65,
  "done": false,
  "info": {}
}
```

### `GET /state`

Returns the current environment state (ticket, history, status).

### `GET /tasks`

Lists all available tasks with their difficulty and descriptions.

### `GET /health`

Health check — returns `{"status": "healthy"}`.

---

## Action Space

| Field         | Type   | Description                                    |
|---------------|--------|------------------------------------------------|
| `action_type` | `str`  | One of: `"respond"`, `"escalate"`, `"close"`   |
| `content`     | `str?` | Free-text response or note (optional)          |

## Observation Space

| Field       | Type       | Description                               |
|-------------|------------|-------------------------------------------|
| `ticket_id` | `str`      | Unique ticket identifier / task ID        |
| `message`   | `str`      | The customer's original message           |
| `history`   | `List[str]`| Conversation history (agent responses)    |
| `status`    | `str`      | Ticket status: `"open"` or `"closed"`     |

## Reward Design

Scores are **strictly in the open interval (0.0, 1.0)** — never exactly 0 or 1.

| Signal                      | Bonus   | Description                                  |
|-----------------------------|---------|----------------------------------------------|
| Empathy keywords            | +0.15   | "sorry", "apologize", "understand"           |
| Substantive response (>5w)  | +0.10   | Response has meaningful content              |
| Detailed response (>15w)    | +0.05   | Extra detail shows thoroughness              |
| Task-specific keywords      | +0.08–0.40 | Varies by difficulty                      |
| Offering resolution         | +0.15–0.20 | "refund", "replace", etc.                 |
| Efficient resolution (≤2 steps) | +0.12 | Resolving quickly (hard tasks)            |
| Penalty: dragging on (>4 steps) | −0.08 | Discourages unnecessary back-and-forth   |

---

## Tasks

### Easy — Order Status Inquiry
> "Hi, I'd like to know my order status."

Simple inquiry. Agent should respond politely with tracking information. A helpful, empathetic one-turn response scores well.

**Expected baseline score:** ~0.60–0.80

### Medium — Damaged Product
> "I received a damaged product and want a refund or replacement."

Product issue requiring resolution. Agent must acknowledge the damage and explicitly offer a refund or replacement. Keyword matching and empathy both matter.

**Expected baseline score:** ~0.40–0.65

### Hard — Multi-Issue Escalation
> "I was charged twice for my order, my account was suspended, and I can't reach anyone. This is urgent."

Complex multi-issue ticket. Agent must address billing, account suspension, and communication failure. Efficiency (resolving in ≤2 turns) earns a bonus. Requires combining empathy, problem acknowledgment, and resolution.

**Expected baseline score:** ~0.25–0.50

---

## Setup & Usage

### Prerequisites

- Python 3.10+
- An OpenAI-compatible API key

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.server:app --host 0.0.0.0 --port 7860

# In another terminal, run the baseline inference
python inference.py
```

### Environment Variables

| Variable        | Description                          | Default                        |
|-----------------|--------------------------------------|--------------------------------|
| `HF_TOKEN`      | API key (primary)                   | —                              |
| `OPENAI_API_KEY` | API key (fallback)                 | —                              |
| `API_BASE_URL`  | API base URL                        | `https://api.openai.com/v1`    |
| `MODEL_NAME`    | Model to use                        | `gpt-4o-mini`                  |

### Docker

```bash
docker build -t support-ops-env .
docker run -p 7860:7860 support-ops-env
```

### Hugging Face Spaces

This environment is designed to deploy as a Docker-based HF Space tagged with `openenv`.

---

## Baseline Scores

Baseline scores using `meta-llama/llama-3.3-70b-instruct` via OpenRouter:

| Task   | Score  |
|--------|--------|
| Easy   | ~0.70  |
| Medium | ~0.55  |
| Hard   | ~0.35  |

*Scores vary slightly due to LLM response variability. The `clamp_score()` function ensures all values remain in (0.01, 0.99).*

---

## Project Structure

```
├── app/
│   ├── __init__.py       # Package init
│   ├── models.py         # Pydantic: Observation, Action, Reward
│   ├── tasks.py          # Task definitions (easy/medium/hard)
│   ├── graders.py        # Deterministic grading logic
│   ├── env.py            # SupportOpsEnv: reset/step/state
│   └── server.py         # FastAPI endpoints
├── server/
│   └── app.py            # Alternative entry point
├── inference.py          # Baseline inference script
├── openenv.yaml          # OpenEnv manifest
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
└── README.md             # This file
```

---

## License

MIT