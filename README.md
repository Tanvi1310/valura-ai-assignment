# Valura AI Microservice

## Overview

This project is a simple AI-powered backend service that helps users understand and manage their investments.

The system takes a user query, checks if it is safe, understands the intent using an LLM, routes it to the correct component, and streams the response back in real time.

The goal of this assignment was to build the **core pipeline (spine)** in a clean and scalable way.

---

## What the system does

* Filters unsafe or harmful financial queries
* Understands user intent using a single LLM call
* Extracts useful information (like stocks, amounts)
* Routes the request to the correct agent
* Provides portfolio health insights
* Streams responses back to the user

---

## Architecture (Flow)

```
User Query
   ↓
Safety Guard (fast local check)
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

**Safety Guard**
A rule-based filter that blocks harmful queries before they reach the system.

**Intent Classifier**
Uses one LLM call to:

* detect user intent
* extract entities
* decide which agent to call

**Portfolio Health Agent**
Analyzes the user’s portfolio and provides:

* concentration risk
* performance insights
* simple, useful observations

If the user has no portfolio, it guides them on how to start.

**Stub Agents**
Other agents are included as placeholders so the system can be extended easily.

---

## Persistence Choice

This project uses **in-memory storage** for session management.

The session history is stored using a dictionary and a bounded deque to keep only recent messages. A thread lock is used to make sure access is safe when multiple requests are handled.

This approach was chosen because:

* It is simple and fast
* No database setup is required
* Works well for a demo system

In a real-world system, this would be replaced with a database like PostgreSQL or Redis to store data permanently.

---

## Streaming

Responses are streamed using **Server-Sent Events (SSE)**.
This allows the client to receive data in real time instead of waiting for the full response.

---

## How to Run

### 1. Clone the repository

```
git clone https://github.com/Tanvi1310/valura-ai-assignment.git
cd valura-ai-assignment
```

### 2. Create virtual environment

```
python -m venv venv
```

### 3. Activate environment

```
venv\Scripts\activate
```

### 4. Install dependencies

```
pip install -r requirements.txt
```

### 5. Setup environment variables

```
cp .env.example .env
```

Add your OpenAI API key in `.env`

---

### 6. Run the server

```
uvicorn src.valura.main:app --reload
```

---

### 7. Open in browser

```
http://127.0.0.1:8000
```

---

## Running Tests

```
pytest tests/ -v
```

All tests run without needing an API key (LLM is mocked).

---

## Tech Stack

* Python
* FastAPI
* OpenAI API (for classification)
* SSE (streaming responses)
* Pytest
---
* Safety is handled before any LLM call
* Only one LLM call is used for classification
* The system is modular and easy to extend
* In-memory storage is used for simplicity
---

## Demo Video

https://drive.google.com/file/d/1LsG16nx-VVxtyHE9EFtt5T-OvMc0k41z/view?usp=sharing

---

Tanvi Gholap
