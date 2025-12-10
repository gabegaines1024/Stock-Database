"""Service layer functions for transaction-related business logic."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.model import Transaction


def get_current_position(portfolio_id: int, ticker: str, db: Session) -> int:
    """
    Calculate the current position (net quantity) for a given portfolio and ticker.
    
    Sums all BUY transaction quantities and subtracts all SELL transaction quantities.
    
    Args:
        portfolio_id: The portfolio ID to query
        ticker: The ticker symbol to query
        db: Database session
        
    Returns:
        The net integer quantity (current position)
    """
    # Normalize ticker to uppercase for consistency
    ticker_upper = ticker.upper()
    
    # Sum all BUY transactions
    buy_total = db.query(func.sum(Transaction.quantity)).filter(
        Transaction.portfolio_id == portfolio_id,
        Transaction.ticker_symbol == ticker_upper,
        Transaction.transaction_type == "buy"
    ).scalar() or 0.0
    
    # Sum all SELL transactions
    sell_total = db.query(func.sum(Transaction.quantity)).filter(
        Transaction.portfolio_id == portfolio_id,
        Transaction.ticker_symbol == ticker_upper,
        Transaction.transaction_type == "sell"
    ).scalar() or 0.0
    
    # Calculate net position and convert to integer
    net_position = buy_total - sell_total
    return int(net_position)
