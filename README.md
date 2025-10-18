# 🧩 TinyDSL

**TinyDSL** is a modular, agent-ready framework for exploring domain-specific languages (DSLs).
It currently supports two modes:

* 🎨 **Gli** — a graphics DSL for procedural image generation
* 🗣️ **Lexi** — a text DSL for structured, expressive text generation

Both are accessible through a FastAPI backend and can be invoked directly by LLM agents or REST clients.

---

## 🚀 Highlights

* Unified API for multiple DSLs (`/api/gli`, `/api/lexi`)
* Clean modular architecture with automatic CORS setup
* Controlled randomness and reproducibility
* Lightweight agent tool for integration with LangChain, OpenAI, or Autogen
* Example datasets for each DSL for quick testing

---

## ⚙️ Run Locally

```bash
pip install fastapi uvicorn matplotlib requests
uvicorn api.main:app --reload --port 8008
```

Then open [http://localhost:8008/docs](http://localhost:8008/docs) for the interactive API UI.

---

## 🧠 Example Usage

**Lexi (text)**

```dsl
set mood happy
say "Hello!"
repeat 2 { say "Have a wonderful day!" }
```

**Gli (image)**

```dsl
set color orange
repeat 10 {
  set size 3+$i
  draw circle x=cos($i*20)*$i*10 y=sin($i*20)*$i*10
}
```

---

## 🤖 Agent Integration

Agents can call the TinyDSL API through a simple Python tool:

```python
from agent_tool import TinyDSLTool
tool = TinyDSLTool(base_url="http://localhost:8008/api")
tool.run_lexi('set mood happy\nsay "Hi there!"')
```

---

## 📚 API Overview

| DSL   | Endpoint                      | Method | Purpose                |
| ----- | ----------------------------- | ------ | ---------------------- |
| Gli   | `/api/gli/run`                | POST   | Run graphics DSL code  |
| Gli   | `/api/gli/run_example/{id}`   | GET    | Execute stored example |
| Lexi  | `/api/lexi/run`               | POST   | Generate text from DSL |

---

## 🧩 Extend

Add a new DSL by creating an interpreter and router module under `/api/`, then include it in `main.py`.
TinyDSL auto-scales to support new modalities — code, music, or narrative — with the same unified interface.

---

Would you like me to include a **short “Agent Quick Start” section** (2-3 lines on connecting it to GPT-4 or LangChain)?
