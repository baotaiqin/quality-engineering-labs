from __future__ import annotations

from dataclasses import dataclass
from secrets import token_urlsafe
from threading import RLock


@dataclass(frozen=True)
class User:
    username: str
    password: str


class AuthStore:
    """保存本地接口服务中的账号和会话。"""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._tokens: dict[str, str] = {}
        self._lock = RLock()

    def create_user(self, username: str, password: str) -> None:
        with self._lock:
            if username in self._users:
                raise ValueError("用户名已存在")
            self._users[username] = User(username=username, password=password)

    def authenticate(self, username: str, password: str) -> str | None:
        with self._lock:
            user = self._users.get(username)
            if user is None or user.password != password:
                return None
            token = token_urlsafe(24)
            self._tokens[token] = username
            return token

    def username_for_token(self, token: str) -> str | None:
        with self._lock:
            return self._tokens.get(token)

    def revoke_token(self, token: str) -> None:
        with self._lock:
            self._tokens.pop(token, None)

    def delete_user(self, username: str) -> None:
        with self._lock:
            self._users.pop(username, None)
            expired_tokens = [
                token
                for token, token_username in self._tokens.items()
                if token_username == username
            ]
            for token in expired_tokens:
                self._tokens.pop(token, None)

    def reset(self) -> None:
        with self._lock:
            self._users.clear()
            self._tokens.clear()
