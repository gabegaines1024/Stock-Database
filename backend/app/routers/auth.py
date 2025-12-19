from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import cast
import logging
from app.database import get_db
from app.schemas.schemas import Token, UserCreate, User
from app.models.model import User as UserModel
from app.security import authenticate_user, create_access_token
from app.crud import create_user
from app.dependencies import get_current_user
from app.exceptions import UnauthorizedError, ConflictError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """Register a new user."""
    logger.info(f"Registration attempt for username: {user_data.username}")
    
    try:
        new_user = create_user(db, user_data)
        logger.info(f"User registered successfully: {user_data.username} (ID: {new_user.id})")
        # FastAPI will automatically convert SQLAlchemy model to Pydantic schema
        # using from_attributes=True, but we cast for type checking
        return cast(User, new_user)
    except ConflictError:
        # Re-raise conflict errors (already logged in create_user)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration for {user_data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """Authenticate user and return access token."""
    # Rate limiting is handled by the app's limiter middleware
    logger.info(f"Login attempt for username: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise UnauthorizedError("Incorrect username or password", "INVALID_CREDENTIALS")
    
    # Create access token with user ID
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    logger.info(f"User logged in successfully: {form_data.username} (ID: {user.id})")
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
) -> User:
    """Get current authenticated user information."""
    # FastAPI will automatically convert SQLAlchemy model to Pydantic schema
    # using from_attributes=True, but we cast for type checking
    return cast(User, current_user)