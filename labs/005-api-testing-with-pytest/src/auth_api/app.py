from time import sleep
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from auth_api.store import AuthStore


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=64)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class ProfileResponse(BaseModel):
    username: str
    status: str


def create_app(store: AuthStore | None = None) -> FastAPI:
    app = FastAPI(title="Local Auth API", version="1.0.0")
    app.state.auth_store = store or AuthStore()
    bearer = HTTPBearer(auto_error=False)

    def current_credentials(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(bearer),
        ],
    ) -> tuple[str, str]:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_REQUIRED", "message": "需要Bearer Token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        username = app.state.auth_store.username_for_token(credentials.credentials)
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "TOKEN_INVALID", "message": "Token无效或已失效"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username, credentials.credentials

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/users", status_code=status.HTTP_201_CREATED)
    def register(payload: RegisterRequest) -> dict[str, str]:
        try:
            app.state.auth_store.create_user(payload.username, payload.password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "USER_EXISTS", "message": str(exc)},
            ) from exc
        return {"username": payload.username, "status": "active"}

    @app.post("/api/login", response_model=TokenResponse)
    def login(payload: LoginRequest) -> TokenResponse:
        token = app.state.auth_store.authenticate(payload.username, payload.password)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "用户名或密码错误",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=3600,
        )

    @app.get("/api/profile", response_model=ProfileResponse)
    def profile(
        auth: Annotated[tuple[str, str], Depends(current_credentials)],
    ) -> ProfileResponse:
        username, _ = auth
        return ProfileResponse(username=username, status="active")

    @app.post("/api/logout", status_code=status.HTTP_204_NO_CONTENT)
    def logout(
        auth: Annotated[tuple[str, str], Depends(current_credentials)],
    ) -> Response:
        _, token = auth
        app.state.auth_store.revoke_token(token)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.delete("/api/users/me", status_code=status.HTTP_204_NO_CONTENT)
    def delete_current_user(
        auth: Annotated[tuple[str, str], Depends(current_credentials)],
    ) -> Response:
        username, _ = auth
        app.state.auth_store.delete_user(username)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.get("/api/slow")
    def slow_response(
        delay_ms: Annotated[int, Query(ge=0, le=1000)] = 200,
    ) -> dict[str, int]:
        sleep(delay_ms / 1000)
        return {"delay_ms": delay_ms}

    return app


app = create_app()
