from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import cast
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.schemas.schemas import Token, UserCreate, User
from app.models.model import User as UserModel
from app.security import authenticate_user, create_access_token
from app.crud import create_user
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """Register a new user."""
    # Check if username already exists
    existing_user = db.query(UserModel).filter(UserModel.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        new_user = create_user(db, user_data)
        # FastAPI will automatically convert SQLAlchemy model to Pydantic schema
        # using from_attributes=True, but we cast for type checking
        return cast(User, new_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Limit to 5 login attempts per minute to prevent brute force
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """Authenticate user and return access token (rate limited to prevent brute force attacks)."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with user ID
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
) -> User:
    """Get current authenticated user information."""
    # FastAPI will automatically convert SQLAlchemy model to Pydantic schema
    # using from_attributes=True, but we cast for type checking
    return cast(User, current_user)