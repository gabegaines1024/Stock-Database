# Stock Tracker - Full-Stack Application

A comprehensive stock portfolio tracking application with real-time price updates, built with FastAPI (backend) and React + TypeScript (frontend).

## Features

- 🔐 User authentication with JWT tokens
- 📊 Portfolio management (create, edit, delete)
- 💰 Transaction tracking (buy/sell with position validation)
- 📈 Real-time stock price updates via WebSocket
- 🔍 Stock search and price lookup
- 📱 Responsive, modern UI
- 🛡️ Rate limiting and CORS protection

## Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **Alpha Vantage API Key** ([Get one here](https://www.alphavantage.co/support/#api-key))

## Quick Start

### 1. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

#### Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter SSL certificate errors during installation, use:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Required: Alpha Vantage API Key
API_KEY=your_alpha_vantage_api_key_here

# Required: JWT Secret Key (generate a secure random string)
SECRET_KEY=your-secret-key-change-in-production

# Optional: Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///./stock-tracker.db

# Optional: Frontend URL for CORS (defaults to Vite dev server)
FRONTEND_URL=http://localhost:5173
```

**Generate a secure SECRET_KEY:**

```bash
# On macOS/Linux
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Run Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Verify current migration version
alembic current
```

#### Start the Backend Server

```bash
# Using the run script (recommended)
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API Base URL:** `http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

### 2. Frontend Setup

Open a **new terminal** and navigate to the frontend directory:

```bash
cd frontend
```

#### Install Dependencies

```bash
npm install
```

#### Configure Environment Variables (Optional)

Create a `.env` file in the `frontend/` directory if you need to change the API URL:

```env
VITE_API_URL=http://localhost:8000
```

#### Start the Development Server

```bash
npm run dev
```

The frontend will be available at:
- **Frontend URL:** `http://localhost:5173`

---

## Startup Checklist

After starting both servers, verify the following:

### ✅ Backend Verification

1. **FastAPI Documentation**
   - Open `http://localhost:8000/docs` in your browser
   - You should see the Swagger UI with all API endpoints
   - Try the "GET /" endpoint to verify the API is responding

2. **Database Connection**
   - Check that `stock-tracker.db` file exists in the `backend/` directory
   - Verify migrations were applied: `alembic current` should show a revision

3. **Environment Variables**
   - Ensure `API_KEY` is set in `.env` (required for stock price lookups)
   - Ensure `SECRET_KEY` is set (required for JWT authentication)

### ✅ Frontend Verification

1. **Frontend Page**
   - Open `http://localhost:5173` in your browser
   - You should see the login/register page
   - No console errors should appear

2. **API Connection**
   - Open browser DevTools (F12) → Network tab
   - Try logging in or registering
   - API calls should go to `http://localhost:8000`

### ✅ User Registration & Login

1. **Register a New User**
   - Click "Register" on the login page
   - Fill in email, username, and password (min 8 characters)
   - Click "Register"
   - You should be automatically logged in and redirected to the dashboard

2. **Login**
   - If already registered, enter username and password
   - Click "Login"
   - You should be redirected to the dashboard

3. **Verify Authentication**
   - Check that your username appears in the header
   - Protected routes should be accessible
   - Logout button should be visible

### ✅ Live WebSocket Price Updates

1. **Navigate to Dashboard**
   - After logging in, you should be on the dashboard
   - If you have transactions, you should see live price indicators

2. **Test Stock Search**
   - Navigate to "Stock Search" page
   - Search for a stock (e.g., "AAPL" or "Microsoft")
   - Click "Get Price" on a stock
   - You should see the current price
   - A green pulsing dot (●) indicates live price updates

3. **Verify WebSocket Connection**
   - Open browser DevTools (F12) → Console tab
   - You should see: `WebSocket connected`
   - Add a transaction with a stock ticker
   - Return to dashboard
   - Live prices should update every 5 seconds

4. **Test Real-time Updates**
   - Keep the dashboard open
   - Stock prices should update automatically
   - Price change percentages should update in real-time

