from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tinydsl.tinymath.tinymath import TinyMathInterpreter
from tinydsl.tinymath.tinymath_evaluator import TinyMathEvaluator
from tinydsl.api.common_handlers import DSLHandler
import os

router = APIRouter()

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")

TINYMATH_TASKS_PATH = os.getenv(
    "TINYMATH_TASKS_PATH", os.path.join(data_dir, "tinymath_tasks.json")
)
TINYMATH_GRAMMAR_PATH = os.getenv(
    "TINYMATH_GRAMMAR_PATH", os.path.join(data_dir, "tinymath_grammar.lark")
)

# Initialize common handler
handler = DSLHandler(
    dsl_class=TinyMathInterpreter,
    evaluator_class=TinyMathEvaluator,
    tasks_path=TINYMATH_TASKS_PATH,
    dsl_name="tinymath",
    grammar_path=TINYMATH_GRAMMAR_PATH,
)


# Request models
class TinyMathRequest(BaseModel):
    code: str


class TaskRequest(BaseModel):
    task_id: str


class EvalRequest(BaseModel):
    results: list  # [{"task_id": "...", "output": "..."}]


class ASTRequest(BaseModel):
    code: str
    include_pretty: bool = True
    include_dot: bool = False


@router.post("/run")
def run_tinymath(request: TinyMathRequest):
    """Run TinyMath DSL code."""
    response = handler.handle_run(code=request.code)
    return JSONResponse(response)


@router.post("/task")
def run_tinymath_task(request: TaskRequest):
    """Run a predefined TinyMath task."""
    response = handler.handle_task(task_id=request.task_id)
    return JSONResponse(response)


@router.post("/eval")
def evaluate_tinymath_outputs(request: EvalRequest):
    """Evaluate multiple TinyMath outputs."""
    response = handler.handle_eval(results=request.results)
    return JSONResponse(response)


@router.post("/ast")
def get_tinymath_ast(request: ASTRequest):
    """Parse TinyMath code and return AST."""
    response = handler.handle_ast(
        code=request.code,
        include_pretty=request.include_pretty,
        include_dot=request.include_dot,
    )
    return JSONResponse(response)


@router.get("/examples")
def list_tinymath_examples():
    """List available TinyMath examples."""
    try:
        math_interp = TinyMathInterpreter()
        examples = math_interp.get_examples()
        return JSONResponse({"status": "ok", "examples": examples})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
