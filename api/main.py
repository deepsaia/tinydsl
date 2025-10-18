import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles FastAPI startup and shutdown."""
    logging.info("🚀 Glint DSL API is starting up...")
    try:
        # Example of any init logic: preload DSL configs or verify files
        logging.info("Loading Glint examples and verifying environment...")
        yield
    finally:
        logging.info("🛑 Glint DSL API is shutting down...")


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
app.include_router(router, prefix="/api", tags=["Glint DSL"])


@app.get("/")
def root():
    return {"message": "Welcome to the Glint DSL API!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8008, reload=True)
