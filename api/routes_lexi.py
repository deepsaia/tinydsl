# api/routes_lexi.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from lexi_interpreter import LexiInterpreter

router = APIRouter()


class LexiRequest(BaseModel):
    code: str


@router.post("/run")
def run_lexi(request: LexiRequest):
    """Run a Lexi DSL script and return generated text."""
    try:
        lexi = LexiInterpreter()
        lexi.parse(request.code)
        result = lexi.render()
        return JSONResponse({"status": "ok", "output": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
