# Stock Tracker API Backend

A FastAPI-based backend for the Stock Tracker application that provides portfolio management, transaction tracking, and real-time stock price updates.

## Features

- User authentication with JWT tokens
- Portfolio management (create, read, update, delete)
- Transaction tracking (buy/sell stocks)
- Real-time stock price updates via WebSocket
- Position tracking and validation
- Alpha Vantage API integration for stock data

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Edit `.env` and add your configuration:
   - `API_KEY`: Your Alpha Vantage API key
   - `SECRET_KEY`: A secure random string for JWT signing
   - `DATABASE_URL`: Database connection string (default: SQLite)

### Database Migrations

This project uses Alembic for database migrations.

#### Running Migrations

To apply all pending migrations:
```bash
alembic upgrade head
```

#### Creating New Migrations

When you modify the database models, create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Then review the generated migration file in `alembic/versions/` and apply it:
```bash
alembic upgrade head
```

#### Migration Commands

- `alembic current` - Show current migration version
- `alembic history` - Show migration history
- `alembic downgrade -1` - Rollback one migration
- `alembic downgrade base` - Rollback all migrations

## Running the Server

### Development

```bash
python run.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration scripts
│   └── env.py           # Alembic configuration
├── app/
│   ├── api_client/      # External API clients
│   ├── crud/            # Database CRUD operations
│   ├── database/        # Database configuration
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API route handlers
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic services
│   ├── config.py        # Application configuration
│   ├── dependencies.py  # FastAPI dependencies
│   ├── main.py          # FastAPI application
│   ├── security.py      # Authentication utilities
│   └── websocket_manager.py  # WebSocket manager
├── alembic.ini          # Alembic configuration file
├── requirements.txt     # Python dependencies
└── run.py              # Application entry point
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Portfolios
- `GET /portfolios` - List user's portfolios
- `POST /portfolios` - Create a new portfolio
- `GET /portfolios/{id}` - Get portfolio details
- `PUT /portfolios/{id}` - Update portfolio
- `DELETE /portfolios/{id}` - Delete portfolio

### Transactions
- `GET /transactions` - List user's transactions
- `POST /transactions` - Create a new transaction
- `GET /transactions/{id}` - Get transaction details
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction
- `GET /transactions/position/{portfolio_id}/{ticker}` - Get current position

### Stocks
- `GET /stocks` - List all stocks
- `POST /stocks` - Add a new stock
- `GET /stocks/{id}` - Get stock details
- `PUT /stocks/{id}` - Update stock
- `DELETE /stocks/{id}` - Delete stock
- `GET /api/stocks/{ticker}/price` - Get stock price
- `GET /api/stocks/search` - Search stocks

### WebSocket
- `WS /ws/prices` - Real-time stock price updates

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Alpha Vantage API key | Required |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///./stock-tracker.db` |

## Development

### Code Style

The project follows PEP 8 guidelines. Use type hints for better code maintainability.

### Testing

(Testing framework to be added)

## License

(License information to be added)
