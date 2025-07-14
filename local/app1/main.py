import os
from typing import Any

import httpx
from fastapi import FastAPI

app = FastAPI()
APP2_URL = os.getenv("APP2_URL", "http://fastapi-app2-service")


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Root endpoint that returns a simple greeting message.
    This endpoint is used to verify if the FastAPI
    application is running correctly.
    """
    return {"message": "Hello from Kubernetes"}


@app.get("/read_app2")
async def read_app2() -> dict[str, Any]:
    """
    Endpoint to read data from another FastAPI app (app2).
    This endpoint makes an HTTP GET request to app2 and returns its response.
    It is used to demonstrate inter-service communication in a Kubernetes environment.
    Returns:
        dict: A dictionary containing a greeting message and the response from FastAPI App 2.
    """
    try:
        async with httpx.AsyncClient() as client:
            # r = await client.get("http://fastapi-app2-service/")
            r = await client.get(APP2_URL)
            app2_data = r.json()
    except Exception as e:
        app2_data = {"error": str(e)}

    print(f"Response from app2: {app2_data}")

    return {"message": "Hello from FastAPI App 1 (with configmap)", "app2_response": app2_data}


# ********************************************************************************* #
# * CPU‑bound endpoint: for forcing CPU load to test `Horizontal Pod Autoscaling (HPA)`
def burn_cpu(num_iterations: int) -> str:
    """
    CPU-bound endpoint: performs many SHA-256 digests in a tight loop.
    Increasing `num_iterations` linearly increases the CPU work.
    Args:
        num_iterations (int): The number of SHA-256 digests to perform.
    Returns:
        str: The hexadecimal representation of the final SHA-256 digest.
    """
    import hashlib

    # * perform many SHA-256 digests in a tight loop
    data = b"x" * 1024
    result = b""
    for _ in range(num_iterations):
        result = hashlib.sha256(data + result).digest()
    return result.hex()


@app.get("/burn")
def cpu_burner(num_iterations: int = 10_000) -> dict[str, str]:
    """
    CPU-bound endpoint: increasing `num_iterations` linearly increases work.
    """
    digest = burn_cpu(num_iterations)
    return {"digest": digest}


# ********************************************************************************* #


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify the service is running.
    This endpoint is used by Kubernetes to check the health of the application.
    Returns:
        dict: A dictionary indicating the service status.
    """
    return {"status": "ok"}
