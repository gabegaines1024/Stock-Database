from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import cast
from app.database import get_db
from app.dependencies import get_current_user
from app.models.model import User
from app.schemas import PortfolioBase, Portfolio, PortfolioCreate, PortfolioUpdate
from app.crud import create_portfolio, get_portfolio, update_portfolio, delete_portfolio, list_portfolios
from typing import List

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

@router.post("/", response_model=Portfolio)
def create_portfolio_route(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Portfolio:
    """Create a new portfolio for the authenticated user."""
    try:
        return cast(Portfolio, create_portfolio(db, portfolio, current_user.id))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{portfolio_id}", response_model=Portfolio)
def get_portfolio_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Portfolio:
    """Get a portfolio by its primary identifier (must belong to authenticated user)."""
    try:
        return cast(Portfolio, get_portfolio(db, portfolio_id, current_user.id))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[Portfolio])
def list_portfolios_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[Portfolio]:
    """List all portfolios for the authenticated user."""
    try:
        return cast(list[Portfolio], list_portfolios(db, current_user.id))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio_route(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Portfolio:
    """Update a portfolio by its primary identifier (must belong to authenticated user)."""
    try:
        update_portfolio(db, portfolio_id, portfolio, current_user.id)
        return cast(Portfolio, get_portfolio(db, portfolio_id, current_user.id))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{portfolio_id}", response_model=Portfolio)
def delete_portfolio_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Portfolio:
    """Delete a portfolio by its primary identifier (must belong to authenticated user)."""
    try:
        portfolio = get_portfolio(db, portfolio_id, current_user.id)
        delete_portfolio(db, portfolio_id, current_user.id)
        return cast(Portfolio, portfolio)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))