from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class ApiUser:
    username: str
    password: str


class AuthApiClient:
    """为登录接口提供统一的基础地址、会话和超时配置。"""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: tuple[float, float] = (1.0, 1.0),
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def register(self, username: str, password: str) -> requests.Response:
        return self._request(
            "POST",
            "/api/users",
            json={"username": username, "password": password},
        )

    def login(self, username: str, password: str) -> requests.Response:
        return self._request(
            "POST",
            "/api/login",
            json={"username": username, "password": password},
        )

    def use_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def profile(self) -> requests.Response:
        return self._request("GET", "/api/profile")

    def logout(self) -> requests.Response:
        return self._request("POST", "/api/logout")

    def delete_current_user(self) -> requests.Response:
        return self._request("DELETE", "/api/users/me")

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        timeout: float | tuple[float, float] | None = None,
    ) -> requests.Response:
        return self._request("GET", path, params=params, timeout=timeout)

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: float | tuple[float, float] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        request_timeout = self.timeout if timeout is None else timeout
        return self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=request_timeout,
            **kwargs,
        )
