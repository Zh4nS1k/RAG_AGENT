import uvicorn
from src.interfaces.api import app

if __name__ == "__main__":
    print("🚀 Starting RAG Agent Backend on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)