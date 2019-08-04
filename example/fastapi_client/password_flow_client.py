"""
Attempting to follow the "password" flow as described in RFC 6749: https://tools.ietf.org/html/rfc6749
"""
from asyncio import get_event_loop
from contextlib import suppress
from enum import Enum
from typing import List, Optional, Union

from fastapi.openapi.models import OAuthFlowPassword
from httpx import AsyncClient, AsyncResponse
from pydantic import BaseModel, ValidationError
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from typing_extensions import Literal

from fastapi_client.exceptions import UnexpectedResponse


class AccessTokenRequest(BaseModel):
    """
    Specific to the OAuth2.0 "password" flow
    """

    grant_type: Literal["password"] = "password"
    username: str
    password: str
    scope: Optional[str]

    @staticmethod
    def from_scopes(username: str, password: str, scopes: Optional[List[str]] = None) -> "AccessTokenRequest":
        scope = " ".join(scopes) if scopes is not None else None
        return AccessTokenRequest(username=username, password=password, scope=scope)


class RefreshTokenRequest(BaseModel):
    grant_type: Literal["refresh_token"] = "refresh_token"
    refresh_token: str
    scope: Optional[str]

    @staticmethod
    def from_scopes(refresh_token: str, scopes: Optional[List[str]] = None) -> "RefreshTokenRequest":
        scope = " ".join(scopes) if scopes is not None else None
        return RefreshTokenRequest(refresh_token=refresh_token, scope=scope)


class TokenSuccessResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int]
    refresh_token: Optional[str]
    scope: Optional[str]


class TokenErrorType(Enum):
    invalid_request = "invalid_request"
    invalid_client = "invalid_client"
    invalid_grant = "invalid_grant"
    unauthorized_client = "unauthorized_client"
    unsupported_grant_type = "unsupported_grant_type"
    invalid_scope = "invalid_scope"


class TokenErrorResponse(BaseModel):
    error: Union[TokenErrorType, str]
    error_description: Optional[str]
    error_uri: Optional[str]


TokenResponse = Union[TokenSuccessResponse, TokenErrorResponse]


def parse_token_response(response: AsyncResponse) -> TokenResponse:
    with suppress(ValidationError):
        if response.status_code == HTTP_200_OK:
            return TokenSuccessResponse.parse_raw(response.text)
        if response.status_code in (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED):
            return TokenErrorResponse.parse_raw(response.text)
    raise UnexpectedResponse.for_response(response)


class PasswordFlowClient:
    def __init__(self, flow: OAuthFlowPassword) -> None:
        self.flow = flow
        self._async_client = AsyncClient()

    async def request_access_token(self, access_token_request: AccessTokenRequest) -> TokenResponse:
        response = await self._async_client.post(self.flow.tokenUrl, data=access_token_request.dict())
        return parse_token_response(response)

    async def request_refresh_token(self, refresh_token_request: RefreshTokenRequest) -> TokenResponse:
        refresh_url = self.flow.refreshUrl or self.flow.tokenUrl
        response = await self._async_client.post(refresh_url, data=refresh_token_request.dict())
        return parse_token_response(response)

    def request_access_token_sync(self, access_token_request: AccessTokenRequest) -> TokenResponse:
        return get_event_loop().run_until_complete(self.request_access_token(access_token_request))

    def request_refresh_token_sync(self, refresh_token_request: RefreshTokenRequest) -> TokenResponse:
        return get_event_loop().run_until_complete(self.request_refresh_token(refresh_token_request))
