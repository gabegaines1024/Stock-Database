from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import ForeignKey, String


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""


class User(Base):
    """Represents a user of the application."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    
    # Relationships - one user can have many portfolios
    portfolios: Mapped[list["Portfolio"]] = relationship(back_populates="user")


class Stock(Base):
    """Represents a stock instrument tracked by the application."""

    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker_symbol: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(255))

    # One stock can appear in many transactions
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="stock")


class Portfolio(Base):
    """Represents a user-managed portfolio of stock positions."""

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)  # ← Add ForeignKey!
    name: Mapped[str] = mapped_column(String(255), default="My Portfolio")
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="portfolios")  # ← Add this!
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="portfolio")


class Transaction(Base):
    """Represents a buy or sell transaction for a portfolio position."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"), index=True)
    ticker_symbol: Mapped[str] = mapped_column(ForeignKey("stocks.ticker_symbol"), String(10), index=True)  # Fixed: "stocks" not "stock"
    transaction_type: Mapped[str] = mapped_column(String(10))  # "buy" or "sell"
    quantity: Mapped[float] = mapped_column(default=0.0, nullable=False)
    price: Mapped[float] = mapped_column(default=0.0, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(back_populates="transactions")
    stock: Mapped["Stock"] = relationship(back_populates="transactions")  # Fixed: back_populates should be "transactions" not "portfolio"