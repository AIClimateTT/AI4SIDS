# Real-time Data Simulator with SQLite Persistence
import asyncio
import numpy as np
import random
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.locations import Location
from app.models.river_levels import RiverLevel
from app.models.weather import Weather
from app.models.social import Social
from app.core.config import settings

# Configuration: Cycle interval in seconds
# Set via environment variable for easy deployment adjustment
CYCLE_INTERVAL = settings.DATA_CYCLE_INTERVAL  # Default: 1 hour
ENABLE_BACKGROUND_TASK = settings.ENABLE_BACKGROUND_TASK

# Define sensor locations - matches your existing sensor network
SENSOR_LOCATIONS = {
    "CR-001": ("St. Augustine", 10.6406, -61.3994),
    "CR-002": ("Cunupia", 10.5682, -61.3702),
    "CR-003": ("Piarco", 10.5957, -61.3376),
    "CR-004": ("St. Helena", 10.5989, -61.3222),
    "CR-005": ("Chaguanas", 10.5164, -61.4115),
    "CR-006": ("Kelly Village", 10.6102, -61.3361),
    "CR-007": ("Las Lomas", 10.6261, -61.3647),
    "CR-008": ("Caroni", 10.5654, -61.4592)
}

# Global state for persistent simulation
level_tracker = {}  # Track river levels between cycles
location_cache = {}  # Cache location IDs to avoid repeated queries
_background_task_running = False  # Track if background task is running
_background_task = None  # Reference to the running task


async def initialize_simulation_state():
    """Initialize simulation state and ensure locations exist in database"""
    global level_tracker, location_cache
    
    print("🔄 Initializing real-time simulation state...")
    
    try:
        with SessionLocal() as db:
            # Ensure all sensor locations exist in the database
            for sensor_id, (location_name, lat, lon) in SENSOR_LOCATIONS.items():
                location = db.query(Location).filter(Location.sensor_id == sensor_id).first()
                
                if not location:
                    # Create new location if it doesn't exist
                    location = Location(
                        name=location_name,
                        sensor_id=sensor_id,
                        latitude=lat,
                        longitude=lon
                    )
                    db.add(location)
                    db.commit()
                    db.refresh(location)
                    print(f"✅ Created location: {location_name} ({sensor_id})")
                
                # Cache location ID and initialize river level tracker
                location_cache[sensor_id] = location.id
                level_tracker[sensor_id] = 2.2  # Starting river level
                
            print(f"🎯 Simulation initialized for {len(SENSOR_LOCATIONS)} locations")
            
    except Exception as e:
        print(f"❌ Error initializing simulation: {e}")
        raise


