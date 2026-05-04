# AI4SIDS Real-Time API - Clean MVC Architecture
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
from app.core.db import init_db

from app.core.db import init_db, SessionLocal
from app.core.auth import router as auth_router, seed_default_user
from app.data_simulator import generate_realtime_data
from app.features.location.controller import router as location_router
from app.features.analytics.controller import router as analytics_router
from app.background_tasks import start_prediction_tasks, stop_prediction_tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and start background tasks"""
    print("🚀 Initializing AI4SIDS Real-Time API...")
    
    # Initialize database
    print("📊 Connecting to database...")
    try:
        init_db()
        print("✅ Database connection established")
        # Seed default user if not present
        db = SessionLocal()
        try:
            seed_default_user(db)
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        print("   API will continue, but database operations may fail")
    
    # Load initial data from JSON files if available
    # await load_all_data()
    
    # Start real-time data generation (non-blocking)
    print("🌊 Starting data generation task...")
    asyncio.create_task(generate_realtime_data())
    
    # Start background prediction generation tasks (non-blocking)
    print("🔮 Starting prediction tasks...")
    asyncio.create_task(start_prediction_tasks())
    
    print("✅ AI4SIDS Real-Time API started successfully")
    print("📊 Database: Connected")
    print("🌊 Real-time generation: Controlled via ENABLE_BACKGROUND_TASK")
    print("🔮 Prediction generation: Running in background")
    print("🧹 Auto-cleanup: Keep last 24 hours of data")
    print("🌐 Server ready to accept requests")
    
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
    app.include_router(auth_router)
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

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health monitoring"""
    return {
        "status": "healthy",
        "service": "AI4SIDS Real-Time API",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
