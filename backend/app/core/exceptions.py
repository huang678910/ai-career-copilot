from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str = "ERROR"):
        self.code = code
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail, code="UNAUTHORIZED")


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=403, detail=detail, code="FORBIDDEN")


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, code="NOT_FOUND")


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail, code="CONFLICT")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": {"code": exc.code, "message": exc.detail}},
    )
