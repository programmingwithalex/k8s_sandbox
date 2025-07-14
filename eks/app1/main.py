import os
from typing import Any, Callable

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from .logging_config import logger
from .middleware import add_cors_middleware

if os.getenv("ENV", "development") != "production":
    from dotenv import load_dotenv

    load_dotenv()

app = FastAPI()
add_cors_middleware(app)  # Add CORS middleware to allow cross-origin requests from the frontend

# * allows Prometheus to scrape metrics from this FastAPI app
# * automatically exposes metrics at /metrics endpoint that Prometheus can scrape
Instrumentator().instrument(app).expose(app)

APP2_URL = os.getenv("APP2_URL", "http://fastapi-app2-service")
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
# * verify with `kubectl get svc` in the `auth` namespace
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://fastapi-auth-service:80")


class LoginRequest(BaseModel):
    """
    Request model for user login.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
    """

    username: str
    password: str


def verify_jwt(request: Request) -> dict:
    """
    Verify the JWT token from the request headers or cookies.
    This function checks for the presence of a JWT token in the Authorization header
    or in the cookies. If the token is found, it decodes it and verifies its validity.

    Args:
        request (Request): The FastAPI request object containing headers.
    Raises:
        HTTPException: If the token is missing, expired, or invalid.
    Returns:
        dict: The decoded JWT payload if the token is valid.
    """
    auth = request.headers.get("Authorization")  # first check for Authorization header - API call
    token = None

    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]
    else:
        token = request.cookies.get("access_token")  # check for access_token in cookies if not found in header

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/")
def read_root(payload: dict = Depends(verify_jwt)) -> dict[str, str]:
    """
    Root endpoint that returns a greeting message.
    It verifies the JWT token from the request headers or cookies and returns a personalized greeting.

    Args:
        payload (dict): The decoded JWT payload obtained from the `verify_jwt` dependency.
    Returns:
        dict: A dictionary containing a greeting message with the username extracted from the JWT payload.
    """
    username = payload.get("sub", "unknown user")  # `sub` set in `auth` service
    return {"message": f"Hello from Kubernetes, {username}!!!!!"}


@app.get("/read_app2")
async def read_app2(_: dict = Depends(verify_jwt)) -> dict[str, Any]:
    """
    Endpoint to read data from FastAPI App 2.
    It verifies the JWT token from the request headers or cookies and then makes an HTTP GET request
    to app2 to retrieve data.

    Args:
        payload (dict): The decoded JWT payload obtained from the `verify_jwt` dependency.
    Returns:
        dict: A dictionary containing a greeting message and the response from FastAPI App 2.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(APP2_URL)
            app2_data = r.json()
    except httpx.TimeoutException as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"timeout: {str(e)}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"request error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"unexpected error: {str(e)}")

    return {"message": "Hello from FastAPI App 1 (with configmap)", "app2_response": app2_data}


# ********************************************************************************* #
# * CPU‑bound endpoint: for forcing CPU load to test `Horizontal Pod Autoscaling (HPA)`
def burn_cpu(iterations: int) -> str:
    """Burn CPU by performing SHA-256 hashing in a tight loop."""
    import hashlib

    # * perform many SHA‑256 digests in a tight loop
    data = b"x" * 1024
    result = b""
    for _ in range(iterations):
        result = hashlib.sha256(data + result).digest()
    return result.hex()


@app.get("/burn")
def cpu_burner(iterations: int = 10_000) -> dict[str, str]:
    """CPU-bound endpoint: increasing `iterations` linearly increases work."""
    digest = burn_cpu(iterations)
    return {"digest": digest}


# ********************************************************************************* #


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify the service is running."""
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
