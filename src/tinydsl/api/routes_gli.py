# src/tinydsl/api/routes_gli.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from tinydsl.gli.gli import GlintInterpreter
from tinydsl.gli.gli_evaluator import GliEvaluator
from tinydsl.api.common_handlers import DSLHandler
import json
import os

router = APIRouter()

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")
EXAMPLES_PATH = os.getenv("GLI_EXAMPLES_PATH", os.path.join(data_dir, "gli_examples.json"))
TASKS_PATH = os.getenv("GLI_TASKS_PATH", os.path.join(data_dir, "gli_tasks.json"))
GRAMMAR_PATH = os.getenv("GLI_GRAMMAR_PATH", os.path.join(data_dir, "gli_grammar.lark"))

try:
    with open(EXAMPLES_PATH, "r") as f:
        GLI_EXAMPLES = json.load(f)
except Exception as e:
    GLI_EXAMPLES = []
    print(f"Warning: Could not load examples file: {e}")

try:
    with open(TASKS_PATH, "r") as f:
        GLI_TASKS = json.load(f)
except Exception as e:
    GLI_TASKS = []
    print(f"Warning: Could not load tasks file: {e}")

# Initialize common handler
handler = DSLHandler(
    dsl_class=GlintInterpreter,
    evaluator_class=GliEvaluator,
    tasks_path=TASKS_PATH,
    dsl_name="gli",
    grammar_path=GRAMMAR_PATH,
)


# ---------------- Models ----------------
class DSLRequest(BaseModel):
    code: str
    save: bool = True
    open_after_save: bool = False
    name: str | None = None
    id: str | None = None
    output_root: str = Field(default="output", description="Folder to save renders")

    # Pillow knobs
    canvas_size: int = Field(default=768, ge=64, le=4096)
    supersample: int = Field(default=2, ge=1, le=8)
    line_width: int = Field(default=2, ge=1, le=32)


class ASTRequest(BaseModel):
    code: str
    include_pretty: bool = True
    include_dot: bool = False


# ---------------- Helper Functions ----------------
def _gli_run_processor(dsl_instance, output, request: DSLRequest):
    """Custom processor for Gli /run endpoint to handle image rendering."""
    # Gli's render() returns a path, which is already in 'output'
    return {"status": "ok", "renderer": "pillow", "path": output}


def _gli_task_processor(dsl_instance, output, task: dict):
    """Custom processor for Gli /task endpoint to handle image rendering."""
    return {
        "status": "ok",
        "task_id": task["id"],
        "output": output,  # path to rendered image
        "expected_output": task.get("expected_output", ""),
    }


# ---------------- Routes ----------------
@router.get("/examples")
def list_examples(tag: str | None = Query(None)):
    """List all available Glint examples (optionally filter by tag)."""
    if tag:
        return JSONResponse([e for e in GLI_EXAMPLES if tag in e.get("tags", [])])
    return JSONResponse(GLI_EXAMPLES)


@router.get("/examples/{example_id}")
def get_example(example_id: str):
    """Get example by ID."""
    example = next((e for e in GLI_EXAMPLES if e["id"] == example_id), None)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return JSONResponse(example)


@router.get("/examples/by_name/{name}")
def get_example_by_name(name: str):
    """Get example by name."""
    example = next((e for e in GLI_EXAMPLES if e["name"] == name), None)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return JSONResponse(example)


@router.post("/run")
def run_code(
    request: DSLRequest,
    # Optional query overrides
    canvas_size: int = Query(default=None, ge=64, le=4096),
    supersample: int = Query(default=None, ge=1, le=8),
    line_width: int = Query(default=None, ge=1, le=32),
):
    """
    Run arbitrary GLI code and save image (Pillow-only).
    """
    # Build DSL kwargs for rendering
    dsl_kwargs = {
        "canvas_size": canvas_size or request.canvas_size,
        "supersample": supersample or request.supersample,
        "line_width": line_width or request.line_width,
    }

    # Custom handler that uses Gli's special render() signature
    try:
        interp = GlintInterpreter(**dsl_kwargs)
        interp.parse(request.code)
        path = interp.render(
            save=request.save,
            open_after_save=request.open_after_save,
            output_root=request.output_root,
            name=request.name or "custom_code",
            artifact_id=request.id,
        )
        return {"status": "ok", "renderer": "pillow", "path": path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/task")
def run_task(
    task_id: str,
    save: bool = True,
    open_after_save: bool = False,
    name: str | None = None,
    output_root: str = "output",
    canvas_size: int = Query(default=768, ge=64, le=4096),
    supersample: int = Query(default=2, ge=1, le=8),
    line_width: int = Query(default=2, ge=1, le=32),
):
    """Run a benchmark task by ID."""
    task = next((t for t in GLI_TASKS if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        interp = GlintInterpreter(
            canvas_size=canvas_size,
            supersample=supersample,
            line_width=line_width,
        )
        interp.parse(task["code"])
        path = interp.render(
            save=save,
            open_after_save=open_after_save,
            output_root=output_root,
            name=name or task.get("name", f"task_{task_id}"),
            artifact_id=task.get("id"),
        )
        return {
            "status": "ok",
            "task_id": task_id,
            "output": path,
            "expected_output": task.get("expected_output", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/eval")
def evaluate_outputs(results: list[dict]):
    """
    Evaluate multiple task outputs.

    Args:
        results: List of {"task_id": "...", "output": "..."}

    Returns:
        Evaluation report with accuracy and details
    """
    response = handler.handle_eval(results=results)
    return JSONResponse(response)


@router.post("/ast")
def get_gli_ast(request: ASTRequest):
    """Parse Gli code and return AST."""
    response = handler.handle_ast(
        code=request.code,
        include_pretty=request.include_pretty,
        include_dot=request.include_dot,
    )
    return JSONResponse(response)


# Backwards compatibility: keep run_example as alias
@router.get("/run_example/{example_id}")
def run_example(
    example_id: str,
    save: bool = True,
    open_after_save: bool = False,
    name: str | None = None,
    output_root: str = "output",
    canvas_size: int = Query(default=768, ge=64, le=4096),
    supersample: int = Query(default=2, ge=1, le=8),
    line_width: int = Query(default=2, ge=1, le=32),
):
    """Run and render an example by ID (Pillow-only). DEPRECATED: Use /task instead."""
    example = next((e for e in GLI_EXAMPLES if e["id"] == example_id), None)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")

    try:
        interp = _make_interpreter(
            canvas_size=canvas_size,
            supersample=supersample,
            line_width=line_width,
        )
        interp.parse(example["code"])
        path = interp.render(
            save=save,
            open_after_save=open_after_save,
            output_root=output_root,
            name=name or example.get("name", f"example_{example_id}"),
            artifact_id=example.get("id"),
        )
        return {"status": "ok", "example_id": example_id, "renderer": "pillow", "output_path": path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
