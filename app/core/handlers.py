# from fastapi import FastAPI, Request, status
# from fastapi.responses import JSONResponse
# from app.core.exceptions import (
#     AuthError, 
#     PermissionDeniedError, 
#     DuplicateResourceError, 
#     ResourceNotFoundError,
#     BadRequestError
# )

# def register_exception_handlers(app: FastAPI) -> None:
#     """
#     Wires custom operational domain exception hooks onto the core FastAPI app instance.
#     """
    
#     @app.exception_handler(AuthError)
#     async def auth_error_handler(request: Request, exc: AuthError):
#         return JSONResponse(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             content={"detail": exc.detail}
#         )

#     @app.exception_handler(PermissionDeniedError)
#     async def permission_error_handler(request: Request, exc: PermissionDeniedError):
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content={"detail": exc.detail}
#         )

#     @app.exception_handler(DuplicateResourceError)
#     async def duplicate_resource_handler(request: Request, exc: DuplicateResourceError):
#         return JSONResponse(
#             status_code=status.HTTP_409_CONFLICT,
#             content={"detail": exc.detail}
#         )

#     @app.exception_handler(ResourceNotFoundError)
#     async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
#         return JSONResponse(
#             status_code=status.HTTP_404_NOT_FOUND,
#             content={"detail": exc.detail}
#         )

#     @app.exception_handler(BadRequestError)
#     async def bad_request_handler(request: Request, exc: BadRequestError):
#         return JSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={"detail": exc.detail}
#         )

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.exceptions import BasePortalError

logger = logging.getLogger("app.core.handlers")

def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers to clean up API error responses."""
    
    @app.exception_handler(BasePortalError)
    async def custom_portal_exception_handler(request: Request, exc: BasePortalError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "detail": exc.message
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Format Pydantic field validation errors cleanly
        errors = []
        for error in exc.errors():
            # Standardize field location path representation
            field_path = " -> ".join(str(loc_item) for loc_item in error.get("loc", []))
            errors.append({
                "field": field_path,
                "message": error.get("msg"),
                "type": error.get("type")
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "InputValidationError",
                "detail": "One or more request parameters failed validation constraints.",
                "errors": errors
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTPException",
                "detail": exc.detail
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error encountered: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "DatabaseError",
                "detail": "A database operation error occurred while processing your request."
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled system error encountered: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "detail": "An unexpected error occurred. Please contact system support."
            }
        )