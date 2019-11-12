from datetime import datetime
from typing import Any  # noqa
from typing import List, Optional

from pydantic import BaseModel, Schema
from typing_extensions import Literal


class ApiResponse(BaseModel):
    code: "Optional[int]" = Schema(None, alias="code")  # type: ignore
    type: "Optional[str]" = Schema(None, alias="type")  # type: ignore
    message: "Optional[str]" = Schema(None, alias="message")  # type: ignore


class Category(BaseModel):
    id: "Optional[int]" = Schema(None, alias="id")  # type: ignore
    name: "Optional[str]" = Schema(None, alias="name")  # type: ignore


class Order(BaseModel):
    id: "Optional[int]" = Schema(None, alias="id")  # type: ignore
    pet_id: "Optional[int]" = Schema(None, alias="petId")  # type: ignore
    quantity: "Optional[int]" = Schema(None, alias="quantity")  # type: ignore
    ship_date: "Optional[datetime]" = Schema(None, alias="shipDate")  # type: ignore
    status: 'Literal["placed", "approved", "delivered"]' = Schema(None, alias="status")  # type: ignore
    complete: "Optional[bool]" = Schema(None, alias="complete")  # type: ignore


class Pet(BaseModel):
    id: "Optional[int]" = Schema(None, alias="id")  # type: ignore
    category: "Optional[Category]" = Schema(None, alias="category")  # type: ignore
    name: "str" = Schema(..., alias="name")  # type: ignore
    photo_urls: "List[str]" = Schema(..., alias="photoUrls")  # type: ignore
    tags: "Optional[List[Tag]]" = Schema(None, alias="tags")  # type: ignore
    status: 'Literal["available", "pending", "sold"]' = Schema(None, alias="status")  # type: ignore


class Tag(BaseModel):
    id: "Optional[int]" = Schema(None, alias="id")  # type: ignore
    name: "Optional[str]" = Schema(None, alias="name")  # type: ignore


class User(BaseModel):
    id: "Optional[int]" = Schema(None, alias="id")  # type: ignore
    username: "Optional[str]" = Schema(None, alias="username")  # type: ignore
    first_name: "Optional[str]" = Schema(None, alias="firstName")  # type: ignore
    last_name: "Optional[str]" = Schema(None, alias="lastName")  # type: ignore
    email: "Optional[str]" = Schema(None, alias="email")  # type: ignore
    password: "Optional[str]" = Schema(None, alias="password")  # type: ignore
    phone: "Optional[str]" = Schema(None, alias="phone")  # type: ignore
    user_status: "Optional[int]" = Schema(None, alias="userStatus")  # type: ignore
