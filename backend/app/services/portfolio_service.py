"""Service layer functions for portfolio analytics and performance calculations."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
from app.models.model import Transaction, Portfolio
from app.api_client.api_client import StockAPIClient


class PortfolioAnalytics:
    """Calculate portfolio analytics and performance metrics."""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_client = StockAPIClient()
    
    def get_portfolio_positions(self, portfolio_id: int) -> Dict[str, Dict]:
        """
        Get all positions in a portfolio with their quantities and cost basis.
        
        Returns:
            Dict mapping ticker symbols to position data:
            {
                "AAPL": {
                    "quantity": 10.0,
                    "total_cost": 1500.0,
                    "average_cost": 150.0
                },
                ...
            }
        """
        positions: Dict[str, Dict] = {}
        
        # Get all transactions for this portfolio
        transactions = self.db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id
        ).all()
        
        for transaction in transactions:
            ticker = transaction.ticker_symbol.upper()
            
            if ticker not in positions:
                positions[ticker] = {
                    "quantity": 0.0,
                    "total_cost": 0.0,
                    "average_cost": 0.0,
                }
            
            if transaction.transaction_type.lower() == "buy":
                # Add to position
                current_cost = positions[ticker]["total_cost"]
                current_quantity = positions[ticker]["quantity"]
                new_cost = transaction.quantity * transaction.price
                
                positions[ticker]["quantity"] += transaction.quantity
                positions[ticker]["total_cost"] += new_cost
                
                # Recalculate average cost
                if positions[ticker]["quantity"] > 0:
                    positions[ticker]["average_cost"] = (
                        positions[ticker]["total_cost"] / positions[ticker]["quantity"]
                    )
            
            elif transaction.transaction_type.lower() == "sell":
                # Reduce position using FIFO cost basis
                # For simplicity, we'll use average cost method
                positions[ticker]["quantity"] -= transaction.quantity
                
                # Reduce total cost proportionally
                if positions[ticker]["quantity"] > 0:
                    # Adjust total cost based on remaining quantity
                    avg_cost = positions[ticker]["average_cost"]
                    positions[ticker]["total_cost"] = (
                        positions[ticker]["quantity"] * avg_cost
                    )
                else:
                    # Position fully sold
                    positions[ticker]["total_cost"] = 0.0
                    positions[ticker]["average_cost"] = 0.0
        
        # Remove positions with zero quantity
        return {ticker: data for ticker, data in positions.items() if data["quantity"] > 0}
    
    def get_portfolio_value(
        self, 
        portfolio_id: int, 
        current_prices: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Calculate portfolio value using current stock prices.
        
        Args:
            portfolio_id: The portfolio ID
            current_prices: Optional dict of ticker -> current price (for caching)
            
        Returns:
            Dict with:
            - "total_value": Total current portfolio value
            - "total_cost": Total cost basis
            - "total_gain_loss": Total gain/loss amount
            - "gain_loss_percentage": Gain/loss percentage
        """
        positions = self.get_portfolio_positions(portfolio_id)
        
        if not positions:
            return {
                "total_value": 0.0,
                "total_cost": 0.0,
                "total_gain_loss": 0.0,
                "gain_loss_percentage": 0.0,
            }
        
        total_value = 0.0
        total_cost = 0.0
        
        # Use provided prices or fetch from API
        if current_prices is None:
            current_prices = {}
        
        for ticker, position_data in positions.items():
            quantity = position_data["quantity"]
            cost_basis = position_data["total_cost"]
            
            # Get current price
            if ticker in current_prices:
                current_price = current_prices[ticker]
            else:
                try:
                    current_price = self.api_client.get_current_price(ticker)
                    current_prices[ticker] = current_price
                except Exception:
                    # If price fetch fails, use average cost as fallback
                    current_price = position_data["average_cost"]
            
            current_value = quantity * current_price
            total_value += current_value
            total_cost += cost_basis
        
        total_gain_loss = total_value - total_cost
        gain_loss_percentage = (
            (total_gain_loss / total_cost * 100) if total_cost > 0 else 0.0
        )
        
        return {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_gain_loss": round(total_gain_loss, 2),
            "gain_loss_percentage": round(gain_loss_percentage, 2),
        }
    
    def get_stock_positions(
        self, 
        portfolio_id: int, 
        current_prices: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Get detailed position information for each stock in the portfolio.
        
        Returns:
            List of dicts with position details:
            [
                {
                    "ticker": "AAPL",
                    "quantity": 10.0,
                    "average_cost": 150.0,
                    "current_price": 155.0,
                    "current_value": 1550.0,
                    "cost_basis": 1500.0,
                    "gain_loss": 50.0,
                    "gain_loss_percentage": 3.33
                },
                ...
            ]
        """
        positions = self.get_portfolio_positions(portfolio_id)
        
        if not positions:
            return []
        
        # Use provided prices or fetch from API
        if current_prices is None:
            current_prices = {}
        
        stock_positions = []
        
        for ticker, position_data in positions.items():
            quantity = position_data["quantity"]
            average_cost = position_data["average_cost"]
            cost_basis = position_data["total_cost"]
            
            # Get current price
            if ticker in current_prices:
                current_price = current_prices[ticker]
            else:
                try:
                    current_price = self.api_client.get_current_price(ticker)
                    current_prices[ticker] = current_price
                except Exception:
                    # If price fetch fails, use average cost as fallback
                    current_price = average_cost
            
            current_value = quantity * current_price
            gain_loss = current_value - cost_basis
            gain_loss_percentage = (
                (gain_loss / cost_basis * 100) if cost_basis > 0 else 0.0
            )
            
            stock_positions.append({
                "ticker": ticker,
                "quantity": round(quantity, 2),
                "average_cost": round(average_cost, 2),
                "current_price": round(current_price, 2),
                "current_value": round(current_value, 2),
                "cost_basis": round(cost_basis, 2),
                "gain_loss": round(gain_loss, 2),
                "gain_loss_percentage": round(gain_loss_percentage, 2),
            })
        
        # Sort by current value (descending)
        stock_positions.sort(key=lambda x: x["current_value"], reverse=True)
        
        return stock_positions

