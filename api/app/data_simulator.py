# Real-time Data Simulator with SQLite Persistence
import asyncio
import numpy as np
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.locations import Location
from app.models.river_levels import RiverLevel
from app.models.weather import Weather
from app.models.social import Social

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
    Continuously generate and persist new simulated data every 15 seconds.
    Data is saved directly to SQLite database using SQLAlchemy models.
    """
    global level_tracker, location_cache
    
    # Initialize simulation state
    await initialize_simulation_state()
    
    cycle = 0
    print("🌊 Starting real-time data generation...")

    while True:
        timestamp = datetime.now()
        
        try:
            with SessionLocal() as db:
                # Generate data for all sensor locations
                for sensor_id, (location_name, lat, lon) in SENSOR_LOCATIONS.items():
                    location_id = location_cache[sensor_id]
                    
                    # === RIVER LEVEL SIMULATION ===
                    prev_level = level_tracker[sensor_id]
                    change = np.random.normal(loc=0.02, scale=0.01)  # Slight upward drift
                    new_level = max(prev_level + change, 0)  # Prevent negative levels
                    level_tracker[sensor_id] = new_level
                    
                    # Create river level record
                    river_record = RiverLevel(
                        location_id=location_id,
                        timestamp=timestamp,
                        river_level_m=round(new_level, 2),
                        change_in_level_m=round(change, 3)
                    )
                    db.add(river_record)
                    
                    # === WEATHER SIMULATION ===
                    # Predicted values
                    pred_rain = round(np.random.uniform(0.5, 1.5), 2)
                    pred_wind = round(np.random.uniform(10, 15), 1)
                    pred_temp = round(np.random.uniform(26, 28), 1)
                    pred_humid = round(np.random.uniform(70, 85), 1)
                    pred_storm = random.random() < 0.3
                    
                    # Actual values (predicted + realistic error)
                    act_rain = pred_rain + np.random.normal(loc=0.1, scale=0.05)
                    act_wind = pred_wind + np.random.normal(loc=2, scale=0.5)
                    act_temp = pred_temp + np.random.normal(loc=-0.2, scale=0.2)
                    act_humid = pred_humid + np.random.normal(loc=5, scale=1)
                    act_storm = random.random() < 0.3
                    
                    # Create weather record
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
                    
                    sentiment = round(np.clip(np.random.normal(loc=sentiment_mean, scale=0.2), -1, 1), 2)
                    
                    # Post count varies by location and conditions
                    base_posts = 1
                    if flood_level:
                        post_multiplier = random.randint(3, 8)  # More posts during floods
                    elif high_rain:
                        post_multiplier = random.randint(2, 4)  # Some posts during heavy rain
                    else:
                        post_multiplier = random.randint(1, 2)  # Normal activity
                    
                    post_count = base_posts * post_multiplier
                    
                    # Create social record (one per location per timestamp - fully denormalized)
                    social_record = Social(
                        location_id=location_id,
                        timestamp=timestamp,
                        post_count=post_count,
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
                
                print(f"[{timestamp.strftime('%H:%M:%S')}] ✅ Generated data for {len(SENSOR_LOCATIONS)} locations")
                
        except Exception as e:
            print(f"❌ Error generating data: {e}")
            # Continue the loop even if there's an error
            
        # Wait before next generation cycle
        if cycle > 3:  # Skip initial delays for faster startup
            await asyncio.sleep(15)
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
                
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
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
