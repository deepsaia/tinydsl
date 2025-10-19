# 🧩 TinyDSL

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**TinyDSL** is a modular, agent-ready framework for exploring and testing domain-specific languages (DSLs).
It currently supports two DSLs:

* 🎨 **Gli** — a graphics DSL for procedural image generation
* 🗣️ **Lexi** — a text DSL for structured, expressive text generation and reasoning

Both are served via a unified **FastAPI backend** and are designed to be invoked by **LLM agents** or external REST clients.

---

## ⚙️ Get Started

Use [uv](https://github.com/astral-sh/uv):

```bash
uv venv
uv sync
python -m tinydsl.api.main
```

Open [http://localhost:8008/docs](http://localhost:8008/docs).

---

## 🧠 Example Usage

### **Lexi (Text DSL)**

```dsl
set mood happy
say "Hello!"
repeat 2 { say "Have a wonderful day!" }
```

Lexi supports persistent memory:

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

Images save to `/output` as `{id}_{name}_{YYYYMMDD_HHMMSS}.png` (when `id`/`name` provided).

---

## 🚀 What’s New

* **Lark everywhere**

  * `lark_lexi_parser` and `lark_gli_parser` now power both DSLs.
  * Deterministic, extensible grammars; clearer errors.

* **Pillow renderer by default (Gli)**

  * Crisp, anti-aliased output via supersampling.
  * Matplotlib still available if you want it.

* **Smarter inline math**

  * `$i` loop index, `pi`, `e` available.
  * Natural expressions like `10+$i*5` work.
  * `calc(...)` remains for explicit math.

* **AST endpoint (Lexi)**

  * Get parse trees to inspect/visualize your programs.

* **Stable filenames**

  * Artifacts saved as `{id}_{name}_{timestamp}.png` when `id` and/or `name` provided.

---

## 📚 API Overview

| DSL  | Endpoint                    | Method | Purpose                           |
| ---- | --------------------------- | ------ | --------------------------------- |
| Gli  | `/api/gli/run`              | POST   | Run graphics DSL code             |
| Gli  | `/api/gli/run_example/{id}` | GET    | Execute stored example            |
| Lexi | `/api/lexi/run`             | POST   | Execute Lexi DSL code             |
| Lexi | `/api/lexi/task`            | POST   | Run a predefined benchmark task   |
| Lexi | `/api/lexi/eval`            | POST   | Evaluate multiple outputs         |
| Lexi | `/api/lexi/memory`          | GET    | View persistent memory            |
| Lexi | `/api/lexi/memory/clear`    | POST   | Clear memory                      |
| Lexi | `/api/lexi/memory/set`      | POST   | Set key-value in memory           |
| Lexi | `/api/lexi/ast`             | POST   | Get AST (raw dict / pretty / DOT) |

---

## 🔧 Quick Calls

### Run **Lexi**

```bash
curl -X POST http://localhost:8008/api/lexi/run \
  -H 'Content-Type: application/json' \
  -d '{"code":"set mood happy\nsay \"Hello!\""}'
```

### Get **Lexi AST**

```bash
curl -X POST http://localhost:8008/api/lexi/ast \
  -H 'Content-Type: application/json' \
  -d '{"code":"say \"Hi\"","include_pretty":true,"include_dot":false}'
```

### Run **Gli** (Pillow default)

```bash
curl -X POST http://localhost:8008/api/gli/run \
  -H 'Content-Type: application/json' \
  -d '{"id":"adhoc_001","name":"blue_circle","code":"set color blue\nset size 10\ndraw circle x=50 y=50","save":true}'
```

### Run a stored **Gli** example

```bash
curl "http://localhost:8008/api/gli/run_example/003?save=true&engine=pillow"
```

---

## 🤖 Agent Integration

```python
from tinydsl.agent_tools.tinydsl_tool import TinyDSLTool

tool = TinyDSLTool(base_url="http://localhost:8008/api")
print(tool.run_lexi('say "Hello there!"')["output"])
print(tool.run_lexi_task("005"))
print(tool.get_memory()); tool.clear_memory()
```

---

## 📦 Data & Files

* Examples & grammars live under `src/tinydsl/data/`

  * `gli_examples.json`, `gli_grammar.lark`
  * `lexi_tasks.json`, `lexi_grammar.lark`
* Outputs: `./output/` (images, `lexi_memory.json`)

You can override data paths with env vars:
`GLI_EXAMPLES_PATH`, `GLI_GRAMMAR_PATH`, `LEXI_TASKS_PATH`, `LEXI_GRAMMAR_PATH`.

---

## 🧩 Extend

Add a new DSL by creating:

* Parser + transformer (`parser/lark_<dsl>.py`)
* Interpreter (`<dsl>/<dsl>.py`)
* API router (`api/routes_<dsl>.py`)
* Optional: examples + tasks JSON

Register it in `api/main.py`.
TinyDSL’s modular design makes it easy to study **continual learning, compositional reasoning, and symbolic generalization** across DSLs.

---

## 🪪 License

Licensed under the **Apache License, Version 2.0**.  
See [LICENSE](LICENSE) for details.

---
