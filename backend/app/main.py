from fastapi import FastAPI
from app.api.v1.routes import router as api_router

# Initialize FastAPI app
app = FastAPI(
    title="Stock Insight Backend",
    description="Backend for RAG-based Financial Assistant",
    version="1.0.0"
)

# Include routes from API version 1
app.include_router(api_router, prefix="/api/v1")