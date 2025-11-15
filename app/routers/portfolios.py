from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from app.schemas import PortfolioBase, Portfolio, PortfolioUpdate
from app.crud import create_portfolio, get_portfolio, update_portfolio, delete_portfolio, list_portfolios
from typing import List

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

@router.post("/", response_model=Portfolio)
def create_portfolio_route(portfolio: PortfolioBase, db: Session = Depends(get_db)) -> Portfolio:
    """Create a new portfolio."""
    try:
        return create_portfolio(db, portfolio)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{portfolio_id}", response_model=Portfolio)
def get_portfolio_route(portfolio_id: int, db: Session = Depends(get_db)) -> Portfolio:
    """Get a portfolio by its primary identifier."""
    try:
        return get_portfolio(db, portfolio_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[Portfolio])
def list_portfolios_route(db: Session = Depends(get_db)) -> list[Portfolio]:
    """List all portfolios."""
    try:
        return list_portfolios(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio_route(portfolio_id: int, portfolio: PortfolioUpdate, db: Session = Depends(get_db)) -> Portfolio:
    """Update a portfolio by its primary identifier."""
    try:
        update_portfolio(db, portfolio_id, portfolio)
        return get_portfolio(db, portfolio_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{portfolio_id}", response_model=Portfolio)
def delete_portfolio_route(portfolio_id: int, db: Session = Depends(get_db)) -> Portfolio:
    """Delete a portfolio by its primary identifier."""
    try:
        portfolio = get_portfolio(db, portfolio_id)
        delete_portfolio(db, portfolio_id)
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))