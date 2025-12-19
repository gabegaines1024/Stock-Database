from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
import json
import logging

# Database imports
from app.database.database import engine, SessionLocal
from app.models.model import Base

# Config imports
from app.config import settings

# Logging
from app.logging_config import setup_logging, get_logger

# Exception handlers
from app.error_handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.exceptions import AppException

# Router imports
from app.routers import users, portfolios, transactions, stocks, auth

# API Client import
from app.api_client.api_client import StockAPIClient

# WebSocket manager
from app.websocket_manager import manager

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler  # type: ignore
from slowapi.util import get_remote_address  # type: ignore
from slowapi.errors import RateLimitExceeded  # type: ignore

# Setup logging (with error handling in case of path issues)
try:
    setup_logging(
        log_level=settings.log_level,
        log_to_file=settings.log_to_file,
        log_to_console=settings.log_to_console
    )
    logger = get_logger(__name__)
except Exception as e:
    # Fallback to basic logging if setup fails
    import logging as std_logging
    std_logging.basicConfig(level=std_logging.INFO)
    logger = std_logging.getLogger(__name__)
    logger.warning(f"Failed to setup custom logging: {e}. Using basic logging.")

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

# Add custom exception handlers
app.add_exception_handler(AppException, app_exception_handler)  # type: ignore
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(Exception, general_exception_handler)  # type: ignore

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
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log level: {settings.log_level}")
    manager.start_broadcast_task()
    logger.info("WebSocket broadcast task started")
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down application...")

# Stock API endpoints using StockAPIClient
@app.get("/api/stocks/{ticker}/price")
def get_stock_price(ticker: str):
    """Get current price for a stock ticker (public endpoint)."""
    logger.info(f"Fetching price for ticker: {ticker}")
    try:
        client = StockAPIClient()
        price = client.get_current_price(ticker)
        logger.info(f"Successfully fetched price for {ticker}: ${price}")
        return {"ticker": ticker, "price": price}
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {str(e)}", exc_info=True)
        raise

@app.get("/api/stocks/search")
def search_stocks(query: str):
    """Search for stocks by keyword (public endpoint)."""
    logger.info(f"Searching stocks with query: {query}")
    try:
        client = StockAPIClient()
        results = client.search_stocks(query)
        logger.info(f"Found {len(results)} results for query: {query}")
        return {"query": query, "results": results}
    except Exception as e:
        logger.error(f"Error searching stocks with query '{query}': {str(e)}", exc_info=True)
        raise

@app.get("/")
def read_root():
    """Root endpoint - API health check."""
    logger.debug("Root endpoint accessed")
    return {"message": "Stock Tracker API", "version": "1.0.0"}


@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for live stock price updates."""
    logger.info("WebSocket connection established")
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
                        logger.debug(f"WebSocket subscribe request for {ticker}")
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
                        logger.debug(f"WebSocket unsubscribe request for {ticker}")
                        manager.unsubscribe(websocket, ticker)
                
                elif msg_type == "ping":
                    # Respond to ping with pong
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        websocket
                    )
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON received in WebSocket: {str(e)}")
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON"}),
                    websocket
                )
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}", exc_info=True)
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": str(e)}),
                    websocket
                )
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)