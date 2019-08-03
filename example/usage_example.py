from asyncio.events import get_event_loop
from functools import lru_cache

from fastapi.openapi.models import OAuthFlowPassword

from fastapi_client.api_client import ApiClient, Apis
from fastapi_client.auth import AuthMiddleware, AuthState
from fastapi_client.models import User


class AutoAuthClient(ApiClient):
    """
    Subclasses ApiClient to add some extra functionality
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


@lru_cache()
def get_apis() -> Apis[AutoAuthClient]:
    client = AutoAuthClient()
    return Apis(client)


def set_apis_creds(username: str, password: str) -> None:
    get_apis().client.set_creds(username=username, password=password)


set_apis_creds("hello", "world")


async def do_some_tasks() -> None:
    apis = get_apis()

    apis.store_api.delete_order(order_id=0)

    new_user = User(id=1, username="friend", password="globe")
    apis.user_api.create_user(new_user)


def do_some_sync_tasks() -> None:
    apis = get_apis()

    pet = apis.pet_api.get_pet_by_id_sync(pet_id=1)
    pet.status = "sold"
    apis.pet_api.update_pet_sync(pet)

    apis.store_api.delete_order(order_id=1)


do_some_sync_tasks()
get_event_loop().run_until_complete(do_some_tasks())
