from app.schemas.schemas import StockCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import StockBase, Stock, StockUpdate
from app.crud import create_stock, get_stock, update_stock, delete_stock, list_stocks
from typing import List
router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.post("/", response_model=Stock)
def create_stock_route(stock: StockBase, db: Session = Depends(get_db)) -> Stock:
    """Create a new stock."""
    try:
        new_stock = create_stock(db, stock)
        return new_stock
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{stock_id}", response_model=Stock)
def get_stock_route(stock_id: int, db: Session = Depends(get_db)) -> Stock:
    """Get a stock by its primary identifier."""
    try:
        return get_stock(db, stock_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Stock])
def list_stocks_route(db: Session = Depends(get_db)) -> list[Stock]:
    """List all stocks."""
    try:
        return list_stocks(db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{stock_id}", response_model=Stock)
def update_stock_route(stock_id: int, stock: StockUpdate, db: Session = Depends(get_db)) -> Stock:
    """Update a stock by its primary identifier."""
    try:
        return update_stock(db, stock_id, stock)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{stock_id}", response_model=Stock)
def delete_stock_route(stock_id: int, db: Session = Depends(get_db)) -> Stock:
    """Delete a stock by its primary identifier."""
    try:
        stock = get_stock(db, stock_id)
        delete_stock(db, stock_id)
        return stock
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))