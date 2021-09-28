from asyncio import get_event_loop
from typing import Any, Awaitable, Callable, Dict, Generic, Type, TypeVar, overload

from httpx import AsyncClient, Request, Response
from pydantic import ValidationError, parse_obj_as

from example.client.api.pet_api import AsyncPetApi, SyncPetApi
from example.client.api.store_api import AsyncStoreApi, SyncStoreApi
from example.client.api.user_api import AsyncUserApi, SyncUserApi
from example.client.exceptions import ResponseHandlingException, UnexpectedResponse

AsyncClientT = TypeVar("AsyncClientT", bound="AsyncApiClient")


class AsyncApis(Generic[AsyncClientT]):
    def __init__(self, client: AsyncClientT):
        self.client = client

        self.pet_api = AsyncPetApi(self.client)
        self.store_api = AsyncStoreApi(self.client)
        self.user_api = AsyncUserApi(self.client)


class SyncApis(Generic[AsyncClientT]):
    def __init__(self, client: AsyncClientT):
        self.client = client

        self.pet_api = SyncPetApi(self.client)
        self.store_api = SyncStoreApi(self.client)
        self.user_api = SyncUserApi(self.client)


T = TypeVar("T")
AsyncSend = Callable[[Request], Awaitable[Response]]
AsyncMiddlewareT = Callable[[Request, AsyncSend], Awaitable[Response]]


class AsyncApiClient:
    def __init__(self, host: str = None, **kwargs: Any) -> None:
        self.host = host
        self.middleware: AsyncMiddlewareT = BaseAsyncMiddleware()
        self._async_client = AsyncClient(**kwargs)

    @overload
    async def request(
        self, *, type_: Type[T], method: str, url: str, path_params: Dict[str, Any] = None, **kwargs: Any
    ) -> T:
        ...

    @overload  # noqa F811
    async def request(
        self, *, type_: None, method: str, url: str, path_params: Dict[str, Any] = None, **kwargs: Any
    ) -> None:
        ...

    async def request(  # noqa F811
        self, *, type_: Any, method: str, url: str, path_params: Dict[str, Any] = None, **kwargs: Any
    ) -> Any:
        if path_params is None:
            path_params = {}
        url = (self.host or "") + url.format(**path_params)
        request = Request(method, url, **kwargs)
        return await self.send(request, type_)

    async def send(self, request: Request, type_: Type[T]) -> T:
        response = await self.middleware(request, self.send_inner)
        if response.status_code in [200, 201]:
            try:
                return parse_obj_as(type_, response.json())
            except ValidationError as e:
                raise ResponseHandlingException(e)
        raise UnexpectedResponse.for_response(response)

    async def send_inner(self, request: Request) -> Response:
        try:
            response = await self._async_client.send(request)
        except Exception as e:
            raise ResponseHandlingException(e)
        return response

    def add_middleware(self, middleware: AsyncMiddlewareT) -> None:
        current_middleware = self.middleware

        async def new_middleware(request: Request, call_next: AsyncSend) -> Response:
            async def inner_send(request: Request) -> Response:
                return await current_middleware(request, call_next)

            return await middleware(request, inner_send)

        self.middleware = new_middleware


class BaseAsyncMiddleware:
    async def __call__(self, request: Request, call_next: AsyncSend) -> Response:
        return await call_next(request)
