from datetime import datetime
from fastapi import HTTPException
from collections.abc import Iterable
from typing import Optional, List
import logging

from sqlalchemy.orm import Session

from app.models import User, Stock, Portfolio, Transaction
from app.schemas import StockCreate, StockUpdate, PortfolioCreate, PortfolioUpdate, TransactionCreate, TransactionUpdate, UserCreate, UserUpdate
from app.security import hash_password
from app.exceptions import NotFoundError, ConflictError, DatabaseError, ValidationError

logger = logging.getLogger(__name__)


def create_stock(db: Session, stock: StockCreate) -> Stock:
    """Create a new stock record in the database."""
    db_stock = Stock(ticker_symbol=stock.ticker_symbol, company_name=stock.company_name, sector=stock.sector)
    try:
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        return db_stock
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def get_stock(db: Session, stock_id: int) -> Optional[Stock]:
    """Retrieve a stock by its primary identifier."""
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock

def get_stock_by_ticker(db: Session, ticker: str) -> Optional[Stock]:
    """Retrieve a stock by its ticker symbol."""
    db_stock = db.query(Stock).filter(Stock.ticker_symbol == ticker).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock


def list_stocks(db: Session) -> List[Stock]:
    """Return a list of all stored stocks."""
    db_stocks = db.query(Stock).all()
    return db_stocks


def update_stock(db: Session, stock_id: int, stock: StockUpdate) -> Stock:
    """Update an existing stock record."""
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    update_data = stock.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_stock, field, value)
    try:
        db.commit()
        db.refresh(db_stock)
        return db_stock
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_stock(db: Session, stock_id: int) -> None:
    """Delete a stock record from the database."""
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    try:
        db.delete(db_stock)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def create_portfolio(db: Session, portfolio: PortfolioCreate, user_id: int) -> Portfolio:
    """Create a new portfolio record."""
    db_portfolio = Portfolio(name=portfolio.name, user_id=user_id)
    try:
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_portfolio(db: Session, portfolio_id: int, user_id: int) -> Portfolio:
    """Retrieve a portfolio by its primary identifier, ensuring it belongs to the user."""
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return db_portfolio


def list_portfolios(db: Session, user_id: int) -> List[Portfolio]:
    """Return a list of all portfolios for a specific user."""
    db_portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    return db_portfolios


def update_portfolio(
    db: Session,
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    user_id: int,
) -> Portfolio:
    """Update an existing portfolio record, ensuring it belongs to the user."""
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    update_data = portfolio.model_dump(exclude_unset=True, exclude_none=True)
    # Don't allow changing user_id
    update_data.pop('user_id', None)
    for field, value in update_data.items():
        setattr(db_portfolio, field, value)
    try:
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def delete_portfolio(db: Session, portfolio_id: int, user_id: int) -> None:
    """Delete a portfolio record from the database, ensuring it belongs to the user."""
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    try:
        db.delete(db_portfolio)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def create_transaction(
    db: Session,
    transaction: TransactionCreate,
    user_id: int,
) -> Transaction:
    """Create a new transaction record, ensuring the portfolio belongs to the user."""
    # Verify portfolio belongs to user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == transaction.portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db_transaction = Transaction(portfolio_id=transaction.portfolio_id, ticker_symbol=transaction.ticker_symbol, transaction_type=transaction.transaction_type, quantity=transaction.quantity, price=transaction.price)
    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_transaction(db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
    """Retrieve a transaction by its primary identifier, ensuring it belongs to the user's portfolio."""
    db_transaction = db.query(Transaction).join(Portfolio).filter(
        Transaction.id == transaction_id,
        Portfolio.user_id == user_id
    ).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


def list_transactions(db: Session, user_id: int) -> List[Transaction]:
    """Return all transactions for portfolios belonging to the user."""
    db_transactions = db.query(Transaction).join(Portfolio).filter(
        Portfolio.user_id == user_id
    ).all()
    return db_transactions


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction: TransactionUpdate,
    user_id: int,
) -> Transaction:
    """Update an existing transaction record, ensuring it belongs to the user's portfolio."""
    db_transaction = db.query(Transaction).join(Portfolio).filter(
        Transaction.id == transaction_id,
        Portfolio.user_id == user_id
    ).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # If portfolio_id is being updated, verify new portfolio belongs to user
    update_data = transaction.model_dump(exclude_unset=True, exclude_none=True)
    if 'portfolio_id' in update_data:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == update_data['portfolio_id'],
            Portfolio.user_id == user_id
        ).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
    
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    try:
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> None:
    """Delete a transaction record from the database, ensuring it belongs to the user's portfolio."""
    db_transaction = db.query(Transaction).join(Portfolio).filter(
        Transaction.id == transaction_id,
        Portfolio.user_id == user_id
    ).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        db.delete(db_transaction)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user record with hashed password."""
    logger.info(f"Creating user: {user.username}")
    
    # Check for duplicate username
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        logger.warning(f"Attempt to create user with duplicate username: {user.username}")
        raise ConflictError("Username already registered", "USERNAME_EXISTS")
    
    # Check for duplicate email
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        logger.warning(f"Attempt to create user with duplicate email: {user.email}")
        raise ConflictError("Email already registered", "EMAIL_EXISTS")
    
    # Hash the password before storing
    hashed_password_str = hash_password(user.password)
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password_str,
        disabled=False,  # New users are enabled by default
        created_at=datetime.now()
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created successfully: {user.username} (ID: {db_user.id})")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user {user.username}: {str(e)}", exc_info=True)
        raise DatabaseError(f"Failed to create user: {str(e)}")


def get_user(db: Session, username: str) -> User:
    """Retrieve a user by username."""
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Retrieve a user by its primary identifier (ID)."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def list_users(db: Session) -> List[User]:
    """Return a list of all users."""
    db_users = db.query(User).all()
    return db_users

