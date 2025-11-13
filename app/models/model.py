from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import ForeignKey, String


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""


class Stock(Base):
    """Represents a stock instrument tracked by the application."""

    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker_symbol: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(255))

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="portfolio")


class Portfolio(Base):
    """Represents a user-managed portfolio of stock positions."""

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(255), default="My Portfolio")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="portfolio")


class Transaction(Base):
    """Represents a buy or sell transaction for a portfolio position."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"), index=True) #connects to the portfolio table
    ticker_symbol: Mapped[str] = mapped_column(ForeignKey("stock.ticker_symbol"), String(10), index=True) #connects to the stock table
    transaction_type: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[float] = mapped_column(default=0.0, nullable=False)
    price: Mapped[float] = mapped_column(default=0.0, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)

    portfolio: Mapped["Portfolio"] = relationship(back_populates="transactions") #one to many relationship with the portfolio table --> one portfolio can have many transactions
    stock: Mapped["Stock"] = relationship(back_populates="transactions") #one to many relationship with the stock table --> one stock can have many transactions