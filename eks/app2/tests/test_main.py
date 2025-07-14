from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app2.main import app  # pylint: disable=import-error


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """fixture to create a testclient for app2"""
    with TestClient(app) as c:
        yield c


def test_healthz(client: TestClient) -> None:
    """test the health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root(client: TestClient) -> None:
    """test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI App 2!"}
