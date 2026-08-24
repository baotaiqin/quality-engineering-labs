from __future__ import annotations

import json
import socket
from pathlib import Path
from threading import Thread
from time import monotonic, sleep

import requests
import uvicorn

from auth_api.app import create_app


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "response_samples.json"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    port = free_port()
    server = uvicorn.Server(
        uvicorn.Config(
            create_app(),
            host="127.0.0.1",
            port=port,
            log_level="error",
        )
    )
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    deadline = monotonic() + 5
    while monotonic() < deadline:
        try:
            if requests.get(f"{base_url}/health", timeout=0.2).status_code == 200:
                break
        except requests.RequestException:
            sleep(0.05)
    else:
        raise RuntimeError("本地接口服务启动失败")

    try:
        session = requests.Session()
        register = session.post(
            f"{base_url}/api/users",
            json={"username": "capture_user", "password": "safe-pass-2026"},
            timeout=(1, 1),
        )
        login = session.post(
            f"{base_url}/api/login",
            json={"username": "capture_user", "password": "safe-pass-2026"},
            timeout=(1, 1),
        )
        token = login.json()["access_token"]
        session.headers["Authorization"] = f"Bearer {token}"
        profile = session.get(f"{base_url}/api/profile", timeout=(1, 1))
        logout = session.post(f"{base_url}/api/logout", timeout=(1, 1))
        after_logout = session.get(f"{base_url}/api/profile", timeout=(1, 1))

        samples = {
            "register": {"status": register.status_code, "body": register.json()},
            "login": {
                "status": login.status_code,
                "body": {**login.json(), "access_token": "<redacted>"},
            },
            "profile": {"status": profile.status_code, "body": profile.json()},
            "logout": {"status": logout.status_code, "body": None},
            "profile_after_logout": {
                "status": after_logout.status_code,
                "body": after_logout.json(),
            },
        }
        OUTPUT.write_text(
            json.dumps(samples, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"已保存脱敏响应：{OUTPUT}")
    finally:
        server.should_exit = True
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
