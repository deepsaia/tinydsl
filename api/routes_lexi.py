from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from lexi_interpreter import LexiInterpreter

router = APIRouter()

class LexiRequest(BaseModel):
    code: str
    randomness: float = 0.1
    seed: int | None = None


@router.post("/lexi/run")
def run_lexi(request: LexiRequest):
    """Run a Lexi DSL script and return the generated text."""
    try:
        lexi = LexiInterpreter(seed=request.seed, randomness=request.randomness)
        lexi.parse(request.code)
        result = lexi.render()
        return JSONResponse({"status": "ok", "output": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
