from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from app.database import get_db
from app.dependencies import get_current_user
from app.models.model import User
from app.schemas import TransactionBase, Transaction, TransactionUpdate, TransactionCreate
from app.crud import create_transaction, get_transaction, update_transaction, delete_transaction, list_transactions
from app.services.transaction_service import get_current_position
from app.exceptions import BusinessLogicError
from typing import List, cast

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=Transaction)
def create_transaction_route(
    transaction: TransactionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    """Create a new transaction (portfolio must belong to authenticated user)."""
    logger.info(
        f"Creating {transaction.transaction_type} transaction: "
        f"{transaction.quantity} shares of {transaction.ticker_symbol} at ${transaction.price}"
    )
    try:
        # If transaction type is SELL, check if sufficient holdings exist
        if transaction.transaction_type.lower() == "sell":
            current_position = get_current_position(
                portfolio_id=transaction.portfolio_id,
                ticker=transaction.ticker_symbol,
                db=db
            )
            
            if transaction.quantity > current_position:
                logger.warning(
                    f"Insufficient holdings: trying to sell {transaction.quantity} "
                    f"but only {current_position} available for {transaction.ticker_symbol}"
                )
                raise BusinessLogicError(
                    f"Insufficient holdings. You have {current_position} shares, "
                    f"but trying to sell {transaction.quantity}.",
                    "INSUFFICIENT_HOLDINGS"
                )
        
        transaction_create = TransactionCreate(**transaction.model_dump())
        created = create_transaction(db, transaction_create, current_user.id)
        return cast(Transaction, created)
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
        transaction = get_transaction(db, transaction_id, current_user.id)
        return cast(Transaction, transaction)
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
        transactions = list_transactions(db, current_user.id)
        return cast(List[Transaction], transactions)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/position/{portfolio_id}/{ticker}")
def get_position_route(
    portfolio_id: int,
    ticker: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get the current position (available quantity) for a portfolio and ticker."""
    try:
        # Verify portfolio belongs to user
        from app.models.model import Portfolio
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        position = get_current_position(portfolio_id=portfolio_id, ticker=ticker, db=db)
        return {"portfolio_id": portfolio_id, "ticker": ticker.upper(), "position": position}
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
        updated = update_transaction(db, transaction_id, transaction, current_user.id)
        return cast(Transaction, updated)
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
        return cast(Transaction, transaction)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))