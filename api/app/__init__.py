# AI4SIDS Real-Time API - Clean MVC Architecture
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.core.db import init_db
from app.data_simulator import generate_realtime_data
from app.features.location.controller import router as location_router
from app.features.analytics.controller import router as analytics_router
from app.background_tasks import start_prediction_tasks, stop_prediction_tasks


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
    
    # Start background prediction generation tasks
    await start_prediction_tasks()
    
    print("✅ AI4SIDS Real-Time API started successfully")
    print("📊 Database: SQLite with real-time data simulation")
    print("🌊 Real-time generation: Every 15 seconds")
    print("🔮 Prediction generation: Every 5 minutes")
    print("🧹 Auto-cleanup: Keep last 24 hours of data")
    
    yield
    
    # Cleanup when shutting down
    print("🛑 Shutting down AI4SIDS Real-Time API...")
    await stop_prediction_tasks()
    print("✅ Shutdown complete")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
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

    return app

app = create_app()


@app.get("/api/predictions/status")
async def get_prediction_status():
    """Get status of background prediction tasks"""
    from app.background_tasks import get_prediction_task_status
    return get_prediction_task_status()


@app.post("/api/predictions/generate")
async def trigger_prediction_generation():
    """Manually trigger prediction generation for all locations"""
    from app.background_tasks import force_prediction_generation
    try:
        await force_prediction_generation()
        return {"success": True, "message": "Prediction generation triggered successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to trigger prediction generation: {str(e)}"}


# ============================================================================
# BACKGROUND DATA GENERATION CONTROL ENDPOINTS
# ============================================================================

@app.get("/api/data-generation/status")
async def get_data_generation_status():
    """Get status of background data generation task"""
    from app.data_simulator import get_background_task_status
    return get_background_task_status()


@app.post("/api/data-generation/start")
async def start_data_generation():
    """Start background data generation task"""
    from app.data_simulator import start_background_generation
    result = await start_background_generation()
    return result


@app.post("/api/data-generation/stop")
async def stop_data_generation():
    """Stop background data generation task"""
    from app.data_simulator import stop_background_generation
    result = await stop_background_generation()
    return result
