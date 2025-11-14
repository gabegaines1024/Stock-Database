from fastapi import HTTPException
from collections.abc import Iterable
from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas


def create_stock(db: Session, stock: schemas.StockCreate) -> models.Stock:
    """Create a new stock record in the database."""
    db_stock = models.Stock(ticker_symbol=stock.ticker_symbol, company_name=stock.company_name, sector=stock.sector)
    try:
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        return db_stock
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_stock(db: Session, stock_id: int) -> Optional[models.Stock]:
    """Retrieve a stock by its primary identifier."""
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock

def get_stock_by_ticker(db: Session, ticker: str) -> Optional[models.Stock]:
    """Retrieve a stock by its ticker symbol."""
    db_stock = db.query(models.Stock).filter(models.Stock.ticker_symbol == ticker).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock


def list_stocks(db: Session) -> Iterable[models.Stock]:
    """Return an iterable of all stored stocks."""
    db_stocks = db.query(models.Stock).all()
    return db_stocks


def update_stock(db: Session, stock_id: int, stock: schemas.StockUpdate) -> models.Stock:
    """Update an existing stock record."""
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    update_data = db_stock.model_dump(exclude_unset=True)
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
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    try:
        db.delete(db_stock)
        db.commit()
        return {"message": "stock deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def create_portfolio(db: Session, portfolio: schemas.PortfolioCreate) -> models.Portfolio:
    """Create a new portfolio record."""
    db_portfolio = models.Portfolio(name=portfolio.name, user_id=portfolio.user_id)
    try:
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_portfolio(db: Session, portfolio_id: int) -> Optional[models.Portfolio]:
    """Retrieve a portfolio by its primary identifier."""
    db_portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return db_portfolio


def list_portfolios(db: Session) -> Iterable[models.Portfolio]:
    """Return an iterable of all stored portfolios."""
    db_portfolios = db.query(models.Portfolio).all()
    return db_portfolios


def update_portfolio(
    db: Session,
    portfolio_id: int,
    portfolio: schemas.PortfolioUpdate,
) -> models.Portfolio:
    """Update an existing portfolio record."""
    db_portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    update_data = db_portfolio.model_dump(exclude_unset=True)
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
    db_portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
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
    transaction: schemas.TransactionCreate,
) -> models.Transaction:
    """Create a new transaction record."""
    db_transaction = models.Transaction(portfolio_id=transaction.portfolio_id, ticker_symbol=transaction.ticker_symbol, transaction_type=transaction.transaction_type, quantity=transaction.quantity, price=transaction.price)
    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    """Retrieve a transaction by its primary identifier."""
    # TODO: Implement retrieval logic
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


def list_transactions(db: Session) -> Iterable[models.Transaction]:
    """Return an iterable of all stored transactions."""
    db_transactions = db.query(models.Transaction).all()
    return db_transactions


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction: schemas.TransactionUpdate,
) -> models.Transaction:
    """Update an existing transaction record."""
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = db_transaction.model_dump(exclude_unset=True)
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
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        db.delete(db_transaction)
        db.commit()
        return {"message": "transaction deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
