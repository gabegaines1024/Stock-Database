"""Tests for CRUD operations."""
import pytest  # type: ignore
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.model import User, Portfolio, Stock, Transaction
from app.crud import (
    create_portfolio,
    get_portfolio,
    list_portfolios,
    update_portfolio,
    delete_portfolio,
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
    delete_transaction,
    create_stock,
    get_stock,
    list_stocks,
)
from app.schemas.schemas import (
    PortfolioCreate,
    PortfolioUpdate,
    TransactionCreate,
    TransactionUpdate,
    StockCreate,
)


class TestPortfolioCRUD:
    """Test portfolio CRUD operations."""
    
    def test_create_portfolio(self, db_session: Session, test_user: User):
        """Test creating a portfolio."""
        portfolio_data = PortfolioCreate(name="My Portfolio")
        portfolio = create_portfolio(db_session, portfolio_data, test_user.id)
        
        assert portfolio.id is not None
        assert portfolio.name == "My Portfolio"
        assert portfolio.user_id == test_user.id
    
    def test_get_portfolio(self, db_session: Session, test_portfolio: Portfolio, test_user: User):
        """Test retrieving a portfolio."""
        portfolio = get_portfolio(db_session, test_portfolio.id, test_user.id)
        assert portfolio.id == test_portfolio.id
        assert portfolio.name == test_portfolio.name
    
    def test_get_portfolio_wrong_user(self, db_session: Session, test_portfolio: Portfolio, test_user2: User):
        """Test that users cannot access other users' portfolios."""
        with pytest.raises(HTTPException) as exc_info:
            get_portfolio(db_session, test_portfolio.id, test_user2.id)
        assert exc_info.value.status_code == 404
    
    def test_list_portfolios(self, db_session: Session, test_user: User):
        """Test listing portfolios for a user."""
        # Create multiple portfolios
        for i in range(3):
            portfolio_data = PortfolioCreate(name=f"Portfolio {i+1}")
            create_portfolio(db_session, portfolio_data, test_user.id)
        
        portfolios = list_portfolios(db_session, test_user.id)
        assert len(portfolios) == 3
    
    def test_list_portfolios_user_isolation(
        self, db_session: Session, test_user: User, test_user2: User
    ):
        """Test that users only see their own portfolios."""
        # Create portfolios for user1
        portfolio_data1 = PortfolioCreate(name="User1 Portfolio")
        create_portfolio(db_session, portfolio_data1, test_user.id)
        
        # Create portfolios for user2
        portfolio_data2 = PortfolioCreate(name="User2 Portfolio")
        create_portfolio(db_session, portfolio_data2, test_user2.id)
        
        # Check isolation
        user1_portfolios = list_portfolios(db_session, test_user.id)
        user2_portfolios = list_portfolios(db_session, test_user2.id)
        
        assert len(user1_portfolios) == 1
        assert len(user2_portfolios) == 1
        assert user1_portfolios[0].name == "User1 Portfolio"
        assert user2_portfolios[0].name == "User2 Portfolio"
    
    def test_update_portfolio(self, db_session: Session, test_portfolio: Portfolio, test_user: User):
        """Test updating a portfolio."""
        update_data = PortfolioUpdate(name="Updated Portfolio", user_id=None)
        updated = update_portfolio(db_session, test_portfolio.id, update_data, test_user.id)
        
        assert updated.name == "Updated Portfolio"
        assert updated.id == test_portfolio.id
    
    def test_update_portfolio_wrong_user(
        self, db_session: Session, test_portfolio: Portfolio, test_user2: User
    ):
        """Test that users cannot update other users' portfolios."""
        update_data = PortfolioUpdate(name="Hacked Portfolio", user_id=None)
        with pytest.raises(HTTPException) as exc_info:
            update_portfolio(db_session, test_portfolio.id, update_data, test_user2.id)
        assert exc_info.value.status_code == 404
    
    def test_delete_portfolio(self, db_session: Session, test_portfolio: Portfolio, test_user: User):
        """Test deleting a portfolio."""
        portfolio_id = test_portfolio.id
        delete_portfolio(db_session, portfolio_id, test_user.id)
        
        # Verify it's deleted
        with pytest.raises(HTTPException) as exc_info:
            get_portfolio(db_session, portfolio_id, test_user.id)
        assert exc_info.value.status_code == 404


