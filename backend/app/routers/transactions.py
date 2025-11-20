from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TransactionBase, Transaction, TransactionUpdate
from app.crud import create_transaction, get_transaction, update_transaction, delete_transaction, list_transactions
from typing import List

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=Transaction)
def create_transaction_route(transaction: TransactionBase, db: Session = Depends(get_db)) -> Transaction:
    """Create a new transaction."""
    try:
        return create_transaction(db, transaction)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction_route(transaction_id: int, db: Session = Depends(get_db)) -> Transaction:
    """Get a transaction by its primary identifier."""
    try:
        return get_transaction(db, transaction_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Transaction])
def list_transactions_route(db: Session = Depends(get_db)) -> List[Transaction]:
    """List all transactions."""
    try:
        return list_transactions(db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction_route(transaction_id: int, transaction: TransactionUpdate, db: Session = Depends(get_db)) -> Transaction:
    """Update a transaction by its primary identifier."""
    try:
        return update_transaction(db, transaction_id, transaction)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{transaction_id}", response_model=Transaction)
def delete_transaction_route(transaction_id: int, db: Session = Depends(get_db)) -> Transaction:
    """Delete a transaction by its primary identifier."""
    try:
        transaction = get_transaction(db, transaction_id)
        delete_transaction(db, transaction_id)
        return transaction
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))