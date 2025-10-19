# src/tinydsl/api/routes_gli.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import json
import os

from tinydsl.gli.gli import GlintInterpreter
from tinydsl.gli.renderers import PillowRenderer  # kept for type clarity

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


def _make_interpreter(
    *,
    canvas_size: int,
    supersample: int,
    line_width: int,
) -> GlintInterpreter:
    """Build a Pillow-only interpreter with tuned renderer."""
    return GlintInterpreter(
        canvas_size=canvas_size,
        supersample=supersample,
        line_width=line_width,
    )


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
    try:
        interp = _make_interpreter(
            canvas_size=canvas_size or request.canvas_size,
            supersample=supersample or request.supersample,
            line_width=line_width or request.line_width,
        )
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
    """Run and render an example by ID (Pillow-only)."""
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
