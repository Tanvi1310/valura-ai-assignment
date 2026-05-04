# Valura AI Microservice

## Overview

This project is a small AI-powered backend service designed to help users understand and manage their investments.

The idea is simple:
A user asks a question → the system understands it → checks if it’s safe → routes it to the right logic → and responds in real time.

The focus of this assignment is to build the **core pipeline (spine)** of the system in a clean and scalable way.

---

## What this system does

* Blocks unsafe or risky financial queries
* Understands user intent using an LLM
* Routes requests to the correct agent
* Analyzes portfolio health (main implemented feature)
* Streams responses back in real time

---

## Architecture (How it works)

```
User Query
   ↓
Safety Guard (fast, local check)
   ↓
Intent Classifier (LLM)
   ↓
Router
   ↓
Agent (Portfolio Health / Stub)
   ↓
Streaming Response (SSE)
```

---

## Key Components

**1. Safety Guard**
A simple rule-based filter that blocks harmful queries before they reach the system.

**2. Intent Classifier**
Uses a single LLM call to:

* detect user intent
* extract important details (like stocks, amounts)
* decide which agent should handle the request

**3. Portfolio Health Agent**
Analyzes a user’s portfolio and gives:

* risk insights
* performance overview
* simple, useful observations

If the user has no portfolio, it guides them on how to start.

**4. Stub Agents**
Other agents are kept as placeholders so the system can scale easily later.

---

## How to Run

### 1. Clone the repo

```
git clone https://github.com/Tanvi1310/valura-ai-assignment.git
cd valura-ai-assignment
```

### 2. Create virtual environment

```
python -m venv venv
```

### 3. Activate it

```
venv\Scripts\activate
```

### 4. Install dependencies

```
pip install -r requirements.txt
```

### 5. Run the server

```
uvicorn src.valura.main:app --reload
```

### 6. Open in browser

```
http://127.0.0.1:8000
```

---

## Running Tests

```
pytest tests/ -v
```

All tests run without needing an API key (LLM is mocked in tests).

---

## Tech Stack

* Python
* FastAPI
* OpenAI API (for classification)
* SSE (streaming responses)
* Pytest

---

## Notes / Decisions

* Safety is handled before any AI call
* Only one LLM call is used for classification
* The system is modular, so new agents can be added easily
* In-memory storage is used for simplicity

Tanvi Gholap

