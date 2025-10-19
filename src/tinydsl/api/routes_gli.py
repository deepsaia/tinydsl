from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
from tinydsl.src.tinydsl.gli import GlintInterpreter

router = APIRouter()

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")

EXAMPLES_PATH = os.getenv("GLI_EXAMPLES_PATH", os.path.join(data_dir, "gli_examples.json"))

try:
    with open(EXAMPLES_PATH, "r") as f:
        GLI_EXAMPLES = json.load(f)
except Exception as e:
    GLI_EXAMPLES = []
    print(f"Warning: Could not load examples file: {e}")


class DSLRequest(BaseModel):
    code: str
    save: bool = True
    open_after_save: bool = False
    name: str | None = None


@router.get("/examples")
def list_examples(tag: str | None = Query(None)):
    """List all available Glint examples."""
    if tag:
        filtered = [e for e in GLI_EXAMPLES if tag in e["tags"]]
        return JSONResponse(filtered)
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
def run_code(request: DSLRequest):
    """Run arbitrary Glint DSL code and save image."""
    gl = GlintInterpreter()
    try:
        gl.parse(request.code)
        output_path = gl.render(
            save=request.save,
            open_after_save=request.open_after_save,
            name=request.name or "custom_code",
        )
        return {"status": "ok", "path": output_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/run_example/{example_id}")
def run_example(example_id: str, save: bool = True, open_after_save: bool = False):
    """Run and render an example by ID."""
    example = next((e for e in GLI_EXAMPLES if e["id"] == example_id), None)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")

    gl = GlintInterpreter()
    try:
        gl.parse(example["code"])
        output_path = gl.render(
            save=save, open_after_save=open_after_save, name=example["name"]
        )
        return {"status": "ok", "example_id": example_id, "output_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
