import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from tinydsl.api.routes_lexi import router as lexi_router
from tinydsl.api.routes_gli import router as gli_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Handles FastAPI startup and shutdown."""
    logging.info("🚀 Tiny DSL API is starting up...")
    try:
        # Example of any init logic: preload DSL configs or verify files
        logging.info("Loading Gli examples and verifying environment...")
        yield
    finally:
        logging.info("🛑 Tiny DSL API is shutting down...")


# Initialize app
app = FastAPI(
    title="Glint DSL API",
    version="0.2",
    description="API for running and testing the Glint DSL interpreter.",
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
app.include_router(gli_router, prefix="/api/gli", tags=["Glint DSL"])
app.include_router(lexi_router, prefix="/api/lexi", tags=["Lexi DSL"])


@app.get("/")
def root():
    return {
        "message": "Welcome to TinyDSL API with Glint (image) and Lexi (text) DSLs.!"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tinydsl.api.main:app",
        host="0.0.0.0",
        port=8008,
        reload=True
        )
