from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from tinydsl.core.logging_config import logger, setup_standard_logging_interception
from tinydsl.api.routes_lexi import router as lexi_router
from tinydsl.api.routes_gli import router as gli_router
from tinydsl.api.routes_tinycalc import router as tinycalc_router
from tinydsl.api.routes_tinysql import router as tinysql_router
from tinydsl.api.routes_tinymath import router as tinymath_router

# Register DSLs in global registry
from tinydsl.core.dsl_registry import register_dsl
from tinydsl.gli.gli import GlintInterpreter
from tinydsl.lexi.lexi import LexiInterpreter
from tinydsl.tinycalc.tinycalc import TinyCalcInterpreter
from tinydsl.tinysql.tinysql import TinySQLInterpreter
from tinydsl.tinymath.tinymath import TinyMathInterpreter

# Setup logging interception for uvicorn and fastapi
setup_standard_logging_interception()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Handles FastAPI startup and shutdown."""
    logger.info("🚀 TinyDSL API is starting up...")
    try:
        # Try to register DSLs in the global registry (optional - only needed for /dsls endpoint)
        # Some DSLs may not inherit from BaseDSL, which is fine for REST API usage
        try:
            register_dsl("gli", GlintInterpreter)
            register_dsl("lexi", LexiInterpreter)
            register_dsl("tinycalc", TinyCalcInterpreter)
            register_dsl("tinysql", TinySQLInterpreter)
            register_dsl("tinymath", TinyMathInterpreter)
            logger.success("✅ Registered DSLs: gli, lexi, tinycalc, tinysql, tinymath")
        except ValueError as e:
            logger.warning(f"⚠️  DSL registration skipped: {e}")
            logger.info("API endpoints will still work, but /dsls endpoint may not list all DSLs")
        yield
    finally:
        logger.info("🛑 TinyDSL API is shutting down...")


# Initialize app
app = FastAPI(
    title="TinyDSL API",
    version="0.4.0",
    description="Modular framework for multiple DSLs: Gli (graphics), Lexi (text), TinyCalc (units), TinySQL (queries), TinyMath (arithmetic)",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(gli_router, prefix="/api/gli", tags=["Gli DSL - Graphics"])
app.include_router(lexi_router, prefix="/api/lexi", tags=["Lexi DSL - Text"])
app.include_router(tinycalc_router, prefix="/api/tinycalc", tags=["TinyCalc DSL - Unit Conversion"])
app.include_router(tinysql_router, prefix="/api/tinysql", tags=["TinySQL DSL - Data Query"])
app.include_router(tinymath_router, prefix="/api/tinymath", tags=["TinyMath DSL - Arithmetic"])


@app.get("/")
def root():
    """API root with available DSLs."""
    return {
        "message": "Welcome to TinyDSL API - A modular framework for domain-specific languages",
        "version": "0.4.0",
        "dsls": {
            "gli": {"endpoint": "/api/gli", "description": "Graphics DSL for procedural image generation"},
            "lexi": {"endpoint": "/api/lexi", "description": "Text DSL for structured text generation"},
            "tinycalc": {"endpoint": "/api/tinycalc", "description": "Novel unit conversion DSL"},
            "tinysql": {"endpoint": "/api/tinysql", "description": "Simple query DSL for structured data"},
            "tinymath": {"endpoint": "/api/tinymath", "description": "General-purpose arithmetic calculator"}
        },
        "docs": "/docs"
    }


@app.get("/dsls")
def list_dsls():
    """List all registered DSLs."""
    from tinydsl.core.dsl_registry import list_available_dsls
    registered = list_available_dsls()

    # Fallback: list all DSLs even if not registered
    if not registered:
        registered = ["gli", "lexi", "tinycalc", "tinysql", "tinymath"]

    return {
        "status": "ok",
        "dsls": registered
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tinydsl.api.main:app",
        host="0.0.0.0",
        port=8008,
        reload=True
        )
