from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

# Database imports
from app.database.database import engine, SessionLocal
from app.models.model import Base

# Config imports
from app.config import settings

# Router imports
from app.routers import users, portfolios, transactions, stocks, auth

# API Client import
from app.api_client.api_client import StockAPIClient

# WebSocket manager
from app.websocket_manager import manager

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Stock Portfolio API",
    description="A stock tracking and portfolio management API",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware - restrict to frontend URL for security
# In production, only allow requests from the configured frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
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

# Start WebSocket broadcast task
@app.on_event("startup")
async def startup_event():
    """Start the WebSocket price broadcast task on application startup."""
    manager.start_broadcast_task()

# Stock API endpoints using StockAPIClient
@app.get("/api/stocks/{ticker}/price")
def get_stock_price(ticker: str):
    """Get current price for a stock ticker (public endpoint)."""
    client = StockAPIClient()
    price = client.get_current_price(ticker)
    return {"ticker": ticker, "price": price}

@app.get("/api/stocks/search")
def search_stocks(query: str):
    """Search for stocks by keyword (public endpoint)."""
    client = StockAPIClient()
    results = client.search_stocks(query)
    return {"query": query, "results": results}

@app.get("/")
def read_root():
    return {"message": "Stock Tracker API"}


@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for live stock price updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Receive messages from client (subscribe/unsubscribe requests)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "subscribe":
                    ticker = message.get("ticker", "").upper()
                    if ticker:
                        manager.subscribe(websocket, ticker)
                        # Send cached price if available
                        if ticker in manager.price_cache:
                            await manager.send_personal_message(
                                json.dumps({
                                    "type": "price_update",
                                    "ticker": ticker,
                                    "price": manager.price_cache[ticker],
                                    "cached": True
                                }),
                                websocket
                            )
                
                elif msg_type == "unsubscribe":
                    ticker = message.get("ticker", "").upper()
                    if ticker:
                        manager.unsubscribe(websocket, ticker)
                
                elif msg_type == "ping":
                    # Respond to ping with pong
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        websocket
                    )
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON"}),
                    websocket
                )
            except Exception as e:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": str(e)}),
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)