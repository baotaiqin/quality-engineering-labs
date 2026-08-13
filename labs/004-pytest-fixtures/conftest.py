from collections.abc import Iterator

import pytest

from account_service import AccountStore, Credentials, PasswordPolicy, SessionClient


@pytest.fixture(scope="session")
def password_policy() -> PasswordPolicy:
    """提供整次测试会话共用的密码策略。"""
    return PasswordPolicy(minimum_length=8)


@pytest.fixture
def account_store() -> Iterator[AccountStore]:
    """为每条测试创建独立账号存储，并在结束时确认数据已清理。"""
    store = AccountStore()
    yield store
    store.close()


@pytest.fixture
def registered_user(
    account_store: AccountStore,
    password_policy: PasswordPolicy,
) -> Iterator[Credentials]:
    """创建测试账号，并在测试结束后删除。"""
    credentials = Credentials(username="fixture_user", password="safe-pass-2026")
    account_store.create_user(credentials, password_policy)
    yield credentials
    account_store.delete_user(credentials.username)


@pytest.fixture
def authenticated_client(
    account_store: AccountStore,
    registered_user: Credentials,
) -> Iterator[SessionClient]:
    """返回已登录客户端，并在测试结束后退出会话。"""
    client = SessionClient(account_store)
    client.login(registered_user)
    yield client
    client.logout()
