from __future__ import annotations

import re

import pytest
import requests

from api_client import ApiUser, AuthApiClient


TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{20,}$")


def test_login_returns_a_usable_bearer_token(
    api_client: AuthApiClient,
    registered_user: ApiUser,
) -> None:
    login_response = api_client.login(
        registered_user.username,
        registered_user.password,
    )

    assert login_response.status_code == 200
    body = login_response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 3600
    assert TOKEN_PATTERN.fullmatch(body["access_token"])

    api_client.use_token(body["access_token"])
    profile_response = api_client.profile()
    assert profile_response.status_code == 200
    assert profile_response.json() == {
        "username": registered_user.username,
        "status": "active",
    }


@pytest.mark.parametrize(
    ("password", "expected_code"),
    [
        pytest.param("wrong-pass", "INVALID_CREDENTIALS", id="wrong-password"),
        pytest.param("SAFE-PASS-2026", "INVALID_CREDENTIALS", id="case-sensitive"),
    ],
)
def test_login_rejects_invalid_passwords(
    api_client: AuthApiClient,
    registered_user: ApiUser,
    password: str,
    expected_code: str,
) -> None:
    response = api_client.login(registered_user.username, password)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"]["code"] == expected_code


def test_login_rejects_a_missing_password(api_client: AuthApiClient) -> None:
    response = api_client.session.post(
        f"{api_client.base_url}/api/login",
        json={"username": "api_user"},
        timeout=api_client.timeout,
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert errors[0]["loc"] == ["body", "password"]
    assert errors[0]["type"] == "missing"


def test_duplicate_registration_returns_a_conflict(
    api_client: AuthApiClient,
    registered_user: ApiUser,
) -> None:
    response = api_client.register(
        registered_user.username,
        registered_user.password,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == {
        "code": "USER_EXISTS",
        "message": "用户名已存在",
    }


def test_profile_requires_a_bearer_token(api_client: AuthApiClient) -> None:
    response = api_client.profile()

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"]["code"] == "AUTH_REQUIRED"


def test_logout_revokes_the_current_token(
    authenticated_client: AuthApiClient,
) -> None:
    logout_response = authenticated_client.logout()
    profile_response = authenticated_client.profile()

    assert logout_response.status_code == 204
    assert logout_response.content == b""
    assert profile_response.status_code == 401
    assert profile_response.json()["detail"]["code"] == "TOKEN_INVALID"


@pytest.mark.timeout
def test_client_stops_waiting_for_a_slow_response(
    api_client: AuthApiClient,
) -> None:
    with pytest.raises(requests.Timeout):
        api_client.get(
            "/api/slow",
            params={"delay_ms": 200},
            timeout=(0.1, 0.05),
        )
