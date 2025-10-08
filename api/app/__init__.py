# AI4SIDS Real-Time API - Clean MVC Architecture
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.core.db import init_db
from app.core.data_loader import load_all_data
from app.data_simulator import generate_realtime_data
from app.features.location.contoller import router as location_router
from app.features.analytics.controller import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and start background tasks"""
    print("🚀 Initializing AI4SIDS Real-Time API...")
    
    # Initialize database
    init_db()
    
    # Load initial data from JSON files if available
    # await load_all_data()
    
    # Start real-time data generation
    asyncio.create_task(generate_realtime_data())
    
    print("✅ AI4SIDS Real-Time API started successfully")
    print("📊 Database: SQLite with real-time data simulation")
    print("🌊 Real-time generation: Every 15 seconds")
    print("🧹 Auto-cleanup: Keep last 24 hours of data")
    
    yield


app = FastAPI(
    title="AI4SIDS Real-Time Flood Monitoring API",
    description="Real-time flood monitoring system for Small Island Developing States",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(location_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    """API root endpoint with system information"""
    from app.services.realtime_data_service import RealTimeDataService
    
    stats = RealTimeDataService.get_data_statistics()
    
    return {
        "message": "AI4SIDS Real-Time Flood Monitoring API",
        "version": "3.0.0",
        "status": "active",
        "architecture": "MVC (Models-Views-Controllers)",
        "database": "SQLite with real-time simulation",
        "data_statistics": stats,
        "endpoints": {
            "locations": "/api/locations",
            "real_time": "/api/real-time/{location}",
            "history": "/api/history/{location}",
            "timeline": "/api/timeline/{location}",
            "system_update": "/api/system-update",
            "analytics": "/api/analytics/{location_id}",
            "predictions": "/api/analytics/{location_id}/predictions",
            "analytics_summary": "/api/analytics/"
        },
        "features": [
            "Real-time river level monitoring",
            "Weather prediction vs actual tracking", 
            "Social media sentiment analysis",
            "Flood risk assessment",
            "Historical data analysis",
            "Automated data cleanup",
            "SQLite persistence",
            "Predictive analytics with 30-minute forecasting",
            "Prediction accuracy tracking",
            "Interactive analytics API"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.realtime_data_service import RealTimeDataService
    
    try:
        stats = RealTimeDataService.get_data_statistics()
        locations = RealTimeDataService.get_available_locations()
        
        return {
            "status": "healthy",
            "database": "connected",
            "active_locations": len(locations),
            "total_records": (
                stats.get("river_records", 0) + 
                stats.get("weather_records", 0) + 
                stats.get("social_records", 0)
            ),
            "last_update": stats.get("latest_update"),
            "simulation": "active"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database": "disconnected"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)