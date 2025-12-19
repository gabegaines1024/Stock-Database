"""Tests for transaction service functions."""
import pytest  # type: ignore
from sqlalchemy.orm import Session

from app.services.transaction_service import get_current_position
from app.models.model import Transaction, Portfolio, Stock, User


class TestGetCurrentPosition:
    """Test cases for get_current_position function."""
    
    def test_empty_position(self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock):
        """Test position calculation when no transactions exist."""
        position = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker=test_stock.ticker_symbol,
            db=db_session
        )
        assert position == 0
    
    def test_single_buy_transaction(self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock):
        """Test position calculation with a single buy transaction."""
        transaction = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=10.0,
            price=150.0,
        )
        db_session.add(transaction)
        db_session.commit()
        
        position = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker=test_stock.ticker_symbol,
            db=db_session
        )
        assert position == 10
    
    def test_multiple_buy_transactions(self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock):
        """Test position calculation with multiple buy transactions."""
        # Add multiple buy transactions
        for quantity in [10.0, 5.0, 15.0]:
            transaction = Transaction(
                portfolio_id=test_portfolio.id,
                ticker_symbol=test_stock.ticker_symbol,
                transaction_type="buy",
                quantity=quantity,
                price=150.0,
            )
            db_session.add(transaction)
        db_session.commit()
        
        position = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker=test_stock.ticker_symbol,
            db=db_session
        )
        assert position == 30  # 10 + 5 + 15
    
    def test_buy_and_sell_transactions(self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock):
        """Test position calculation with both buy and sell transactions."""
        # Add buy transactions
        buy1 = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=20.0,
            price=150.0,
        )
        buy2 = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=10.0,
            price=160.0,
        )
        # Add sell transaction
        sell1 = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="sell",
            quantity=5.0,
            price=170.0,
        )
        db_session.add_all([buy1, buy2, sell1])
        db_session.commit()
        
        position = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker=test_stock.ticker_symbol,
            db=db_session
        )
        assert position == 25  # (20 + 10) - 5
    
    def test_all_sold_position(self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock):
        """Test position calculation when all shares are sold."""
        # Buy 10 shares
        buy = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=10.0,
            price=150.0,
        )
        # Sell 10 shares
        sell = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="sell",
            quantity=10.0,
            price=170.0,
        )
        db_session.add_all([buy, sell])
        db_session.commit()
        
        position = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker=test_stock.ticker_symbol,
            db=db_session
        )
        assert position == 0
    
    def test_ticker_case_insensitive(self, db_session: Session, test_portfolio: Portfolio, test_stock: Stock):
        """Test that ticker symbol matching is case-insensitive."""
        transaction = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol="AAPL",  # Uppercase
            transaction_type="buy",
            quantity=10.0,
            price=150.0,
        )
        db_session.add(transaction)
        db_session.commit()
        
        # Query with lowercase
        position = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker="aapl",  # Lowercase
            db=db_session
        )
        assert position == 10
    
    def test_different_portfolios_isolated(
        self, db_session: Session, test_user: User, test_stock: Stock
    ):
        """Test that positions are calculated per portfolio."""
        # Create two portfolios
        portfolio1 = Portfolio(name="Portfolio 1", user_id=test_user.id)
        portfolio2 = Portfolio(name="Portfolio 2", user_id=test_user.id)
        db_session.add_all([portfolio1, portfolio2])
        db_session.commit()
        
        # Add transactions to portfolio1
        transaction1 = Transaction(
            portfolio_id=portfolio1.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=10.0,
            price=150.0,
        )
        # Add transactions to portfolio2
        transaction2 = Transaction(
            portfolio_id=portfolio2.id,
            ticker_symbol=test_stock.ticker_symbol,
            transaction_type="buy",
            quantity=5.0,
            price=150.0,
        )
        db_session.add_all([transaction1, transaction2])
        db_session.commit()
        
        # Check positions are isolated
        position1 = get_current_position(
            portfolio_id=portfolio1.id,
            ticker=test_stock.ticker_symbol,
            db=db_session
        )
        position2 = get_current_position(
            portfolio_id=portfolio2.id,
            ticker=test_stock.ticker_symbol,
            db=db_session
        )
        
        assert position1 == 10
        assert position2 == 5
    
    def test_different_tickers_isolated(
        self, db_session: Session, test_portfolio: Portfolio
    ):
        """Test that positions are calculated per ticker symbol."""
        # Create two stocks
        stock1 = Stock(ticker_symbol="AAPL", company_name="Apple Inc.", sector="Technology")
        stock2 = Stock(ticker_symbol="MSFT", company_name="Microsoft Corp.", sector="Technology")
        db_session.add_all([stock1, stock2])
        db_session.commit()
        
        # Add transactions for different tickers
        transaction1 = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol="AAPL",
            transaction_type="buy",
            quantity=10.0,
            price=150.0,
        )
        transaction2 = Transaction(
            portfolio_id=test_portfolio.id,
            ticker_symbol="MSFT",
            transaction_type="buy",
            quantity=5.0,
            price=300.0,
        )
        db_session.add_all([transaction1, transaction2])
        db_session.commit()
        
        # Check positions are isolated
        position_aapl = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker="AAPL",
            db=db_session
        )
        position_msft = get_current_position(
            portfolio_id=test_portfolio.id,
            ticker="MSFT",
            db=db_session
        )
        
        assert position_aapl == 10
        assert position_msft == 5

