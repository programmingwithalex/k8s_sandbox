import os
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt  # PyJWT
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from .logging_config import logger
from .middleware import add_cors_middleware

app = FastAPI()
add_cors_middleware(app)  # Add CORS middleware to allow cross-origin requests from the frontend

# * allows Prometheus to scrape metrics from this FastAPI app
# * automatically exposes metrics at /metrics endpoint that Prometheus can scrape
Instrumentator().instrument(app).expose(app)

SECRET_KEY = os.environ["SECRET_KEY"]
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

TEST_USERS = {
    "user": "pass",
    "alice": "wonderland",
    "bob": "builder",
    "charlie": "chocolate",
}


class LoginRequest(BaseModel):
    """
    Model for login request data

    Attributes:
        username (str): The username of the user
        password (str): The password of the user
    """

    username: str
    password: str


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token with an expiration time.
    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): The expiration time for the token. Defaults to 30 minutes.
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/login")
def login(data: LoginRequest) -> JSONResponse:
    """Endpoint to handle user login and return a JWT token"""
    if not TEST_USERS.get(data.username) == data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": data.username})
    resp = JSONResponse(content={"access_token": token, "token_type": "bearer"})
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="strict",
    )
    return resp


@app.post("/logout")
def logout() -> JSONResponse:
    """Endpoint to handle user logout and clear the JWT token"""
    resp = JSONResponse(content={"message": "Logged out successfully"})
    resp.delete_cookie(  # set attributes to be consistent with login
        key="access_token",
        httponly=True,
        secure=False,  # Set to True in production
        samesite="strict",
    )
    return resp


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify the service is running"""
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
