# -*- coding: utf-8 -*-
"""
Pydantic data models for the server.
"""

from typing import List, Optional

from pydantic import BaseModel


class FormPostResponse(BaseModel):
    """Response from the form testing"""

    length: int = 0
    hash: Optional[str] = None
    token: Optional[str] = None
    content_type: Optional[str] = None


class ListTagsResponse(BaseModel):
    """Response from lists in query test"""

    tags: List[str]
