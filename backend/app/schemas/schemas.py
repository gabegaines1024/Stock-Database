from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============== STOCK SCHEMAS ==============
class StockBase(BaseModel):
    """Shared fields for all stock operations."""
    ticker_symbol: str = Field(..., min_length=1, max_length=10)
    company_name: str = Field(..., min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)


class StockCreate(StockBase):
    """For creating stocks - inherits all from Base."""
    pass


class StockUpdate(BaseModel):
    """For partial updates - all optional, doesn't inherit from Base."""
    ticker_symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)


class Stock(StockBase):
    """API response - inherits base fields + adds id."""
    id: int
    
    class Config:
        from_attributes = True


# ============== PORTFOLIO SCHEMAS ==============
class PortfolioBase(BaseModel):
    """Shared fields for all portfolio operations."""
    name: str = Field(..., min_length=1, max_length=100)


class PortfolioCreate(PortfolioBase):
    """For creating portfolios - user_id comes from authenticated user."""
    pass


class PortfolioUpdate(BaseModel):
    """For partial updates - all optional, doesn't inherit from Base."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    user_id: Optional[int] = Field(None, gt=0)


class Portfolio(PortfolioBase):
    """API response - inherits base fields + adds id, user_id and timestamp."""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== TRANSACTION SCHEMAS ==============
class TransactionBase(BaseModel):
    """Shared fields for all transaction operations."""
    portfolio_id: int = Field(..., gt=0)
    ticker_symbol: str = Field(..., min_length=1, max_length=10)
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)


class TransactionCreate(TransactionBase):
    """For creating transactions - inherits all from Base, executed_at set by DB."""
    pass


class TransactionUpdate(BaseModel):
    """For partial updates - all optional, doesn't inherit from Base."""
    portfolio_id: Optional[int] = Field(None, gt=0)
    ticker_symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    transaction_type: Optional[str] = Field(None, pattern="^(buy|sell)$")
    quantity: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)


class Transaction(TransactionBase):
    """API response - inherits base fields + adds id and timestamp."""
    id: int
    executed_at: datetime
    
    class Config:
        from_attributes = True


# ============== USER SCHEMAS ==============
class UserBase(BaseModel):
    """Shared fields for all user operations."""
    email: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., min_length=1, max_length=255)


class UserCreate(BaseModel):
    """For creating users - includes password field."""
    email: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """For partial updates - all optional, doesn't inherit from Base."""
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

class UserLogin(BaseModel):
    username: str = Field(..., min_length =  1, max_length = 100)
    password: str = Field(..., min_length = 8, max_length = 100)


class User(UserBase):
    """API response - inherits base fields + adds id and timestamp."""
    id: int
    disabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Token response schema for authentication."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data schema."""
    username: Optional[str] = None


# ============== PORTFOLIO ANALYTICS SCHEMAS ==============
class StockPosition(BaseModel):
    """Position details for a single stock in a portfolio."""
    ticker: str
    quantity: float
    average_cost: float
    current_price: float
    current_value: float
    cost_basis: float
    gain_loss: float
    gain_loss_percentage: float


class PortfolioValue(BaseModel):
    """Portfolio value and performance metrics."""
    total_value: float
    total_cost: float
    total_gain_loss: float
    gain_loss_percentage: float


class PortfolioAnalytics(BaseModel):
    """Complete portfolio analytics including value and positions."""
    portfolio_id: int
    portfolio_name: str
    value: PortfolioValue
    positions: list[StockPosition]