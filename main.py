import sys
import os

# 1. Add the backend directory to the search path
# We use an absolute path to ensure accuracy inside the Render container
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# 2. Import the FastAPI 'app' from backend/app.py
try:
    from app import app
except ImportError:
    # Fallback for different environment configurations
    import backend.app as backend_app
    app = backend_app.app

# This root file can now be targeted as 'main:app' or 'app:app'
# if you rename it. But 'main:app' is the current render.yaml default.
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
