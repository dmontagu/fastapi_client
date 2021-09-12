from typing import Dict

from fastapi.openapi.models import OAuthFlowPassword
from generated_client.api_client import AsyncApiClient
from generated_client.auth import AuthMiddleware, AuthState


class AutoAuthClient(AsyncApiClient):
    """
    Subclasses AsyncApiClient to add some extra functionality
    """

    def __init__(self, host: str = "http://localhost", tokenUrl: str = "http://localhost/token"):
        super().__init__(host)
        self.auth_state = AuthState()
        flow = OAuthFlowPassword(tokenUrl=tokenUrl)
        auth_middleware = AuthMiddleware(auth_state=self.auth_state, flow=flow)
        self.add_middleware(auth_middleware)

    def set_creds(self, username: str, password: str) -> None:
        self.auth_state.username = username
        self.auth_state.password = password


def test_auth() -> None:
    client = AutoAuthClient(host="http://localhost:8000", tokenUrl="http://localhost:8000/token")
    client.set_creds("username", "password")
    result = client.request_sync(type_=Dict, method="GET", url="/")
    assert result == {"result": "success"}
    assert client.auth_state.access_token == "access_token"
