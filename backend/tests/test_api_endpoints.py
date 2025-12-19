"""Integration tests for API endpoints."""
import pytest  # type: ignore
from fastapi.testclient import TestClient

from app.models.model import Transaction


class TestTransactionEndpoints:
    """Test transaction API endpoints."""
    
    def test_create_transaction_buy(
        self, client: TestClient, auth_headers: dict, test_portfolio, test_stock
    ):
        """Test creating a buy transaction."""
        response = client.post(
            "/transactions/",
            json={
                "portfolio_id": test_portfolio.id,
                "ticker_symbol": test_stock.ticker_symbol,
                "transaction_type": "buy",
                "quantity": 10.0,
                "price": 150.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_type"] == "buy"
        assert data["quantity"] == 10.0
        assert data["price"] == 150.0
    
    def test_create_transaction_sell_success(
        self, client: TestClient, auth_headers: dict, test_portfolio, test_stock, test_transaction_buy
    ):
        """Test creating a sell transaction when sufficient holdings exist."""
        response = client.post(
            "/transactions/",
            json={
                "portfolio_id": test_portfolio.id,
                "ticker_symbol": test_stock.ticker_symbol,
                "transaction_type": "sell",
                "quantity": 5.0,
                "price": 170.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_type"] == "sell"
        assert data["quantity"] == 5.0
    
    def test_create_transaction_sell_insufficient_holdings(
        self, client: TestClient, auth_headers: dict, test_portfolio, test_stock
    ):
        """Test creating a sell transaction when insufficient holdings exist."""
        response = client.post(
            "/transactions/",
            json={
                "portfolio_id": test_portfolio.id,
                "ticker_symbol": test_stock.ticker_symbol,
                "transaction_type": "sell",
                "quantity": 10.0,
                "price": 170.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()
    
    def test_get_transaction(
        self, client: TestClient, auth_headers: dict, test_transaction_buy
    ):
        """Test retrieving a transaction."""
        response = client.get(
            f"/transactions/{test_transaction_buy.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_transaction_buy.id
    
    def test_list_transactions(
        self, client: TestClient, auth_headers: dict, test_transaction_buy
    ):
        """Test listing transactions."""
        response = client.get("/transactions/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_position(
        self, client: TestClient, auth_headers: dict, test_portfolio, test_stock, test_transaction_buy
    ):
        """Test getting current position."""
        response = client.get(
            f"/transactions/position/{test_portfolio.id}/{test_stock.ticker_symbol}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "position" in data
        assert data["ticker"] == test_stock.ticker_symbol.upper()
        assert data["position"] == 10  # From test_transaction_buy fixture
    
    def test_update_transaction(
        self, client: TestClient, auth_headers: dict, test_transaction_buy
    ):
        """Test updating a transaction."""
        response = client.put(
            f"/transactions/{test_transaction_buy.id}",
            json={
                "quantity": 15.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 15.0
    
    def test_delete_transaction(
        self, client: TestClient, auth_headers: dict, test_transaction_buy
    ):
        """Test deleting a transaction."""
        transaction_id = test_transaction_buy.id
        response = client.delete(
            f"/transactions/{transaction_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(
            f"/transactions/{transaction_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    def test_create_transaction_unauthorized(self, client: TestClient, test_portfolio, test_stock):
        """Test creating a transaction without authentication."""
        response = client.post(
            "/transactions/",
            json={
                "portfolio_id": test_portfolio.id,
                "ticker_symbol": test_stock.ticker_symbol,
                "transaction_type": "buy",
                "quantity": 10.0,
                "price": 150.0,
            },
        )
        assert response.status_code == 401


class TestPortfolioEndpoints:
    """Test portfolio API endpoints."""
    
    def test_create_portfolio(self, client: TestClient, auth_headers: dict):
        """Test creating a portfolio."""
        response = client.post(
            "/portfolios/",
            json={"name": "New Portfolio"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Portfolio"
        assert "id" in data
    
    def test_list_portfolios(self, client: TestClient, auth_headers: dict, test_portfolio):
        """Test listing portfolios."""
        response = client.get("/portfolios/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_portfolio(self, client: TestClient, auth_headers: dict, test_portfolio):
        """Test retrieving a portfolio."""
        response = client.get(
            f"/portfolios/{test_portfolio.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_portfolio.id
        assert data["name"] == test_portfolio.name
    
    def test_update_portfolio(self, client: TestClient, auth_headers: dict, test_portfolio):
        """Test updating a portfolio."""
        response = client.put(
            f"/portfolios/{test_portfolio.id}",
            json={"name": "Updated Portfolio"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Portfolio"
    
    def test_delete_portfolio(self, client: TestClient, auth_headers: dict, test_portfolio):
        """Test deleting a portfolio."""
        portfolio_id = test_portfolio.id
        response = client.delete(
            f"/portfolios/{portfolio_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(
            f"/portfolios/{portfolio_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestStockEndpoints:
    """Test stock API endpoints."""
    
    def test_create_stock(self, client: TestClient, auth_headers: dict):
        """Test creating a stock."""
        response = client.post(
            "/stocks/",
            json={
                "ticker_symbol": "TSLA",
                "company_name": "Tesla Inc.",
                "sector": "Automotive",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ticker_symbol"] == "TSLA"
        assert data["company_name"] == "Tesla Inc."
    
    def test_list_stocks(self, client: TestClient, auth_headers: dict, test_stock):
        """Test listing stocks."""
        response = client.get("/stocks/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_stock(self, client: TestClient, auth_headers: dict, test_stock):
        """Test retrieving a stock."""
        response = client.get(
            f"/stocks/{test_stock.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_stock.id
        assert data["ticker_symbol"] == test_stock.ticker_symbol

