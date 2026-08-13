from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class PasswordPolicy:
    minimum_length: int = 8

    def validate(self, password: str) -> None:
        if len(password) < self.minimum_length:
            raise ValueError(f"密码长度不能少于{self.minimum_length}位")


class AccountStore:
    def __init__(self) -> None:
        self._accounts: dict[str, str] = {}
        self._closed = False

    @property
    def user_count(self) -> int:
        return len(self._accounts)

    def create_user(self, credentials: Credentials, policy: PasswordPolicy) -> None:
        self._ensure_open()
        policy.validate(credentials.password)
        if credentials.username in self._accounts:
            raise ValueError("用户名已存在")
        self._accounts[credentials.username] = credentials.password

    def delete_user(self, username: str) -> None:
        self._ensure_open()
        self._accounts.pop(username, None)

    def authenticate(self, credentials: Credentials) -> bool:
        self._ensure_open()
        return self._accounts.get(credentials.username) == credentials.password

    def close(self) -> None:
        if self._accounts:
            raise RuntimeError("关闭AccountStore前必须清理测试账号")
        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("AccountStore已经关闭")


class SessionClient:
    def __init__(self, store: AccountStore) -> None:
        self._store = store
        self._current_user: str | None = None

    @property
    def current_user(self) -> str | None:
        return self._current_user

    def login(self, credentials: Credentials) -> None:
        if not self._store.authenticate(credentials):
            raise PermissionError("用户名或密码错误")
        self._current_user = credentials.username

    def logout(self) -> None:
        self._current_user = None

    def get_profile(self) -> dict[str, str]:
        if self._current_user is None:
            raise PermissionError("当前会话未登录")
        return {"username": self._current_user, "status": "active"}
