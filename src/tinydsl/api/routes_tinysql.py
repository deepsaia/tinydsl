from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tinydsl.tinysql.tinysql import TinySQLInterpreter
from tinydsl.tinysql.tinysql_evaluator import TinySQLEvaluator
from tinydsl.api.common_handlers import DSLHandler
import os

router = APIRouter()

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")

TINYSQL_TASKS_PATH = os.getenv(
    "TINYSQL_TASKS_PATH", os.path.join(data_dir, "tinysql_tasks.json")
)
TINYSQL_GRAMMAR_PATH = os.getenv(
    "TINYSQL_GRAMMAR_PATH", os.path.join(data_dir, "tinysql_grammar.lark")
)

# Initialize common handler
handler = DSLHandler(
    dsl_class=TinySQLInterpreter,
    evaluator_class=TinySQLEvaluator,
    tasks_path=TINYSQL_TASKS_PATH,
    dsl_name="tinysql",
    grammar_path=TINYSQL_GRAMMAR_PATH,
)


# Request models
class TinySQLRequest(BaseModel):
    code: str


class TaskRequest(BaseModel):
    task_id: str


class EvalRequest(BaseModel):
    results: list


class ASTRequest(BaseModel):
    code: str
    include_pretty: bool = True
    include_dot: bool = False


@router.post("/run")
def run_tinysql(request: TinySQLRequest):
    """Run TinySQL DSL code."""
    response = handler.handle_run(code=request.code)
    return JSONResponse(response)


@router.post("/task")
def run_tinysql_task(request: TaskRequest):
    """Run a predefined TinySQL task."""
    response = handler.handle_task(task_id=request.task_id)
    return JSONResponse(response)


@router.post("/eval")
def evaluate_tinysql_outputs(request: EvalRequest):
    """Evaluate multiple TinySQL outputs."""
    response = handler.handle_eval(results=request.results)
    return JSONResponse(response)


@router.post("/ast")
def get_tinysql_ast(request: ASTRequest):
    """Parse TinySQL code and return AST."""
    response = handler.handle_ast(
        code=request.code,
        include_pretty=request.include_pretty,
        include_dot=request.include_dot,
    )
    return JSONResponse(response)


@router.get("/examples")
def list_tinysql_examples():
    """List available TinySQL examples."""
    try:
        sql = TinySQLInterpreter()
        examples = sql.get_examples()
        return JSONResponse({"status": "ok", "examples": examples})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
