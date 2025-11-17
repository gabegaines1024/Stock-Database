from datetime import datetime
from fastapi import HTTPException
from collections.abc import Iterable
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models import User, Stock, Portfolio, Transaction
from app.schemas import StockCreate, StockUpdate, PortfolioCreate, PortfolioUpdate, TransactionCreate, TransactionUpdate, UserCreate, UserUpdate
from app.security import hash_password


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
        return {"message": "stock deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def create_portfolio(db: Session, portfolio: PortfolioCreate) -> Portfolio:
    """Create a new portfolio record."""
    db_portfolio = Portfolio(name=portfolio.name, user_id=portfolio.user_id)
    try:
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_portfolio(db: Session, portfolio_id: int) -> Optional[Portfolio]:
    """Retrieve a portfolio by its primary identifier."""
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return db_portfolio


def list_portfolios(db: Session) -> Iterable[Portfolio]:
    """Return an iterable of all stored portfolios."""
    db_portfolios = db.query(Portfolio).all()
    return db_portfolios


def update_portfolio(
    db: Session,
    portfolio_id: int,
    portfolio: PortfolioUpdate,
) -> Portfolio:
    """Update an existing portfolio record."""
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    update_data = portfolio.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_portfolio, field, value)
    try:
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def delete_portfolio(db: Session, portfolio_id: int) -> None:
    """Delete a portfolio record from the database."""
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    try:
        db.delete(db_portfolio)
        db.commit()
        return {"message": "portfolio deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def create_transaction(
    db: Session,
    transaction: TransactionCreate,
) -> Transaction:
    """Create a new transaction record."""
    db_transaction = Transaction(portfolio_id=transaction.portfolio_id, ticker_symbol=transaction.ticker_symbol, transaction_type=transaction.transaction_type, quantity=transaction.quantity, price=transaction.price)
    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Retrieve a transaction by its primary identifier."""
    # TODO: Implement retrieval logic
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


def list_transactions(db: Session) -> List[Transaction]:
    """Return an iterable of all stored transactions."""
    db_transactions = db.query(Transaction).all()
    return db_transactions


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction: TransactionUpdate,
) -> Transaction:
    """Update an existing transaction record."""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = transaction.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    try:
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def delete_transaction(db: Session, transaction_id: int) -> None:
    """Delete a transaction record from the database."""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        db.delete(db_transaction)
        db.commit()
        return {"message": "transaction deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user record with hashed password."""
    # Hash the password before storing
    hashed_password_str = hash_password(user.password)
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password_str,
        created_at=datetime.now()
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_user(db: Session, user_id: int) -> User:
    """Retrieve a user by its primary identifier."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def list_users(db: Session) -> List[User]:
    """Return a list of all users."""
    db_users = db.query(User).all()
    return db_users