---

## Project Structure

```
Stock-Database/
├── backend/                 # FastAPI backend
│   ├── alembic/            # Database migrations
│   │   ├── versions/       # Migration scripts
│   │   └── env.py          # Alembic configuration
│   ├── app/                # Application code
│   │   ├── api_client/     # External API clients
│   │   ├── crud/           # Database operations
│   │   ├── database/       # Database configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # API route handlers
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Configuration
│   │   ├── main.py         # FastAPI app
│   │   └── ...
│   ├── alembic.ini         # Alembic config
│   ├── requirements.txt    # Python dependencies
│   ├── run.py             # Server entry point
│   └── .env               # Environment variables (create from .env.example)
│
└── frontend/              # React frontend
    ├── src/
    │   ├── components/    # Reusable components
    │   ├── contexts/      # React contexts
    │   ├── hooks/         # Custom hooks
    │   ├── pages/         # Page components
    │   ├── services/      # API services
    │   └── ...
    ├── package.json      # Node dependencies
    └── vite.config.ts    # Vite configuration
```

---

## Common Commands

### Backend

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run migrations
alembic upgrade head              # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic current                   # Show current version
alembic history                   # Show migration history

# Start server
python run.py                     # With auto-reload
uvicorn app.main:app --reload    # Alternative
```

### Frontend

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Troubleshooting

### Backend Issues

**Problem:** `API_KEY environment variable is not set`
- **Solution:** Ensure `.env` file exists in `backend/` directory with `API_KEY=your_key`

**Problem:** `ModuleNotFoundError: No module named 'app'`
- **Solution:** Make sure you're running from the `backend/` directory or using `python run.py`

**Problem:** Database migration errors
- **Solution:** Check that `DATABASE_URL` in `.env` is correct and database file is writable

**Problem:** Rate limiting not working
- **Solution:** Ensure `slowapi` is installed: `pip install slowapi`

**Problem:** `RuntimeError: Form data requires "python-multipart" to be installed`
- **Solution:** Install the missing package: `pip install python-multipart`

### Frontend Issues

**Problem:** CORS errors in browser console
- **Solution:** Check that `FRONTEND_URL` in backend `.env` matches your frontend URL (default: `http://localhost:5173`)

**Problem:** API calls failing with 401 Unauthorized
- **Solution:** Clear localStorage and log in again: `localStorage.clear()` in browser console

**Problem:** WebSocket not connecting
- **Solution:** 
  - Check backend is running on port 8000
  - Verify WebSocket endpoint: `ws://localhost:8000/ws/prices`
  - Check browser console for connection errors

**Problem:** Stock prices not updating
- **Solution:**
  - Verify `API_KEY` is set in backend `.env`
  - Check backend logs for API errors
  - Ensure Alpha Vantage API key is valid (free tier: 5 calls/minute)

---

## Development Workflow

### Making Database Changes

1. Modify models in `backend/app/models/model.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply migration: `alembic upgrade head`

### Adding New Features

1. **Backend:**
   - Add routes in `backend/app/routers/`
   - Add schemas in `backend/app/schemas/`
   - Add CRUD operations in `backend/app/crud/`

2. **Frontend:**
   - Add pages in `frontend/src/pages/`
   - Add components in `frontend/src/components/`
   - Update API service in `frontend/src/services/api.ts`

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI:** `http://localhost:8000/docs` (interactive API documentation)
- **ReDoc:** `http://localhost:8000/redoc` (alternative documentation)

---

## Security Notes

- **Never commit `.env` files** - They contain sensitive keys
- **Change default SECRET_KEY** - Generate a secure random string for production
- **Rate Limiting** - Auth endpoints are limited to 5 requests/minute
- **CORS** - Only configured frontend URL can access the API
- **JWT Tokens** - Expire after 30 minutes (configurable)

---

## License

[Add your license information here]

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check backend logs for error messages
4. Verify all environment variables are set correctly

---

**Happy Trading! 📈**
