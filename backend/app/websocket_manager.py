import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.api_client.api_client import StockAPIClient


class ConnectionManager:
    """Manages WebSocket connections and broadcasts stock price updates."""
    
    def __init__(self):
        # Map of ticker -> set of websocket connections subscribed to it
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of websocket -> set of tickers it's subscribed to
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.client = StockAPIClient()
        self.price_cache: Dict[str, float] = {}
        self._broadcast_task = None
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.connection_subscriptions[websocket] = set()
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection and its subscriptions."""
        # Remove from all ticker subscriptions
        if websocket in self.connection_subscriptions:
            tickers = self.connection_subscriptions[websocket].copy()
            for ticker in tickers:
                self.unsubscribe(websocket, ticker)
            del self.connection_subscriptions[websocket]
    
    def subscribe(self, websocket: WebSocket, ticker: str):
        """Subscribe a connection to a ticker symbol."""
        ticker = ticker.upper()
        if ticker not in self.active_connections:
            self.active_connections[ticker] = set()
        self.active_connections[ticker].add(websocket)
        self.connection_subscriptions[websocket].add(ticker)
    
    def unsubscribe(self, websocket: WebSocket, ticker: str):
        """Unsubscribe a connection from a ticker symbol."""
        ticker = ticker.upper()
        if ticker in self.active_connections:
            self.active_connections[ticker].discard(websocket)
            if not self.active_connections[ticker]:
                del self.active_connections[ticker]
        if websocket in self.connection_subscriptions:
            self.connection_subscriptions[websocket].discard(ticker)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_text(message)
        except Exception:
            # Connection may be closed
            self.disconnect(websocket)
    
    async def broadcast_price_update(self, ticker: str, price: float):
        """Broadcast a price update to all connections subscribed to a ticker."""
        ticker = ticker.upper()
        if ticker not in self.active_connections:
            return
        
        message = json.dumps({
            "type": "price_update",
            "ticker": ticker,
            "price": price,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Send to all subscribed connections
        disconnected = []
        for connection in self.active_connections[ticker].copy():
            try:
                await connection.send_text(message)
            except Exception:
                # Connection is closed, mark for removal
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def fetch_and_broadcast_prices(self):
        """Periodically fetch prices for all subscribed tickers and broadcast updates."""
        while True:
            try:
                # Get all unique tickers that have active subscriptions
                tickers_to_update = set(self.active_connections.keys())
                
                for ticker in tickers_to_update:
                    try:
                        # Fetch current price
                        price = self.client.get_current_price(ticker)
                        self.price_cache[ticker] = price
                        
                        # Broadcast update
                        await self.broadcast_price_update(ticker, price)
                    except Exception as e:
                        # If price fetch fails, send error to subscribers
                        error_message = json.dumps({
                            "type": "error",
                            "ticker": ticker,
                            "message": f"Failed to fetch price: {str(e)}"
                        })
                        for connection in self.active_connections.get(ticker, set()).copy():
                            try:
                                await connection.send_text(error_message)
                            except Exception:
                                self.disconnect(connection)
                
                # Wait 5 seconds before next update cycle
                await asyncio.sleep(5)
            except Exception as e:
                # Log error and continue
                print(f"Error in price broadcast loop: {e}")
                await asyncio.sleep(5)
    
    def start_broadcast_task(self):
        """Start the background task for price broadcasting."""
        if self._broadcast_task is None or self._broadcast_task.done():
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self._broadcast_task = loop.create_task(self.fetch_and_broadcast_prices())


# Global connection manager instance
manager = ConnectionManager()

