# CONTRIBUTION.md

Thanks for helping improve **TinyDSL**! This doc keeps contributions fast and friction-free.

---

## Ways to Contribute

* 🐞 Report bugs (clear steps + expected vs. actual)
* 🧪 Add/expand tests
* ✍️ Improve docs (README, examples)
* 🧩 Add or extend DSL rules/transformers
* 🎨 Contribute new **Gli** examples or **Lexi** tasks
* 🔌 Add a new DSL (parser + interpreter + router)

---

## Dev Setup

```bash
# 1) create env
uv venv
uv sync

# 2) run API
python -m tinydsl.api.main  # http://localhost:8008/docs
```

**Optional env vars**

```
GLI_EXAMPLES_PATH, GLI_GRAMMAR_PATH
LEXI_TASKS_PATH,   LEXI_GRAMMAR_PATH
```

---

## Branch & PR

* Create a feature branch: `feat/<area>-<short-desc>` or `fix/<issue-id>`
* Keep PRs focused & < ~300 lines when possible
* Link related issues and add a brief rationale in the PR description
* Include before/after behavior in the PR (screenshots for Gli welcome)

---

## Code Style

* Python ≥ 3.11, type hints everywhere (`mypy`-friendly)
* Prefer small, composable functions; keep public APIs stable
* Follow existing module layout:

  * `parser/` → Lark grammars & transformers
  * `lexi/`, `gli/` → interpreters, renderers
  * `api/` → FastAPI routers
  * `data/` → grammars, examples, tasks

*(If you use formatters/linters, stick to Black-ish formatting & Ruff-ish rules.)*

---

## Testing

* Add tests for grammar changes and interpreter behavior
* Include failure cases (bad tokens, invalid params)
* For Gli, avoid pixel assertions—assert **shape lists** from the parser, not images

---

## Updating Grammars (Lark)

* Keep grammars unambiguous (avoid reduce/reduce)
* If adding math-like features, prefer explicit `calc(...)` or scoped rules
* Mirror transformer method names to grammar rule labels
* Update minimal examples in `data/*.json`

---

## Adding Gli Examples / Lexi Tasks

* **Gli**: one-liners or compact snippets; use `$i`, `sin`, `cos` for variety
  Ensure output renders with **Pillow** by default.
* **Lexi**: keep tasks small; include `name`, `difficulty`, `goal`, `expected_output`
  Make sure tasks run via `/api/lexi/task`.

---

## API Changes

* Keep endpoints backward compatible
* Document new query/body params in router docstrings
* Update README tables if you add endpoints
* Return clear JSON errors (`detail`) with actionable hints

---

## New DSL Checklist

1. Grammar + transformer (`parser/lark_<dsl>_parser.py`)
2. Interpreter (`<dsl>/<dsl>.py`)
3. Router (`api/routes_<dsl>.py`)
4. Example data (`data/<dsl>_examples.json`)
5. Register router in `api/main.py`
6. README + short usage snippet

---

## Release Checklist

* All tests pass locally
* Examples render & save to `/output`
* README / CONTRIBUTION updated
* Version bump (if applicable)

---

## Code of Conduct

Be kind, constructive, and inclusive. We value curiosity and clear communication.

---
