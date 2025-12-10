from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.model import User as UserModel
from app.schemas import UserCreate, User, UserUpdate
from app.crud import create_user, get_user, get_user_by_id, list_users
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User)
def create_user_route(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> User:
    """Create a new user (requires authentication)."""
    try:
        return create_user(db, user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=User)
def get_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> User:
    """Get a user by its primary identifier (requires authentication)."""
    try:
        return get_user_by_id(db, user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[User])
def list_users_route(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> List[User]:
    """List all users (requires authentication)."""
    try:
        return list_users(db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))