async def generate_realtime_data():
    """
    Continuously generate and persist new simulated data.
    Controlled by ENABLE_BACKGROUND_TASK environment variable.
    For free hosting (Railway/Render), set ENABLE_BACKGROUND_TASK=false
    and use on-demand generation via API endpoints instead.
    """
    global _background_task_running
    
    if not ENABLE_BACKGROUND_TASK:
        print("⏸️  Background data generation is DISABLED (ENABLE_BACKGROUND_TASK=false)")
        print("📊 Data will be generated on-demand via API calls")
        _background_task_running = False
        return
    
    global level_tracker, location_cache
    
    # Initialize simulation state
    await initialize_simulation_state()
    
    _background_task_running = True
    cycle = 0
    print("🌊 Starting real-time data generation...")

    while _background_task_running:  # Changed from while True to respect stop signal
        timestamp = datetime.now(timezone.utc)
        
        try:
            with SessionLocal() as db:
                # Generate data for all sensor locations
                for sensor_id, (location_name, lat, lon) in SENSOR_LOCATIONS.items():
                    location_id = location_cache[sensor_id]
                    
                    # === RIVER LEVEL SIMULATION ===
                    # === VIDEO RECORDING MODE: Accelerated flood scenario ===
                    # prev_level = level_tracker[sensor_id]
                    
                    # # Create dramatic flood scenario for video
                    # if cycle < 20:  # First minute: gradual rise
                    #     change = np.random.normal(loc=0.08, scale=0.02)  # Faster rise
                    # elif cycle < 40:  # Second minute: rapid flood development
                    #     change = np.random.normal(loc=0.15, scale=0.03)  # Rapid rise
                    # elif cycle < 60:  # Third minute: peak flooding
                    #     change = np.random.normal(loc=0.05, scale=0.04)  # Near peak with fluctuation
                    # else:  # After 3 minutes: gradual decline
                    #     change = np.random.normal(loc=-0.02, scale=0.03)  # Slow decline
                    
                    # new_level = max(prev_level + change, 0)  # Prevent negative levels
                    # level_tracker[sensor_id] = new_level
                    
                    # === NORMAL PRODUCTION MODE (COMMENTED OUT) ===
                    prev_level = level_tracker[sensor_id]
                    change = np.random.normal(loc=0.02, scale=0.01)  # Slight upward drift
                    new_level = max(prev_level + change, 0)  # Prevent negative levels
                    level_tracker[sensor_id] = new_level
                    
                    # Create river level record (convert numpy types to Python types)
                    river_record = RiverLevel(
                        location_id=location_id,
                        timestamp=timestamp,
                        river_level_m=round(float(new_level), 2),
                        change_in_level_m=round(float(change), 3)
                    )
                    db.add(river_record)
                    
                    # === WEATHER SIMULATION ===
                    # === VIDEO RECORDING MODE: Weather supports flood scenario ===
                    if cycle < 30:  # First 1.5 minutes: heavy rain scenario
                        pred_rain = float(round(np.random.uniform(3.0, 5.0), 2))  # Heavy rain
                        pred_storm = True  # Storm conditions
                    elif cycle < 50:  # Next minute: continued rain
                        pred_rain = float(round(np.random.uniform(2.0, 4.0), 2))  # Moderate-heavy rain
                        pred_storm = random.random() < 0.7  # Likely storm
                    else:  # After 2.5 minutes: rain subsiding
                        pred_rain = float(round(np.random.uniform(0.5, 2.0), 2))  # Light-moderate rain
                        pred_storm = random.random() < 0.3  # Occasional storm
                    
                    # === NORMAL PRODUCTION MODE (COMMENTED OUT) ===
                    # pred_rain = round(np.random.uniform(0.5, 1.5), 2)
                    # pred_storm = random.random() < 0.3
                    pred_wind = float(round(np.random.uniform(10, 15), 1))
                    pred_temp = float(round(np.random.uniform(26, 28), 1))
                    pred_humid = float(round(np.random.uniform(70, 85), 1))
                    # pred_storm = random.random() < 0.3  # Moved above
                    
                    # Actual values (predicted + realistic error)
                    act_rain = float(pred_rain + np.random.normal(loc=0.1, scale=0.05))
                    act_wind = float(pred_wind + np.random.normal(loc=2, scale=0.5))
                    act_temp = float(pred_temp + np.random.normal(loc=-0.2, scale=0.2))
                    act_humid = float(pred_humid + np.random.normal(loc=5, scale=1))
                    act_storm = random.random() < 0.3
                    
                    # Create weather record (values already converted to Python types)
                    weather_record = Weather(
                        location_id=location_id,
                        timestamp=timestamp,
                        predicted_rainfall_mm=round(pred_rain, 2),
                        predicted_temperature_c=round(pred_temp, 1),
                        predicted_humidity_percent=round(pred_humid, 1),
                        predicted_windspeed_kmh=round(pred_wind, 1),
                        predicted_storm=pred_storm,
                        actual_rainfall_mm=round(act_rain, 2),
                        actual_temperature_c=round(act_temp, 1),
                        actual_humidity_percent=round(act_humid, 1),
                        actual_windspeed_kmh=round(act_wind, 1),
                        actual_storm=act_storm
                    )
                    db.add(weather_record)
                    
                    # === SOCIAL MEDIA SIMULATION (PER LOCATION) ===
                    # Generate sentiment based on current conditions
                    flood_level = new_level >= 3.0
                    high_rain = act_rain > 2.0
                    
                    # Sentiment gets worse with flooding and heavy rain
                    base_sentiment = -0.3
                    if flood_level and high_rain:
                        sentiment_mean = -0.7  # Very negative during floods
                    elif flood_level or high_rain:
                        sentiment_mean = -0.5  # Negative during concerning conditions
                    else:
                        sentiment_mean = base_sentiment
                    
                    sentiment = float(round(np.clip(np.random.normal(loc=sentiment_mean, scale=0.2), -1, 1), 2))
                    
                    # Post count varies by location and conditions
                    base_posts = 1
                    if flood_level:
                        post_multiplier = random.randint(3, 8)  # More posts during floods
                    elif high_rain:
                        post_multiplier = random.randint(2, 4)  # Some posts during heavy rain
                    else:
                        post_multiplier = random.randint(1, 2)  # Normal activity
                    
                    post_count = base_posts * post_multiplier
                    
                    # Create social record (values already converted to Python types)
                    social_record = Social(
                        location_id=location_id,
                        timestamp=timestamp,
                        post_count=int(post_count),
                        sentiment_score=sentiment
                    )
                    db.add(social_record)
                
                # Commit all records for this timestamp
                db.commit()
                
                # Clean up old data (keep only last 24 hours)
                cleanup_cutoff = timestamp - timedelta(hours=24)
                db.query(RiverLevel).filter(RiverLevel.timestamp < cleanup_cutoff).delete()
                db.query(Weather).filter(Weather.timestamp < cleanup_cutoff).delete()
                db.query(Social).filter(Social.timestamp < cleanup_cutoff).delete()
                db.commit()
                
                # Display local time in console for user convenience, but store UTC in database
                local_time = datetime.now()
                print(f"[{local_time.strftime('%H:%M:%S')}] ✅ Generated data for {len(SENSOR_LOCATIONS)} locations")
                
        except Exception as e:
            print(f"❌ Error generating data: {e}")
            # Continue the loop even if there's an error
            
        # Wait before next generation cycle
        if cycle > 3:  # Skip initial delays for faster startup
            await asyncio.sleep(CYCLE_INTERVAL)  # Configurable via env variable
        else:
            await asyncio.sleep(2)  # Faster initial cycles
            
        cycle += 1


