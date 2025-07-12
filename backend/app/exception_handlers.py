from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Union
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: Union[RequestValidationError, ValidationError]):
    """Custom handler for validation errors"""
    logger.error(f"Validation error on {request.url}: {exc}")
    
    if isinstance(exc, RequestValidationError):
        # FastAPI validation error
        errors = {}
        for error in exc.errors():
            field_name = " -> ".join(str(loc) for loc in error["loc"])
            if field_name not in errors:
                errors[field_name] = []
            errors[field_name].append(error["msg"])
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation failed",
                "error_type": "validation_error",
                "field_errors": errors
            }
        )
    
    elif isinstance(exc, ValidationError):
        # Pydantic validation error
        errors = {}
        for error in exc.errors():
            field_name = " -> ".join(str(loc) for loc in error["loc"])
            if field_name not in errors:
                errors[field_name] = []
            errors[field_name].append(error["msg"])
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Data validation failed",
                "error_type": "pydantic_validation_error",
                "field_errors": errors
            }
        )
    
    # Fallback
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "error_type": "unknown_validation_error"
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom handler for HTTP exceptions"""
    logger.error(f"HTTP error on {request.url}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": "http_error",
            "status_code": exc.status_code
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Custom handler for general exceptions"""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": "server_error"
        }
    )
