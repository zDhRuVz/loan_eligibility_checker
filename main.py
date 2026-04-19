import sys
import os

# Ensure the backend directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Now we can safely import 'app' from the backend folder
# This avoids the circular import named 'app'
from app import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