class TestTransactionCRUD:
    """Test transaction CRUD operations."""
    
    def test_create_transaction(
        self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock, test_user: User
    ):
        """Test creating a transaction."""
        transaction_data = TransactionCreate(
            portfolio_id=test_portfolio.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=10.0,
            price=150.0,
        )
        transaction = create_transaction(db_session, transaction_data, test_user.id)
        
        assert transaction.id is not None
        assert transaction.portfolio_id == test_portfolio.id
        assert transaction.ticker_symbol == test_stock.ticker_symbol
        assert transaction.quantity == 10.0
    
    def test_create_transaction_wrong_portfolio(
        self, db_session: Session, test_user: User, test_user2: User, test_stock: Stock
    ):
        """Test that users cannot create transactions for other users' portfolios."""
        # Create a portfolio for user2
        from app.crud import create_portfolio
        from app.schemas.schemas import PortfolioCreate
        
        portfolio2 = create_portfolio(
            db_session, PortfolioCreate(name="User2 Portfolio"), test_user2.id
        )
        
        # Try to create transaction as user1 for user2's portfolio
        transaction_data = TransactionCreate(
            portfolio_id=portfolio2.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=10.0,
            price=150.0,
        )
        
        with pytest.raises(HTTPException) as exc_info:
            create_transaction(db_session, transaction_data, test_user.id)
        assert exc_info.value.status_code == 404
    
    def test_get_transaction(
        self, db_session: Session, test_transaction_buy: Transaction, test_user: User
    ):
        """Test retrieving a transaction."""
        transaction = get_transaction(
            db_session, test_transaction_buy.id, test_user.id
        )
        assert transaction is not None
        assert transaction.id == test_transaction_buy.id
    
    def test_list_transactions(
        self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock, test_user: User
    ):
        """Test listing transactions."""
        # Create multiple transactions
        for i in range(3):
            transaction_data = TransactionCreate(
                portfolio_id=test_portfolio.id,
                ticker_symbol=test_stock.ticker_symbol,
                transaction_type="buy",
                quantity=10.0 + i,
                price=150.0,
            )
            create_transaction(db_session, transaction_data, test_user.id)
        
        transactions = list_transactions(db_session, test_user.id)
        assert len(transactions) >= 3
    
    def test_update_transaction(
        self, db_session: Session, test_transaction_buy: Transaction, test_user: User
    ):
        """Test updating a transaction."""
        # TransactionUpdate allows partial updates - only quantity is required here
        update_data = TransactionUpdate.model_validate({"quantity": 20.0})
        updated = update_transaction(
            db_session, test_transaction_buy.id, update_data, test_user.id
        )
        assert updated is not None
        assert updated.quantity == 20.0
    
    def test_delete_transaction(
        self, db_session: Session, test_transaction_buy: Transaction, test_user: User
    ):
        """Test deleting a transaction."""
        transaction_id = test_transaction_buy.id
        delete_transaction(db_session, transaction_id, test_user.id)
        
        # Verify it's deleted
        with pytest.raises(HTTPException) as exc_info:
            get_transaction(db_session, transaction_id, test_user.id)
        assert exc_info.value.status_code == 404


class TestStockCRUD:
    """Test stock CRUD operations."""
    
    def test_create_stock(self, db_session: Session):
        """Test creating a stock."""
        stock_data = StockCreate(
            ticker_symbol="TSLA",
            company_name="Tesla Inc.",
            sector="Automotive",
        )
        stock = create_stock(db_session, stock_data)
        
        assert stock.id is not None
        assert stock.ticker_symbol == "TSLA"
        assert stock.company_name == "Tesla Inc."
    
    def test_get_stock(self, db_session: Session, test_stock: Stock):
        """Test retrieving a stock."""
        stock = get_stock(db_session, test_stock.id)
        assert stock is not None
        assert stock.id == test_stock.id
        assert stock.ticker_symbol == test_stock.ticker_symbol
    
    def test_list_stocks(self, db_session: Session):
        """Test listing all stocks."""
        # Create multiple stocks
        for ticker in ["AAPL", "MSFT", "GOOGL"]:
            stock_data = StockCreate(
                ticker_symbol=ticker,
                company_name=f"{ticker} Company",
                sector="Technology",
            )
            create_stock(db_session, stock_data)
        
        stocks = list_stocks(db_session)
        assert len(stocks) >= 3

