"""
Regression tests for fastapi_client
"""
import hashlib
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, Query
from starlette.requests import Request

from ..models import FormPostResponse, ListTagsResponse


def client_router() -> APIRouter:
    """
    Returns the router for regression test endpoints
    """
    router = APIRouter()

    @router.get("/any")
    async def no_schema() -> Dict[str, str]:
        """
        Testing endpoints with no response_model. The client should return the dict
        unmodified
        """
        return {"hello": "world"}

    @router.post("/file_upload", response_model=FormPostResponse)
    async def file_upload(
        request: Request, file: bytes = File(...), token: Optional[str] = Form(...)
    ) -> FormPostResponse:
        """
        Testing file uploads using multipart/form. Responds with the size and hash of the file,
        the token and the content-type of the incoming request
        """
        hash_text: Optional[str]
        if file:
            hash_text = hashlib.sha256(file).hexdigest()
            length = len(file)
        else:
            hash_text = None
            length = 0
        content_type = request.headers.get("content-type", None)
        return FormPostResponse(length=length, hash=hash_text, token=token, content_type=content_type)

    @router.post("/form_upload", response_model=FormPostResponse)
    async def form_upload(request: Request, token: Optional[str] = Form(...)) -> FormPostResponse:
        """
        Testing forms using application/x-www-form-urlencoded
        returns the token & the request's content-type
        """
        content_type = request.headers.get("content-type", None)
        return FormPostResponse(token=token, content_type=content_type)

    @router.get("/tags_list", response_model=ListTagsResponse)
    async def tags_list(tags: List[str] = Query(None)) -> ListTagsResponse:
        """
        Check client with list of items in the query. Client should send <url>?tags=1&tags=2&tags=3
        Responds with the sent tags list
        """
        return ListTagsResponse(tags=tags)

    return router
