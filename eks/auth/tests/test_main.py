from typing import Generator

import jwt
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from auth.main import ALGORITHM, SECRET_KEY, TEST_USERS, app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """fixture to create a testclient for auth"""
    with TestClient(app) as c:
        yield c


def test_healthz(client: TestClient) -> None:
    """test the health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_login_success(client: TestClient) -> None:
    """test login with valid credentials"""
    for username, password in TEST_USERS.items():
        response = client.post("/login", json={"username": username, "password": password})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

        decoded = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == username  # verify JWT
        assert "access_token" in response.cookies  # verify cookie is set

        break  # only test first user for brevity


def test_login_invalid_credentials(client: TestClient) -> None:
    """test login with invalid credentials"""
    response = client.post("/login", json={"username": "not_a_user", "password": "badpass"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


def test_logout(client: TestClient) -> None:
    """test logout endpoint clears cookie"""
    response = client.post("/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logged out successfully"
