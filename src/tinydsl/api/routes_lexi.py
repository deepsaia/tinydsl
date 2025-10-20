from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tinydsl.lexi.lexi import LexiInterpreter
from tinydsl.lexi.lexi_evaluator import LexiEvaluator
from tinydsl.api.common_handlers import DSLHandler
import os

from tinydsl.core.memory import JSONFileMemory

memory_store = JSONFileMemory(filepath="memory/lexi_memory.json")

router = APIRouter()

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")

LEXI_TASKS_PATH = os.getenv(
    "LEXI_TASKS_PATH", os.path.join(data_dir, "lexi_tasks.json")
)
LEXI_GRAMMAR_PATH = os.getenv(
    "LEXI_GRAMMAR_PATH", os.path.join(data_dir, "lexi_grammar.lark")
)

# Initialize common handler
handler = DSLHandler(
    dsl_class=LexiInterpreter,
    evaluator_class=LexiEvaluator,
    tasks_path=LEXI_TASKS_PATH,
    dsl_name="lexi",
    grammar_path=LEXI_GRAMMAR_PATH,
)


# ---------- Request Schemas ----------
class LexiRequest(BaseModel):
    code: str


class TaskRequest(BaseModel):
    task_id: str


class EvalRequest(BaseModel):
    results: list  # list of { "task_id": "...", "output": "..." }


class ASTRequest(BaseModel):
    code: str
    include_pretty: bool = True
    include_dot: bool = False


@router.get("/memory")
def get_lexi_memory():
    """Retrieve persistent Lexi memory contents."""
    try:
        mem = memory_store.load()
        return JSONResponse({"status": "ok", "memory": mem})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/clear")
def clear_lexi_memory():
    """Clear persistent Lexi memory."""
    try:
        memory_store.clear()
        return JSONResponse({"status": "ok", "message": "Memory cleared."})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/set")
def set_lexi_memory(item: dict):
    """Set a specific memory key-value pair."""
    try:
        key, value = next(iter(item.items()))
        memory_store.set(key, value)
        return JSONResponse({"status": "ok", "key": key, "value": value})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Core Run ----------
def _lexi_run_processor(dsl_instance, output):
    """Custom processor for Lexi /run endpoint to include memory."""
    mem_data = {}
    if hasattr(dsl_instance, "memory"):
        if hasattr(dsl_instance.memory, "to_dict"):  # JSONFileMemory
            mem_data = dsl_instance.memory.to_dict()
        elif isinstance(dsl_instance.memory, dict):
            mem_data = dsl_instance.memory
    return {"status": "ok", "output": output, "memory": mem_data}


@router.post("/run")
def run_lexi(request: LexiRequest):
    """Run a Lexi DSL script and return generated text."""
    response = handler.handle_run(code=request.code, process_output=_lexi_run_processor)
    return JSONResponse(response)


# ---------- Task Execution ----------
@router.post("/task")
def run_lexi_task(request: TaskRequest):
    """Run a predefined Lexi task from benchmark JSON."""
    response = handler.handle_task(task_id=request.task_id)
    return JSONResponse(response)


# ---------- Evaluation ----------
@router.post("/eval")
def evaluate_lexi_outputs(request: EvalRequest):
    """Evaluate multiple Lexi outputs against benchmark expectations."""
    response = handler.handle_eval(results=request.results)
    return JSONResponse(response)


@router.post("/ast")
def lexi_ast(request: ASTRequest):
    """
    Parse Lexi code and return its AST.
    Returns:
      - tree: JSON-serializable AST (type/children/tokens)
      - pretty: human-readable tree dump (optional)
      - dot: Graphviz DOT string (optional)
    """
    response = handler.handle_ast(
        code=request.code,
        include_pretty=request.include_pretty,
        include_dot=request.include_dot,
    )
    return JSONResponse(response)
