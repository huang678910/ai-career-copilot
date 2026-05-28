from pydantic import BaseModel


class APIResponse(BaseModel):
    data: object | None = None
    message: str = "ok"


class ErrorResponse(BaseModel):
    error: dict


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    data: list
    meta: dict
