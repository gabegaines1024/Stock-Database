from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============== STOCK SCHEMAS ==============
class StockBase(BaseModel):
    ticker_symbol: str = Field(..., min_length=1, max_length=10)
    company_name: str = Field(..., min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)  # Can be None, no default


class StockCreate(StockBase):
    """Inherits all fields from StockBase - nothing to add."""
    pass


class StockUpdate(BaseModel):
    """All fields optional for partial updates."""
    ticker_symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)


class Stock(StockBase):
    """API response includes id."""
    id: int
    
    class Config:
        from_attributes = True


# ============== PORTFOLIO SCHEMAS ==============
class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    user_id: int = Field(..., gt=0)


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    user_id: Optional[int] = Field(None, gt=0)


class Portfolio(PortfolioBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== TRANSACTION SCHEMAS ==============
class TransactionBase(BaseModel):
    """Shared fields for transaction responses."""
    portfolio_id: int = Field(..., gt=0)
    ticker_symbol: str = Field(..., min_length=1, max_length=10)
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)


class TransactionCreate(BaseModel):
    """For creating transactions - no id, no executed_at."""
    portfolio_id: int = Field(..., gt=0)
    ticker_symbol: str = Field(..., min_length=1, max_length=10)
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    # executed_at will be set by database automatically


class TransactionUpdate(BaseModel):
    """For partial updates - all optional."""
    portfolio_id: Optional[int] = Field(None, gt=0)
    ticker_symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    transaction_type: Optional[str] = Field(None, pattern="^(buy|sell)$")
    quantity: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)


class Transaction(TransactionBase):
    """API response includes id and timestamp."""
    id: int
    executed_at: datetime
    
    class Config:
        from_attributes = True