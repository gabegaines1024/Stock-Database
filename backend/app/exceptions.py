"""Custom exception classes for standardized error handling."""
from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class AppException(HTTPException):
    """Base exception class for application-specific errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: Optional[Any] = None, error_code: str = "NOT_FOUND"):
        detail = f"{resource} not found"
        if identifier is not None:
            detail = f"{resource} with id {identifier} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )


class UnauthorizedError(AppException):
    """Raised when authentication is required or fails."""
    
    def __init__(self, detail: str = "Authentication required", error_code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(AppException):
    """Raised when user doesn't have permission to access a resource."""
    
    def __init__(self, detail: str = "Permission denied", error_code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class ConflictError(AppException):
    """Raised when a resource conflict occurs (e.g., duplicate entry)."""
    
    def __init__(self, detail: str, error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )


class ExternalServiceError(AppException):
    """Raised when an external service (e.g., stock API) fails."""
    
    def __init__(self, service: str, detail: str, error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service} error: {detail}",
            error_code=error_code
        )


class DatabaseError(AppException):
    """Raised when a database operation fails."""
    
    def __init__(self, detail: str, error_code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}",
            error_code=error_code
        )


class BusinessLogicError(AppException):
    """Raised when a business rule is violated."""
    
    def __init__(self, detail: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )

