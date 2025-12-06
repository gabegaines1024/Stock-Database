Summary
Implemented authentication/authorization and live stock price monitoring with WebSocket/SSE.
Backend changes
Authentication & Authorization:
Added /auth/register endpoint for user registration
Updated user schemas to remove required fields from UserCreate
Protected routes: portfolios, transactions, and stock creation require authentication
User-scoped data: portfolios and transactions filtered by authenticated user
Added /auth/me endpoint to get current user info
WebSocket live price updates:
Created websocket_manager.py to manage connections and price broadcasting
Added /ws/prices WebSocket endpoint
Background task fetches prices every 5 seconds and broadcasts to subscribed clients
Supports subscribe/unsubscribe for specific tickers
Price caching to send immediate updates on subscription
Frontend changes
Authentication UI:
Created AuthContext for managing auth state
Added Login and Register pages with forms
Updated API service with JWT token handling and interceptors
Protected routes redirect to login if not authenticated
Updated Header to show username and logout button
Live price monitoring:
Created WebSocket client service (websocket.ts) with auto-reconnect
Updated StockSearch page to show live prices for tracked stocks
Updated Dashboard to show live prices for transaction tickers with price change indicators
Visual indicators (pulsing green dot) for live prices
UI updates:
Removed user_id selection from portfolio creation (auto-assigned)
Added live price displays with percentage change indicators
Styling for live price indicators
Features
User registration and login with JWT tokens
Protected routes requiring authentication
User-scoped data (users only see their own portfolios/transactions)
Real-time stock price updates via WebSocket
Auto-reconnect for WebSocket connections
Live price indicators on Dashboard and Stock Search pages
Price change percentages shown for transactions
The application now supports user authentication and real-time stock price monitoring. Users can register, log in, manage their portfolios, and see live price updates for their tracked stocks.