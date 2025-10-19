from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tinydsl.src.tinydsl.lexi import LexiInterpreter
from tinydsl.src.tinydsl.lexi_evaluator import LexiEvaluator
import json
import os

from tinydsl.src.tinydsl.lexi_memory import LexiMemoryStore

memory_store = LexiMemoryStore()

router = APIRouter()

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")

LEXI_TASKS_PATH = os.getenv("LEXI_TASKS_PATH", os.path.join(data_dir, "lexi_tasks.json"))
LEXI_EVALUATOR = LexiEvaluator(LEXI_TASKS_PATH)


# ---------- Request Schemas ----------
class LexiRequest(BaseModel):
    code: str


class TaskRequest(BaseModel):
    task_id: str


class EvalRequest(BaseModel):
    results: list  # list of { "task_id": "...", "output": "..." }


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
@router.post("/run")
def run_lexi(request: LexiRequest):
    """Run a Lexi DSL script and return generated text."""
    try:
        lexi = LexiInterpreter()
        lexi.parse(request.code)
        result = lexi.render()
        mem_data = {}
        if hasattr(lexi, "memory"):
            if hasattr(lexi.memory, "load"):  # LexiMemoryStore
                mem_data = lexi.memory.load()
            elif isinstance(lexi.memory, dict):
                mem_data = lexi.memory

        return JSONResponse({"status": "ok", "output": result, "memory": mem_data})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Task Execution ----------
@router.post("/task")
def run_lexi_task(request: TaskRequest):
    """Run a predefined Lexi task from benchmark JSON."""
    try:
        with open(LEXI_TASKS_PATH, "r") as f:
            tasks = json.load(f)
        task = next((t for t in tasks if t["id"] == request.task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        lexi = LexiInterpreter()
        lexi.parse(task["code"])
        result = lexi.render()
        return JSONResponse(
            {
                "status": "ok",
                "task_id": task["id"],
                "task_name": task["name"],
                "expected_output": task["expected_output"],
                "generated_output": result,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Evaluation ----------
@router.post("/eval")
def evaluate_lexi_outputs(request: EvalRequest):
    """Evaluate multiple Lexi outputs against benchmark expectations."""
    try:
        report = LEXI_EVALUATOR.batch_evaluate(request.results)
        return JSONResponse(
            {
                "status": "ok",
                "summary": {
                    "accuracy": report["accuracy"],
                    "passed": sum(r["status"] == "pass" for r in report["details"]),
                    "total": len(report["details"]),
                },
                "details": report["details"],
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
