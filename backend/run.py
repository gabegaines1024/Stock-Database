#!/usr/bin/env python3
"""
Run script for the Stock Tracker API.
This script ensures proper Python path setup before starting the server.
"""
import sys
import os
from pathlib import Path

# Get the backend directory (where this script is located)
backend_dir = Path(__file__).parent.absolute()

# Add the backend directory to Python path so 'app' module can be found
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure relative paths work
os.chdir(backend_dir)

# Set PYTHONPATH environment variable for subprocesses
os.environ["PYTHONPATH"] = str(backend_dir)

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(backend_dir / "app")],
        reload_includes=["*.py"],
    )

