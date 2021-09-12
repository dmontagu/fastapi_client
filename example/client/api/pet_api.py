# flake8: noqa E501
from asyncio import get_event_loop
from typing import IO, TYPE_CHECKING, Any, Awaitable, Dict, List

from fastapi.encoders import jsonable_encoder

from example.client import models as m

if TYPE_CHECKING:
    from example.client.api_client import AsyncApiClient


class _PetApi:
    def __init__(self, api_client: "AsyncApiClient"):
        self.api_client = api_client

    def _build_for_add_pet(self, body: m.Pet) -> Awaitable[None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/pet", json=body)

    def _build_for_delete_pet(self, pet_id: int, api_key: str = None) -> Awaitable[None]:
        path_params = {"petId": str(pet_id)}

        headers = {}
        if api_key is not None:
            headers["api_key"] = str(api_key)

        return self.api_client.request(
            type_=None,
            method="DELETE",
            url="/pet/{petId}",
            path_params=path_params,
            headers=headers,
        )

    def _build_for_find_pets_by_status(self, status: List[str]) -> Awaitable[List[m.Pet]]:
        """
        Multiple status values can be provided with comma separated strings
        """
        query_params = {"status": str(status)}

        return self.api_client.request(
            type_=List[m.Pet],
            method="GET",
            url="/pet/findByStatus",
            params=query_params,
        )

    def _build_for_find_pets_by_tags(self, tags: List[str]) -> Awaitable[List[m.Pet]]:
        """
        Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.
        """
        query_params = {"tags": str(tags)}

        return self.api_client.request(
            type_=List[m.Pet],
            method="GET",
            url="/pet/findByTags",
            params=query_params,
        )

    def _build_for_get_pet_by_id(self, pet_id: int) -> Awaitable[m.Pet]:
        """
        Returns a single pet
        """
        path_params = {"petId": str(pet_id)}

        return self.api_client.request(
            type_=m.Pet,
            method="GET",
            url="/pet/{petId}",
            path_params=path_params,
        )

    def _build_for_update_pet(self, body: m.Pet) -> Awaitable[None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="PUT", url="/pet", json=body)

    def _build_for_update_pet_with_form(self, pet_id: int, name: str = None, status: str = None) -> Awaitable[None]:
        path_params = {"petId": str(pet_id)}

        files: Dict[str, IO[Any]] = {}  # noqa F841
        data: Dict[str, Any] = {}  # noqa F841
        if name is not None:
            data["name"] = name
        if status is not None:
            data["status"] = status

        return self.api_client.request(
            type_=None, method="POST", url="/pet/{petId}", path_params=path_params, data=data, files=files or None
        )

    def _build_for_upload_file(
        self, pet_id: int, additional_metadata: str = None, file: IO[Any] = None
    ) -> Awaitable[m.ApiResponse]:
        path_params = {"petId": str(pet_id)}

        files: Dict[str, IO[Any]] = {}  # noqa F841
        data: Dict[str, Any] = {}  # noqa F841
        if additional_metadata is not None:
            data["additionalMetadata"] = additional_metadata
        if file is not None:
            files["file"] = file

        return self.api_client.request(
            type_=m.ApiResponse,
            method="POST",
            url="/pet/{petId}/uploadImage",
            path_params=path_params,
            data=data,
            files=files,
        )


class AsyncPetApi(_PetApi):
    async def add_pet(self, body: m.Pet) -> None:
        return await self._build_for_add_pet(body=body)

    async def delete_pet(self, pet_id: int, api_key: str = None) -> None:
        return await self._build_for_delete_pet(pet_id=pet_id, api_key=api_key)

    async def find_pets_by_status(self, status: List[str]) -> List[m.Pet]:
        """
        Multiple status values can be provided with comma separated strings
        """
        return await self._build_for_find_pets_by_status(status=status)

    async def find_pets_by_tags(self, tags: List[str]) -> List[m.Pet]:
        """
        Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.
        """
        return await self._build_for_find_pets_by_tags(tags=tags)

    async def get_pet_by_id(self, pet_id: int) -> m.Pet:
        """
        Returns a single pet
        """
        return await self._build_for_get_pet_by_id(pet_id=pet_id)

    async def update_pet(self, body: m.Pet) -> None:
        return await self._build_for_update_pet(body=body)

    async def update_pet_with_form(self, pet_id: int, name: str = None, status: str = None) -> None:
        return await self._build_for_update_pet_with_form(pet_id=pet_id, name=name, status=status)

    async def upload_file(self, pet_id: int, additional_metadata: str = None, file: IO[Any] = None) -> m.ApiResponse:
        return await self._build_for_upload_file(pet_id=pet_id, additional_metadata=additional_metadata, file=file)


class SyncPetApi(_PetApi):
    def add_pet(self, body: m.Pet) -> None:
        coroutine = self._build_for_add_pet(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def delete_pet(self, pet_id: int, api_key: str = None) -> None:
        coroutine = self._build_for_delete_pet(pet_id=pet_id, api_key=api_key)
        return get_event_loop().run_until_complete(coroutine)

    def find_pets_by_status(self, status: List[str]) -> List[m.Pet]:
        """
        Multiple status values can be provided with comma separated strings
        """
        coroutine = self._build_for_find_pets_by_status(status=status)
        return get_event_loop().run_until_complete(coroutine)

    def find_pets_by_tags(self, tags: List[str]) -> List[m.Pet]:
        """
        Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.
        """
        coroutine = self._build_for_find_pets_by_tags(tags=tags)
        return get_event_loop().run_until_complete(coroutine)

    def get_pet_by_id(self, pet_id: int) -> m.Pet:
        """
        Returns a single pet
        """
        coroutine = self._build_for_get_pet_by_id(pet_id=pet_id)
        return get_event_loop().run_until_complete(coroutine)

    def update_pet(self, body: m.Pet) -> None:
        coroutine = self._build_for_update_pet(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def update_pet_with_form(self, pet_id: int, name: str = None, status: str = None) -> None:
        coroutine = self._build_for_update_pet_with_form(pet_id=pet_id, name=name, status=status)
        return get_event_loop().run_until_complete(coroutine)

    def upload_file(self, pet_id: int, additional_metadata: str = None, file: IO[Any] = None) -> m.ApiResponse:
        coroutine = self._build_for_upload_file(pet_id=pet_id, additional_metadata=additional_metadata, file=file)
        return get_event_loop().run_until_complete(coroutine)
