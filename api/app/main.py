"""
AI4SIDS Real-Time Demo API - Reorganized with feature-based architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.db import init_db
from app.core.data_loader import load_all_data
from app.features.location.contoller import router as location_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and load data on startup"""
    # Initialize database tables
    init_db()
    
    # Load data from JSON files
    try:
        load_all_data()
        print("✅ Data loaded successfully")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
    
    print("🚀 AI4SIDS Demo API started successfully")
    
    yield  # The application runs here


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(location_router)


@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "features": ["location_management", "real_time_monitoring", "analytics"]
    }