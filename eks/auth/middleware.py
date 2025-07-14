import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8003").split(",")


def add_cors_middleware(app: FastAPI) -> None:
    """
    Add CORS middleware to the FastAPI application.
    This middleware allows cross-origin requests from specified origins,
    enabling the frontend to communicate with the backend services.
    Args:
        app (FastAPI): The FastAPI application instance to which the middleware will be added.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,  # React dev or NGINX port
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
