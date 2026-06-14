from pydantic import BaseModel
from typing import Optional, Any


class MessageResponse(BaseModel):
    message: str


class ErrorDetail(BaseModel):
    detail: str


class PaginatedResponse(BaseModel):
    data: list[Any]
    total: int
    page: int
    per_page: int
