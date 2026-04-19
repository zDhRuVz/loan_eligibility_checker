import sys
import os

# Add the 'backend' directory to the Python path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import the FastAPI app from backend/app.py
from app import app

# This allows the root 'app' object to be detected by Render/Gunicorn/Uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
