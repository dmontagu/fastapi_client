from contextlib import suppress
from datetime import datetime, timedelta
from typing import Optional

from fastapi.openapi.models import OAuthFlowPassword
from httpx import Request, Response
from pydantic import BaseModel

from example.client.api_client import AsyncSend
from example.client.exceptions import UnexpectedResponse
from example.client.password_flow_client import (
    AccessTokenRequest,
    PasswordFlowClient,
    RefreshTokenRequest,
    TokenSuccessResponse,
)

HTTP_401_UNAUTHORIZED = 401


class AuthState(BaseModel):
    username: Optional[str]
    password: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    expires_at: Optional[datetime]  # should be UTC
    scope: Optional[str]

    def get_login_request(self) -> Optional[AccessTokenRequest]:
        if self.username is None or self.password is None:
            return None
        return AccessTokenRequest(username=self.username, password=self.password, scope=self.scope)

    def get_refresh_request(self) -> Optional[RefreshTokenRequest]:
        if self.refresh_token is None:
            return None
        return RefreshTokenRequest(refresh_token=self.refresh_token, scope=self.scope)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return self.expires_at < datetime.utcnow() + timedelta(seconds=30)

    def update(self, token_success_response: TokenSuccessResponse) -> None:
        self.access_token = token_success_response.access_token
        self.refresh_token = token_success_response.refresh_token
        self.scope = token_success_response.scope
        if token_success_response.expires_in is not None:
            self.expires_at = datetime.utcnow() + timedelta(seconds=token_success_response.expires_in)


class AuthMiddleware:
    def __init__(self, auth_state: AuthState, flow: OAuthFlowPassword) -> None:
        self.auth_state = auth_state
        self.flow_client = PasswordFlowClient(flow)

    @staticmethod
    def set_access_header(token: str, request: Request, *, replace: bool) -> None:
        key = "authorization"
        value = f"bearer {token}"
        if replace:
            request.headers[key] = value
        else:
            request.headers.setdefault(key, value)

    async def login(self) -> Optional[TokenSuccessResponse]:
        access_token_request = self.auth_state.get_login_request()
        if access_token_request is None:
            return None
        with suppress(UnexpectedResponse):
            token_response = await self.flow_client.request_access_token(access_token_request)
            if isinstance(token_response, TokenSuccessResponse):
                self.update_auth_state(token_response)
                return token_response
        return None

    async def refresh(self) -> Optional[TokenSuccessResponse]:
        refresh_token_request = self.auth_state.get_refresh_request()
        if refresh_token_request is None:
            return None
        with suppress(UnexpectedResponse):
            token_response = await self.flow_client.request_refresh_token(refresh_token_request)
            if isinstance(token_response, TokenSuccessResponse):
                self.update_auth_state(token_response)
                return token_response
        return None

    async def __call__(self, request: Request, call_next: AsyncSend) -> Response:
        if self.auth_state.is_expired():
            await self.refresh()
        access_token = self.auth_state.access_token
        if access_token is not None:
            self.set_access_header(access_token, request, replace=False)

        response = await call_next(request)

        if response.status_code != HTTP_401_UNAUTHORIZED:
            return response
        tokens = await self.refresh()
        if tokens is None:
            tokens = await self.login()
        if tokens:
            self.set_access_header(tokens.access_token, request, replace=True)
            return await call_next(request)  # note: won't work with streaming input
        return response

    def update_auth_state(self, tokens: TokenSuccessResponse) -> None:
        """
        Override this function if you want a hook for caching the access/refresh tokens
        """
        self.auth_state.update(tokens)
