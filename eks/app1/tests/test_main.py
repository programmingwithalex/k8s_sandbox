from typing import Generator

import jwt
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from httpx import TimeoutException
from pytest_httpx import HTTPXMock

from app1.main import ALGORITHM, APP2_URL, SECRET_KEY, app, verify_jwt


class DummyRequest:
    """a dummy request class to simulate fastapi request objects for testing purposes"""

    def __init__(self, headers: dict = None, cookies: dict = None) -> None:
        self.headers = headers or {}
        self.cookies = cookies or {}


@pytest.fixture
def client_verified_auth_header() -> Generator[TestClient, None, None]:
    """fixture to create a testclient with jwt authentication via authorization header"""
    # * generate a valid JWT token
    token = jwt.encode({"sub": "Koyomi Araragi"}, SECRET_KEY, algorithm=ALGORITHM)

    with TestClient(app) as test_client:
        # * set the Authorization header for all requests
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client


@pytest.fixture
def client_verified_auth_cookies() -> Generator[TestClient, None, None]:
    """fixture to create a testclient with verified jwt authentication using cookies"""
    # * generate a valid JWT token
    token = jwt.encode({"sub": "Koyomi Araragi"}, SECRET_KEY, algorithm=ALGORITHM)

    with TestClient(app) as test_client:
        # * set the Authorization header for all requests
        test_client.cookies.set("access_token", token)
        yield test_client


@pytest.fixture
def client_unpatched_auth() -> Generator[TestClient, None, None]:
    """fixture to create a testclient without any jwt authentication"""
    with TestClient(app) as test_client_unpatched:
        yield test_client_unpatched


def create_jwt_token(payload: dict) -> str:
    """create a jwt token for testing purposes"""
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_healthz(client_unpatched_auth: TestClient) -> None:
    """test the health check endpoint"""
    response = client_unpatched_auth.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_burn_cpu(client_unpatched_auth: TestClient) -> None:
    """test the cpu burn endpoint"""
    response = client_unpatched_auth.get("/burn?iterations=10")
    assert response.status_code == 200
    assert "digest" in response.json()


def test_root_unauthorized(client_unpatched_auth: TestClient) -> None:
    """test the root endpoint without authentication"""
    response = client_unpatched_auth.get("/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] in ["Missing token", "Not authenticated"]


def test_root_with_auth_header(client_verified_auth_header: TestClient) -> None:
    """test the root endpoint with jwt authentication via authorization header"""
    response = client_verified_auth_header.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_root_with_auth_cookie(client_verified_auth_cookies: TestClient) -> None:
    """test the root endpoint with jwt authentication via cookies"""
    response = client_verified_auth_cookies.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.parametrize(
    "headers, cookies, expected_sub",
    [
        ({"Authorization": "Bearer " + create_jwt_token({"sub": "Hitagi Senjōgahara"})}, {}, "Hitagi Senjōgahara"),
        ({}, {"access_token": create_jwt_token({"sub": "Mayoi Hachikuji"})}, "Mayoi Hachikuji"),
    ],
)
def test_verify_jwt_valid_token(headers: dict, cookies: dict, expected_sub: str) -> None:
    """test jwt verification with valid tokens in headers or cookies"""
    req = DummyRequest(headers=headers, cookies=cookies)
    result = verify_jwt(req)  # type: ignore[arg-type]
    assert result["sub"] == expected_sub


def test_verify_jwt_missing_token() -> None:
    """test jwt verification with a missing token"""
    req = DummyRequest()
    with pytest.raises(HTTPException) as exc:  # expect an HTTPException to be raised - captured in `exc`
        verify_jwt(req)  # type: ignore[arg-type]
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Missing token"


def test_verify_jwt_invalid_token() -> None:
    """test jwt verification with an invalid token"""
    req = DummyRequest(headers={"Authorization": "Bearer invalidtoken"})
    with pytest.raises(HTTPException) as exc:  # expect an HTTPException to be raised - captured in `exc`
        verify_jwt(req)  # type: ignore[arg-type]
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid token"


def test_read_app2(httpx_mock: HTTPXMock, client_verified_auth_header: TestClient) -> None:
    """test the /read_app2 endpoint with a mocked app2 response"""
    # mock the response for APP2_URL
    httpx_mock.add_response(url=APP2_URL, json={"mocked": True})  # mock the response from APP2_URL

    response = client_verified_auth_header.get("/read_app2")
    assert response.status_code == 200
    assert response.json()['app2_response'] == {"mocked": True}


def test_read_app2_error(httpx_mock: HTTPXMock, client_verified_auth_header: TestClient) -> None:
    """test the /read_app2 endpoint when app2 returns an error response"""
    httpx_mock.add_exception(url=APP2_URL, exception=Exception())
    response = client_verified_auth_header.get("/read_app2")
    assert response.status_code == 500


def test_read_app2_timeout(httpx_mock: HTTPXMock, client_verified_auth_header: TestClient) -> None:
    """test the /read_app2 endpoint when app2 times out"""
    httpx_mock.add_exception(url=APP2_URL, exception=TimeoutException("timeout"))
    response = client_verified_auth_header.get("/read_app2")
    assert response.status_code == 504
    assert response.json()["detail"].startswith("timeout:")
