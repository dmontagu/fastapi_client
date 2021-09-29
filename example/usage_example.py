from asyncio.events import get_event_loop
from functools import lru_cache

from fastapi.openapi.models import OAuthFlowPassword

from client.api_client import AsyncApiClient, AsyncApis, SyncApiClient, SyncApis
from example.client.auth import AuthMiddleware, AuthState
from example.client.models import User


class AutoAuthClient(AsyncApiClient):
    """
    You can add custom handling behavior by subclassing AsyncApiClient.

    This subclass adds automatic retry on auth errors via AuthMiddleware.
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


# lru_cache is used to (essentially) implement the singleton pattern for accessing the apis
@lru_cache()
def get_client() -> AutoAuthClient:
    return AutoAuthClient()


@lru_cache()
def get_sync_apis() -> SyncApis[AutoAuthClient]:
    return SyncApis(get_client())


@lru_cache()
def get_async_apis() -> AsyncApis[AutoAuthClient]:
    return AsyncApis(get_client())


async def do_some_async_tasks() -> None:
    apis = get_async_apis()

    await apis.store_api.delete_order(order_id=0)

    new_user = User(id=1, username="friend", password="globe")
    await apis.user_api.create_user(new_user)


def do_some_sync_tasks() -> None:
    apis = get_sync_apis()

    pet = apis.pet_api.get_pet_by_id(pet_id=1)
    pet.status = "sold"
    apis.pet_api.update_pet(pet)

    apis.store_api.delete_order(order_id=1)


get_client().set_creds(username="hello", password="world")

do_some_sync_tasks()

get_event_loop().run_until_complete(do_some_async_tasks())
