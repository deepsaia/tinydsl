# 🧩 TinyDSL

**TinyDSL** is a modular, agent-ready framework for exploring and testing domain-specific languages (DSLs).  
It currently supports two DSLs:

* 🎨 **Gli** — a graphics DSL for procedural image generation  
* 🗣️ **Lexi** — a text DSL for structured, expressive text generation and reasoning  

Both are served via a unified **FastAPI backend** and are designed to be invoked by **LLM agents** or external REST clients.

---

## ⚙️ Get Started

Use [uv](https://github.com/astral-sh/uv) for lightweight environment management:

```bash
uv venv
uv sync
python -m api.main
````

Then open [http://localhost:8008/docs](http://localhost:8008/docs) for the interactive API UI.

---

## 🧠 Example Usage

### **Lexi (Text DSL)**

```dsl
set mood happy
say "Hello!"
repeat 2 { say "Have a wonderful day!" }
```

Lexi supports memory persistence:

```dsl
remember name = "John Arthur"
recall name
```

### **Gli (Graphics DSL)**

```dsl
set color orange
repeat 10 {
  set size 3+$i
  draw circle x=cos($i*20)*$i*10 y=sin($i*20)*$i*10
}
```

Images are saved to `/output` with timestamped filenames.

---

## 🚀 Highlights

- Unified API for multiple DSLs (`/api/gli`, `/api/lexi`)
- Persistent, session-safe memory for Lexi (`/api/lexi/memory`)
- Built-in benchmark tasks and evaluation metrics
- Lightweight agent tool (`TinyDSLTool`) for integration with LangChain, Autogen, or OpenAI agents
- Simple modular structure to add new DSLs (e.g., music, logic, or code)

---

## 🤖 Agent Integration

Agents or Python scripts can call TinyDSL directly using the included tool:

```python
from agent_tool import TinyDSLTool

tool = TinyDSLTool(base_url="http://localhost:8008/api")

# Run Lexi DSL
lexi_code = 'set mood happy\nsay "Hello there!"'
print(tool.run_lexi(lexi_code)["output"])

# Run a benchmark task
print(tool.run_lexi_task("005"))

# View and clear Lexi memory
print(tool.get_memory())
tool.clear_memory()
```

---

## 📚 API Overview

| DSL  | Endpoint                    | Method | Purpose                         |
| ---- | --------------------------- | ------ | ------------------------------- |
| Gli  | `/api/gli/run`              | POST   | Run graphics DSL code           |
| Gli  | `/api/gli/run_example/{id}` | GET    | Execute stored example          |
| Lexi | `/api/lexi/run`             | POST   | Execute Lexi DSL code           |
| Lexi | `/api/lexi/task`            | POST   | Run a predefined benchmark task |
| Lexi | `/api/lexi/eval`            | POST   | Evaluate multiple outputs       |
| Lexi | `/api/lexi/memory`          | GET    | View persistent memory          |
| Lexi | `/api/lexi/memory/clear`    | POST   | Clear memory                    |
| Lexi | `/api/lexi/memory/set`      | POST   | Set key-value in memory         |

---

## 🧩 Extend

Add a new DSL by creating:

* An interpreter (`<dsl_name>.py`)
* An API router (`routes_<dsl_name>.py`)
* Example data or evaluation JSONs (optional)

Then register it in `api/main.py`.
TinyDSL’s modular design supports quick experimentation for **acquire-and-apply learning** across multiple DSLs.

---

## 🧭 Agent Workflow Example

TinyDSL is built for agent-based experiments testing **acquisition, consolidation, and transfer** of new skills.
A typical loop looks like this:

1. **Discover Tasks**
   The agent fetches all available benchmark tasks:

   ```python
   tasks = [tool.run_lexi_task(tid) for tid in ["001", "002"]]
   ```

2. **Execute & Learn**
   The agent runs Lexi or Gli code, storing intermediate results in memory:

   ```python
   tool.run_lexi('remember mood = "happy"')
   tool.run_lexi('if mood is happy { say "Training complete!" }')
   ```

3. **Evaluate**
   After training or inference, results are scored automatically:

   ```python
   results = [{"task_id": "002", "output": "You look great today!"}]
   print(tool.eval_lexi_outputs(results))
   ```

4. **Persist State**
   Memory is persisted across sessions to simulate **skill retention**:

   ```python
   print(tool.get_memory())  # See consolidated knowledge
   ```

5. **Transfer Test**
   Clear memory and test new unseen compositions:

   ```python
   tool.clear_memory()
   tool.run_lexi_task("020")  # Multi-step reasoning
   ```

---

With this flow, LLM agents can **learn a new DSL in one session** and **apply it in another**, making TinyDSL a foundation for studying *continual learning, compositional reasoning, and symbolic generalization*.

---
