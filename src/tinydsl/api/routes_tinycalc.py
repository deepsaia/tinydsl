from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tinydsl.tinycalc.tinycalc import TinyCalcInterpreter
from tinydsl.tinycalc.tinycalc_evaluator import TinyCalcEvaluator
from tinydsl.api.common_handlers import DSLHandler
import os

router = APIRouter()

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")

TINYCALC_TASKS_PATH = os.getenv(
    "TINYCALC_TASKS_PATH", os.path.join(data_dir, "tinycalc_tasks.json")
)
TINYCALC_GRAMMAR_PATH = os.getenv(
    "TINYCALC_GRAMMAR_PATH", os.path.join(data_dir, "tinycalc_grammar.lark")
)

# Initialize common handler
handler = DSLHandler(
    dsl_class=TinyCalcInterpreter,
    evaluator_class=TinyCalcEvaluator,
    tasks_path=TINYCALC_TASKS_PATH,
    dsl_name="tinycalc",
    grammar_path=TINYCALC_GRAMMAR_PATH,
)


# Request models
class TinyCalcRequest(BaseModel):
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
def run_tinycalc(request: TinyCalcRequest):
    """Run TinyCalc DSL code."""
    response = handler.handle_run(code=request.code)
    return JSONResponse(response)


@router.post("/task")
def run_tinycalc_task(request: TaskRequest):
    """Run a predefined TinyCalc task."""
    response = handler.handle_task(task_id=request.task_id)
    return JSONResponse(response)


@router.post("/eval")
def evaluate_tinycalc_outputs(request: EvalRequest):
    """Evaluate multiple TinyCalc outputs."""
    response = handler.handle_eval(results=request.results)
    return JSONResponse(response)


@router.post("/ast")
def get_tinycalc_ast(request: ASTRequest):
    """Parse TinyCalc code and return AST."""
    response = handler.handle_ast(
        code=request.code,
        include_pretty=request.include_pretty,
        include_dot=request.include_dot,
    )
    return JSONResponse(response)


@router.get("/examples")
def list_tinycalc_examples():
    """List available TinyCalc examples."""
    try:
        calc = TinyCalcInterpreter()
        examples = calc.get_examples()
        return JSONResponse({"status": "ok", "examples": examples})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
