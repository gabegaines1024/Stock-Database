# Project Structure

This document describes the organization of the Stock Tracker codebase.

## Overview

```
Stock-Database/
├── backend/          # FastAPI backend application
├── frontend/         # React + TypeScript frontend application
├── README.md         # Main project documentation
├── .gitignore       # Git ignore rules
└── Documentation files (IMPLEMENTATION_SUMMARY.md, UPDATES.md)
```

## Backend Structure

```
backend/
├── app/                      # Main application code
│   ├── api_client/          # External API clients (Alpha Vantage)
│   ├── crud/                # Database CRUD operations
│   ├── database/            # Database configuration and connection
│   ├── models/              # SQLAlchemy database models
│   ├── routers/             # FastAPI route handlers
│   │   ├── auth.py         # Authentication routes
│   │   ├── portfolios.py  # Portfolio management routes
│   │   ├── stocks.py       # Stock management routes
│   │   ├── transactions.py  # Transaction management routes
│   │   └── users.py        # User management routes
│   ├── schemas/             # Pydantic schemas for request/response validation
│   ├── services/            # Business logic services
│   ├── config.py           # Application configuration
│   ├── dependencies.py     # FastAPI dependencies (auth, database)
│   ├── main.py             # FastAPI application entry point
│   ├── security.py         # Authentication and security utilities
│   └── websocket_manager.py # WebSocket connection management
├── alembic/                 # Database migrations
│   ├── versions/           # Migration scripts
│   └── env.py              # Alembic configuration
├── tests/                   # Test suite
│   ├── conftest.py         # Pytest fixtures and configuration
│   ├── test_auth.py        # Authentication tests
│   ├── test_crud.py        # CRUD operation tests
│   ├── test_api_endpoints.py # API endpoint integration tests
│   └── test_transaction_service.py # Transaction service tests
├── alembic.ini             # Alembic configuration file
├── pytest.ini              # Pytest configuration
├── pyproject.toml          # Python project metadata (uv)
├── pyrightconfig.json      # Type checking configuration
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point script
└── venv/                   # Python virtual environment (gitignored)
```

## Frontend Structure

```
frontend/
├── src/
│   ├── components/         # Reusable React components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Header.tsx
│   │   ├── Modal.tsx
│   │   ├── Toast.tsx
│   │   └── ...
│   ├── contexts/           # React contexts (AuthContext)
│   ├── hooks/              # Custom React hooks
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   ├── Portfolios.tsx
│   │   ├── Register.tsx
│   │   ├── StockSearch.tsx
│   │   └── Transactions.tsx
│   ├── services/           # API and WebSocket services
│   │   ├── api.ts          # REST API client
│   │   └── websocket.ts    # WebSocket client
│   ├── App.tsx             # Main application component
│   └── main.tsx            # Application entry point
├── public/                 # Static assets
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite build configuration
```

## Key Files

### Backend
- `backend/app/main.py` - FastAPI application initialization
- `backend/app/config.py` - Environment variable configuration
- `backend/app/dependencies.py` - FastAPI dependency injection
- `backend/run.py` - Development server entry point
- `backend/requirements.txt` - Python package dependencies
- `backend/alembic.ini` - Database migration configuration

### Frontend
- `frontend/src/App.tsx` - Main React application component
- `frontend/src/services/api.ts` - API client configuration
- `frontend/package.json` - Node.js dependencies

## Configuration Files

- `.gitignore` - Files and directories to exclude from version control
- `backend/pyrightconfig.json` - Python type checking configuration
- `backend/pytest.ini` - Test runner configuration
- `frontend/tsconfig.json` - TypeScript compiler configuration
- `frontend/vite.config.ts` - Vite build tool configuration

## Database

- Database file: `backend/stock-tracker.db` (SQLite, gitignored)
- Migrations: `backend/alembic/versions/`
- Models: `backend/app/models/model.py`

## Testing

- Test configuration: `backend/pytest.ini`
- Test fixtures: `backend/tests/conftest.py`
- Test files: `backend/tests/test_*.py`

## Environment Variables

Backend requires a `.env` file in `backend/` directory:
- `API_KEY` - Alpha Vantage API key
- `SECRET_KEY` - JWT secret key
- `DATABASE_URL` - Database connection string (optional)
- `FRONTEND_URL` - Frontend URL for CORS (optional)

## Notes

- Virtual environments (`venv/`) are gitignored
- Database files (`*.db`) are gitignored
- Cache directories (`__pycache__/`) are gitignored
- Node modules (`node_modules/`) are gitignored
- Environment files (`.env`) are gitignored

