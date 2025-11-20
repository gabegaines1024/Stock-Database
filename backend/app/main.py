from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Database imports
from app.database.database import engine, SessionLocal
from app.models.model import Base

# Router imports
from app.routers import users, portfolios, transactions, stocks, auth

# API Client import
from app.api_client.api_client import StockAPIClient

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stock Portfolio API",
    description="A stock tracking and portfolio management API",
    version="1.0.0"
)

# Add CORS for future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(portfolios.router)
app.include_router(transactions.router)
app.include_router(stocks.router)

# Stock API endpoints using StockAPIClient
@app.get("/api/stocks/{ticker}/price")
def get_stock_price(ticker: str):
    """Get current price for a stock ticker."""
    client = StockAPIClient()
    price = client.get_current_price(ticker)
    return {"ticker": ticker, "price": price}

@app.get("/api/stocks/search")
def search_stocks(query: str):
    """Search for stocks by keyword."""
    client = StockAPIClient()
    results = client.search_stocks(query)
    return {"query": query, "results": results}

@app.get("/")
def read_root():
    return {"message": "Stock Tracker API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)