# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Coroutine, List

from fastapi.encoders import jsonable_encoder

from fastapi_client import models as m

if TYPE_CHECKING:
    from fastapi_client.api_client import ApiClient


class UserApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    # ##################################
    # ##### Asynchronous Interface #####
    # ##################################
    async def create_user(self, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        return await self._build_for_create_user(body=body)

    async def create_users_with_array_input(self, body: List[m.User]) -> None:
        return await self._build_for_create_users_with_array_input(body=body)

    async def create_users_with_list_input(self, body: List[m.User]) -> None:
        return await self._build_for_create_users_with_list_input(body=body)

    async def delete_user(self, username: str) -> None:
        """
        This can only be done by the logged in user.
        """
        return await self._build_for_delete_user(username=username)

    async def get_user_by_name(self, username: str) -> m.User:
        return await self._build_for_get_user_by_name(username=username)

    async def login_user(self, username: str, password: str) -> str:
        return await self._build_for_login_user(username=username, password=password)

    async def logout_user(self,) -> None:
        return await self._build_for_logout_user()

    async def update_user(self, username: str, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        return await self._build_for_update_user(username=username, body=body)

    # #################################
    # ##### Synchronous Interface #####
    # #################################
    def create_user_sync(self, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        coroutine = self.create_user(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def create_users_with_array_input_sync(self, body: List[m.User]) -> None:
        coroutine = self.create_users_with_array_input(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def create_users_with_list_input_sync(self, body: List[m.User]) -> None:
        coroutine = self.create_users_with_list_input(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def delete_user_sync(self, username: str) -> None:
        """
        This can only be done by the logged in user.
        """
        coroutine = self.delete_user(username=username)
        return get_event_loop().run_until_complete(coroutine)

    def get_user_by_name_sync(self, username: str) -> m.User:
        coroutine = self.get_user_by_name(username=username)
        return get_event_loop().run_until_complete(coroutine)

    def login_user_sync(self, username: str, password: str) -> str:
        coroutine = self.login_user(username=username, password=password)
        return get_event_loop().run_until_complete(coroutine)

    def logout_user_sync(self,) -> None:
        coroutine = self.logout_user()
        return get_event_loop().run_until_complete(coroutine)

    def update_user_sync(self, username: str, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        coroutine = self.update_user(username=username, body=body)
        return get_event_loop().run_until_complete(coroutine)

    # ###################
    # ##### Private #####
    # ###################
    def _build_for_create_user(self, body: m.User) -> Coroutine[None, None, None]:
        """
        This can only be done by the logged in user.
        """
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/user", json=body)

    def _build_for_create_users_with_array_input(self, body: List[m.User]) -> Coroutine[None, None, None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/user/createWithArray", json=body)

    def _build_for_create_users_with_list_input(self, body: List[m.User]) -> Coroutine[None, None, None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/user/createWithList", json=body)

    def _build_for_delete_user(self, username: str) -> Coroutine[None, None, None]:
        """
        This can only be done by the logged in user.
        """
        path_params = {"username": str(username)}

        return self.api_client.request(type_=None, method="DELETE", url="/user/{username}", path_params=path_params)

    def _build_for_get_user_by_name(self, username: str) -> Coroutine[None, None, m.User]:
        path_params = {"username": str(username)}

        return self.api_client.request(type_=m.User, method="GET", url="/user/{username}", path_params=path_params)

    def _build_for_login_user(self, username: str, password: str) -> Coroutine[None, None, str]:
        query_params = {"username": str(username), "password": str(password)}

        return self.api_client.request(type_=str, method="GET", url="/user/login", params=query_params)

    def _build_for_logout_user(self,) -> Coroutine[None, None, None]:
        return self.api_client.request(type_=None, method="GET", url="/user/logout")

    def _build_for_update_user(self, username: str, body: m.User) -> Coroutine[None, None, None]:
        """
        This can only be done by the logged in user.
        """
        path_params = {"username": str(username)}

        body = jsonable_encoder(body)

        return self.api_client.request(
            type_=None, method="PUT", url="/user/{username}", path_params=path_params, json=body
        )
