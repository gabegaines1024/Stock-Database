from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.model import User
from app.schemas import TransactionBase, Transaction, TransactionUpdate
from app.crud import create_transaction, get_transaction, update_transaction, delete_transaction, list_transactions
from typing import List

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=Transaction)
def create_transaction_route(
    transaction: TransactionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    """Create a new transaction (portfolio must belong to authenticated user)."""
    try:
        return create_transaction(db, transaction, current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    """Get a transaction by its primary identifier (must belong to authenticated user's portfolio)."""
    try:
        return get_transaction(db, transaction_id, current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Transaction])
def list_transactions_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Transaction]:
    """List all transactions for the authenticated user's portfolios."""
    try:
        return list_transactions(db, current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction_route(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    """Update a transaction by its primary identifier (must belong to authenticated user's portfolio)."""
    try:
        return update_transaction(db, transaction_id, transaction, current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{transaction_id}", response_model=Transaction)
def delete_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    """Delete a transaction by its primary identifier (must belong to authenticated user's portfolio)."""
    try:
        transaction = get_transaction(db, transaction_id, current_user.id)
        delete_transaction(db, transaction_id, current_user.id)
        return transaction
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))