from typing import Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from .logging_config import logger
from .middleware import add_cors_middleware

app = FastAPI()
add_cors_middleware(app)  # Add CORS middleware to allow cross-origin requests from the frontend

# * allows Prometheus to scrape metrics from this FastAPI app
# * automatically exposes metrics at /metrics endpoint that Prometheus can scrape
Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint that returns a simple greeting message."""
    return {"message": "Hello from FastAPI App 2!"}


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify if the service is running."""
    return {"status": "ok"}


@app.middleware("http")
async def log_path(request: Request, call_next: Callable) -> JSONResponse:
    """Middleware to log the incoming request path"""
    logger.info(f"INCOMING PATH: {request.url.path}")
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
