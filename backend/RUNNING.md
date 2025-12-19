# Running the Application

## Quick Start

**Always run from the `backend` directory:**

```bash
cd backend
python run.py
```

Or using uvicorn directly:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'app'`

**Cause:** Running uvicorn from the wrong directory (e.g., from `backend/app/`)

**Solution:** Always run from the `backend/` directory, not from `backend/app/`

```bash
# ❌ WRONG - Running from app directory
cd backend/app
uvicorn main:app --reload  # This will fail!

# ✅ CORRECT - Running from backend directory
cd backend
python run.py
# OR
cd backend
uvicorn app.main:app --reload
```

### Issue: Bad interpreter path in venv

**Cause:** Virtual environment was moved or created in a different location

**Solution:** Recreate the virtual environment:

```bash
cd backend
rm -rf venv .venv
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

## Recommended Method

Use the `run.py` script (handles path setup automatically):

```bash
cd backend
python run.py
```

This script:
- Sets up Python path correctly
- Changes to the correct directory
- Configures reload directories
- Handles all path issues automatically

## Environment Setup

Make sure you have a `.env` file in the `backend/` directory:

```env
API_KEY=your_alpha_vantage_api_key
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./stock-tracker.db
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_TO_CONSOLE=true
ENVIRONMENT=development
```

## Verification

After starting, you should see:
- Server running on `http://localhost:8000`
- API docs at `http://localhost:8000/docs`
- Log messages in console (and `backend/logs/` if file logging is enabled)