# Utility functions for data access (used by API endpoints)
def get_latest_data_for_location(location_name: str, data_type: str = "river"):
    """Get the most recent data point for a specific location"""
    try:
        with SessionLocal() as db:
            location = db.query(Location).filter(Location.name == location_name).first()
            if not location:
                return None
                
            if data_type == "river":
                return db.query(RiverLevel).filter(
                    RiverLevel.location_id == location.id
                ).order_by(RiverLevel.timestamp.desc()).first()
                
            elif data_type == "weather":
                return db.query(Weather).filter(
                    Weather.location_id == location.id
                ).order_by(Weather.timestamp.desc()).first()
                
            elif data_type == "social":
                return db.query(Social).filter(
                    Social.location_id == location.id
                ).order_by(Social.timestamp.desc()).first()
                
    except Exception as e:
        print(f"Error fetching latest data: {e}")
        return None


def get_historical_data_for_location(location_name: str, data_type: str = "river", minutes: int = 60):
    """Get historical data points for a location within the specified time range"""
    try:
        with SessionLocal() as db:
            location = db.query(Location).filter(Location.name == location_name).first()
            if not location:
                return []
                
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            if data_type == "river":
                return db.query(RiverLevel).filter(
                    RiverLevel.location_id == location.id,
                    RiverLevel.timestamp >= cutoff_time
                ).order_by(RiverLevel.timestamp.asc()).all()
                
            elif data_type == "weather":
                return db.query(Weather).filter(
                    Weather.location_id == location.id,
                    Weather.timestamp >= cutoff_time
                ).order_by(Weather.timestamp.asc()).all()
                
            elif data_type == "social":
                return db.query(Social).filter(
                    Social.location_id == location.id,
                    Social.timestamp >= cutoff_time
                ).order_by(Social.timestamp.asc()).all()
                
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []


# ============================================================================
# BACKGROUND TASK CONTROL FUNCTIONS
# ============================================================================

async def start_background_generation():
    """Start the background data generation task"""
    global _background_task, _background_task_running, ENABLE_BACKGROUND_TASK
    
    if _background_task_running:
        return {"success": False, "message": "Background task is already running"}
    
    # Enable background task
    ENABLE_BACKGROUND_TASK = True
    
    # Start the task
    _background_task = asyncio.create_task(generate_realtime_data())
    
    return {"success": True, "message": "Background data generation started"}


async def stop_background_generation():
    """Stop the background data generation task"""
    global _background_task, _background_task_running
    
    if not _background_task_running:
        return {"success": False, "message": "Background task is not running"}
    
    # Signal the task to stop
    _background_task_running = False
    
    # Cancel the task if it exists
    if _background_task:
        _background_task.cancel()
        try:
            await _background_task
        except asyncio.CancelledError:
            pass
        _background_task = None
    
    return {"success": True, "message": "Background data generation stopped"}


def get_background_task_status():
    """Get the current status of the background data generation task"""
    return {
        "running": _background_task_running,
        "enabled_in_env": ENABLE_BACKGROUND_TASK,
        "cycle_interval_seconds": CYCLE_INTERVAL,
        "task_exists": _background_task is not None,
        "locations_count": len(SENSOR_LOCATIONS)
    }
