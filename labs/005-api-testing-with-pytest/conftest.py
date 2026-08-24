from __future__ import annotations

import socket
from collections.abc import Iterator
from threading import Thread
from time import monotonic, sleep
from uuid import uuid4

import pytest
import requests
import uvicorn

from api_client import ApiUser, AuthApiClient
from auth_api.app import create_app
from auth_api.store import AuthStore


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def api_base_url() -> Iterator[str]:
    store = AuthStore()
    port = _free_port()
    config = uvicorn.Config(
        create_app(store),
        host="127.0.0.1",
        port=port,
        log_level="error",
    )
    server = uvicorn.Server(config)
    thread = Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    deadline = monotonic() + 5
    while monotonic() < deadline:
        try:
            response = requests.get(f"{base_url}/health", timeout=0.2)
            if response.status_code == 200:
                break
        except requests.RequestException:
            sleep(0.05)
    else:
        server.should_exit = True
        thread.join(timeout=2)
        raise RuntimeError("本地接口服务未能在5秒内启动")

    yield base_url

    server.should_exit = True
    thread.join(timeout=5)
    store.reset()


@pytest.fixture
def api_client(api_base_url: str) -> Iterator[AuthApiClient]:
    client = AuthApiClient(api_base_url)
    yield client
    client.close()


@pytest.fixture
def registered_user(api_client: AuthApiClient) -> Iterator[ApiUser]:
    user = ApiUser(
        username=f"api_user_{uuid4().hex[:8]}",
        password="safe-pass-2026",
    )
    response = api_client.register(user.username, user.password)
    assert response.status_code == 201

    yield user

    login_response = api_client.login(user.username, user.password)
    if login_response.status_code == 200:
        api_client.use_token(login_response.json()["access_token"])
        api_client.delete_current_user()


@pytest.fixture
def authenticated_client(
    api_client: AuthApiClient,
    registered_user: ApiUser,
) -> AuthApiClient:
    response = api_client.login(registered_user.username, registered_user.password)
    assert response.status_code == 200
    api_client.use_token(response.json()["access_token"])
    return api_client
