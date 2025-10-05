# enhanced_main.py - FastAPI with Real Data Loading
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
import asyncio
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import os
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data and start background tasks"""
    load_data_from_json()
    asyncio.create_task(update_data_cycle())
    print("AI4SIDS Demo API started successfully")
    
    yield  # The application runs here

app = FastAPI(title="AI4SIDS Real-Time Demo API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage
river_data = []
weather_data = []
social_data = []
current_data_index = 45
data_interval_seconds = 15
base_timestamp = datetime(2025, 4, 12, 9, 0, 0)

# Enhanced data models
class LocationInfo(BaseModel):
    name: str
    latitude: float
    longitude: float
    sensor_id: str
    last_updated: datetime

class RealTimeConditions(BaseModel):
    location: str
    river_level: float
    river_trend: str
    change_rate: float
    flood_risk: str
    weather: Dict[str, float]
    social_activity: Dict[str, Any]
    timestamp: datetime
    
class ComprehensiveUpdate(BaseModel):
    locations: List[Dict[str, Any]]
    system_status: Dict[str, Any]
    alerts: List[Dict[str, str]]
    timestamp: datetime

# Data loading functions
def load_data_from_json():
    """Load data from JSON files or fallback to sample data"""
    global river_data, weather_data, social_data
    
    try:
        # Try to load from JSON files first
        if os.path.exists("data/river_data.json"):
            with open("data/river_data.json", "r") as f:
                river_data = json.load(f)
            print(f"Loaded {len(river_data)} river data points from JSON")
        
        if os.path.exists("data/weather_data.json"):
            with open("data/weather_data.json", "r") as f:
                weather_data = json.load(f)
            print(f"Loaded {len(weather_data)} weather data points from JSON")
        
        if os.path.exists("data/social_data.json"):
            with open("data/social_data.json", "r") as f:
                social_data = json.load(f)
            print(f"Loaded {len(social_data)} social data points from JSON")
    
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        print("Using fallback sample data...")
        load_fallback_data()

def load_fallback_data():
    """Load fallback sample data if JSON files are not available"""
    global river_data, weather_data, social_data
    
    # Extended sample data for demo
    river_data = [
        {"timestamp": "04/12/2025 9:00", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.21, "change_in_level_m": 0.007},
        {"timestamp": "04/12/2025 9:00", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.22, "change_in_level_m": 0.010},
        {"timestamp": "04/12/2025 9:01", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.25, "change_in_level_m": 0.030},
        {"timestamp": "04/12/2025 9:01", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.28, "change_in_level_m": 0.030},
        {"timestamp": "04/12/2025 9:02", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.32, "change_in_level_m": 0.040},
        {"timestamp": "04/12/2025 9:02", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.35, "change_in_level_m": 0.030},
        {"timestamp": "04/12/2025 9:03", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.38, "change_in_level_m": 0.030},
        {"timestamp": "04/12/2025 9:03", "sensor_id": "CR-001", "latitude": 10.6406, "longitude": -61.3994, "location": "St. Augustine", "river_level_m": 2.42, "change_in_level_m": 0.040},
        # Add Chaguanas data
        {"timestamp": "04/12/2025 9:00", "sensor_id": "CR-002", "latitude": 10.5168, "longitude": -61.4107, "location": "Chaguanas", "river_level_m": 1.85, "change_in_level_m": 0.005},
        {"timestamp": "04/12/2025 9:01", "sensor_id": "CR-002", "latitude": 10.5168, "longitude": -61.4107, "location": "Chaguanas", "river_level_m": 1.89, "change_in_level_m": 0.040},
        {"timestamp": "04/12/2025 9:02", "sensor_id": "CR-002", "latitude": 10.5168, "longitude": -61.4107, "location": "Chaguanas", "river_level_m": 1.95, "change_in_level_m": 0.060},
        {"timestamp": "04/12/2025 9:03", "sensor_id": "CR-002", "latitude": 10.5168, "longitude": -61.4107, "location": "Chaguanas", "river_level_m": 2.02, "change_in_level_m": 0.070},
    ]
    
    weather_data = [
        {"timestamp": "04/12/2025 9:00", "sensor_id": "CR-001", "location": "St. Augustine", "predicted_rainfall_mm": 0.83, "actual_rainfall_mm": 0.8, "actual_temperature_c": 26.7, "actual_humidity_percent": 72, "actual_windspeed_kmh": 10.5},
        {"timestamp": "04/12/2025 9:01", "sensor_id": "CR-001", "location": "St. Augustine", "predicted_rainfall_mm": 1.30, "actual_rainfall_mm": 1.31, "actual_temperature_c": 26.8, "actual_humidity_percent": 85, "actual_windspeed_kmh": 14.7},
        {"timestamp": "04/12/2025 9:02", "sensor_id": "CR-001", "location": "St. Augustine", "predicted_rainfall_mm": 1.49, "actual_rainfall_mm": 1.42, "actual_temperature_c": 26.2, "actual_humidity_percent": 75, "actual_windspeed_kmh": 10.8},
        {"timestamp": "04/12/2025 9:03", "sensor_id": "CR-001", "location": "St. Augustine", "predicted_rainfall_mm": 1.65, "actual_rainfall_mm": 1.68, "actual_temperature_c": 26.0, "actual_humidity_percent": 78, "actual_windspeed_kmh": 12.5},
        # Chaguanas weather
        {"timestamp": "04/12/2025 9:00", "sensor_id": "CR-002", "location": "Chaguanas", "predicted_rainfall_mm": 0.75, "actual_rainfall_mm": 0.72, "actual_temperature_c": 27.1, "actual_humidity_percent": 70, "actual_windspeed_kmh": 9.8},
        {"timestamp": "04/12/2025 9:01", "sensor_id": "CR-002", "location": "Chaguanas", "predicted_rainfall_mm": 1.20, "actual_rainfall_mm": 1.25, "actual_temperature_c": 26.9, "actual_humidity_percent": 82, "actual_windspeed_kmh": 13.2},
        {"timestamp": "04/12/2025 9:02", "sensor_id": "CR-002", "location": "Chaguanas", "predicted_rainfall_mm": 1.45, "actual_rainfall_mm": 1.40, "actual_temperature_c": 26.5, "actual_humidity_percent": 76, "actual_windspeed_kmh": 11.1},
        {"timestamp": "04/12/2025 9:03", "sensor_id": "CR-002", "location": "Chaguanas", "predicted_rainfall_mm": 1.58, "actual_rainfall_mm": 1.62, "actual_temperature_c": 26.3, "actual_humidity_percent": 79, "actual_windspeed_kmh": 12.8},
    ]
    
    social_data = [
        {"timestamp": "04/12/2025 9:00", "location": "St. Augustine", "post_count": 2, "sentiment_score": -0.35, "st_augustine": 2, "piarco": 1, "cunupia": 0, "st_helena": 1},
        {"timestamp": "04/12/2025 9:01", "location": "St. Augustine", "post_count": 4, "sentiment_score": -0.48, "st_augustine": 3, "piarco": 2, "cunupia": 1, "st_helena": 1},
        {"timestamp": "04/12/2025 9:02", "location": "St. Augustine", "post_count": 6, "sentiment_score": -0.58, "st_augustine": 4, "piarco": 2, "cunupia": 1, "st_helena": 2},
        {"timestamp": "04/12/2025 9:03", "location": "St. Augustine", "post_count": 8, "sentiment_score": -0.65, "st_augustine": 5, "piarco": 3, "cunupia": 2, "st_helena": 2},
        {"timestamp": "04/12/2025 9:00", "location": "Chaguanas", "post_count": 1, "sentiment_score": -0.25, "st_augustine": 0, "piarco": 1, "cunupia": 2, "st_helena": 0},
        {"timestamp": "04/12/2025 9:01", "location": "Chaguanas", "post_count": 3, "sentiment_score": -0.42, "st_augustine": 1, "piarco": 1, "cunupia": 3, "st_helena": 1},
        {"timestamp": "04/12/2025 9:02", "location": "Chaguanas", "post_count": 5, "sentiment_score": -0.52, "st_augustine": 1, "piarco": 2, "cunupia": 4, "st_helena": 1},
        {"timestamp": "04/12/2025 9:03", "location": "Chaguanas", "post_count": 7, "sentiment_score": -0.60, "st_augustine": 2, "piarco": 2, "cunupia": 5, "st_helena": 2},
    ]
    
    print(f"Loaded fallback data: {len(river_data)} river, {len(weather_data)} weather, {len(social_data)} social points")

def get_current_timestamp():
    """Get current timestamp shifted from original data"""
    global current_data_index
    elapsed_seconds = current_data_index * data_interval_seconds
    return datetime.now() - timedelta(seconds=elapsed_seconds)

def get_location_data(location: str, data_type: str):
    """Get current data point for a specific location and data type"""
    global current_data_index

    # print(f"Fetching {data_type} data for {location} at index {current_data_index}")
    
    if data_type == "river":
        location_data = [d for d in river_data if d["location"] == location]
    elif data_type == "weather":
        location_data = [d for d in weather_data if d["location"] == location]
    elif data_type == "social":
        # Social data structure is different - each record contains data for all locations
        if not social_data:
            return None
        
        # Get the current social data record
        current_social_record = social_data[current_data_index % len(social_data)]
        
        # Map location names to the social data fields
        location_mapping = {
            "St. Augustine": "st_augustine",
            "St Augustine": "st_augustine", 
            "Piarco": "piarco",
            "Cunupia": "cunupia",
            "St. Helena": "st_helena",
            "St Helena": "st_helena"
        }
        
        location_key = location_mapping.get(location)
        if not location_key:
            # If location not found in mapping, return a generic social data point
            return {
                "post_count": current_social_record.get("post_count", 0),
                "sentiment_score": current_social_record.get("sentiment_score", 0),
                "timestamp": current_social_record.get("timestamp"),
                location_key or "unknown": 0
            }
        
        # Extract relevant data for this location
        location_posts = current_social_record.get(location_key, 0)
        return {
            "timestamp": current_social_record.get("timestamp"),
            "post_count": location_posts,  # Posts specific to this location
            "sentiment_score": current_social_record.get("sentiment_score"),
            "total_post_count": current_social_record.get("post_count", 0),  # Total posts across all locations
            location_key: location_posts,
            "cunupia": current_social_record.get("cunupia", 0),
            "piarco": current_social_record.get("piarco", 0), 
            "st_augustine": current_social_record.get("st_augustine", 0),
            "st_helena": current_social_record.get("st_helena", 0)
        }
    else:
        return None
    
    if not location_data:
        return None
    
    # print(f"Found {len(location_data)} data points for {location} in {data_type}")
    
    return location_data[current_data_index % len(location_data)]

def calculate_flood_risk(river_level: float) -> str:
    """Calculate flood risk based on river level - calibrated to actual data
    
    Based on actual data analysis:
    - No flood events: 2.200m to 3.000m  
    - Flood events start: 3.000m+
    - Average flood level: 3.824m
    - Maximum recorded: 4.710m
    """
    if river_level >= 4.2:
        return "CRITICAL"    # Approaching maximum recorded levels (4.710m)
    elif river_level >= 3.6:
        return "HIGH"        # Above average flood level (3.824m) 
    elif river_level >= 3.0:
        return "MEDIUM"      # Flood threshold - where flood events begin
    elif river_level >= 2.7:
        return "ELEVATED"    # Approaching flood threshold
    else:
        return "LOW"         # Normal levels (2.200m to 2.700m)

def generate_contextual_posts(location: str, sentiment: float, conditions: dict) -> List[str]:
    """Generate contextual social media posts based on current conditions"""
    posts = []
    
    if sentiment <= -0.6:
        posts = [
            f"🚨 URGENT: Severe flooding in {location}! Multiple roads impassable",
            f"Water levels critical in {location} - emergency services on scene",
            f"AVOID {location} at all costs - dangerous flooding conditions"
        ]
    elif sentiment <= -0.5:
        posts = [
            f"⚠️ Heavy flooding reported in {location} - several roads blocked",
            f"River overflowing in {location}, water reaching residential areas",
            f"Dangerous conditions in {location} - stay indoors if possible"
        ]
    elif sentiment <= -0.4:
        posts = [
            f"Significant flooding in {location} - main roads affected",
            f"Water levels rising fast in {location}, avoid unnecessary travel",
            f"Flooding getting worse in {location}, monitoring situation"
        ]
    elif sentiment <= -0.3:
        posts = [
            f"Some flooding reported in {location} - drive with caution",
            f"Water on roads in {location}, conditions deteriorating",
            f"Heavy rain causing issues in {location}"
        ]
    else:
        posts = [
            f"Light rain in {location}, monitoring conditions",
            f"Weather looking uncertain in {location}",
            f"Keeping eye on river levels in {location}"
        ]
    
    return posts[:3]

def generate_alerts() -> List[Dict[str, str]]:
    """Generate system alerts based on current conditions"""
    alerts = []
    available_locations = list(set([d["location"] for d in river_data if "location" in d]))
    for location in available_locations:
        river_point = get_location_data(location, "river")
        if river_point:
            risk = calculate_flood_risk(river_point["river_level_m"])
            if risk in ["ELEVATED", "MEDIUM", "HIGH", "CRITICAL"]:
                alerts.append({
                    "level": risk.lower(),
                    "location": location,
                    "message": f"{risk} flood risk in {location} - River level: {river_point['river_level_m']}m",
                    "timestamp": get_current_timestamp().isoformat()
                })
    
    return alerts

# Background task to cycle through data
async def update_data_cycle():
    """Background task to cycle through data every 15 seconds"""
    global current_data_index
    while True:
        await asyncio.sleep(data_interval_seconds)
        max_points = max(len(river_data), len(weather_data), len(social_data))
        if max_points > 0:
            current_data_index = (current_data_index + 1) % max_points
        print(f"Data cycle updated: index {current_data_index}")

# API Endpoints





@app.get("/")
async def root():
    return {
        "message": "AI4SIDS Real-Time Demo API",
        "version": "2.0.0",
        "current_index": current_data_index,
        "data_points": {
            "river": len(river_data),
            "weather": len(weather_data),
            "social": len(social_data)
        }
    }

@app.get("/api/real-time/{location}")
async def get_real_time_conditions(location: str):
    """Get comprehensive real-time conditions for a location"""
    try:
        # Get current data for location
        river_point = get_location_data(location, "river")
        weather_point = get_location_data(location, "weather")
        social_point = get_location_data(location, "social")
        
        if not river_point:
            # Fallback for locations not in data
            river_point = {"river_level_m": 2.0, "change_in_level_m": 0.01, "sensor_id": "CR-999"}
        
        if not weather_point:
            weather_point = {"actual_rainfall_mm": 1.0, "actual_temperature_c": 27.0, "actual_humidity_percent": 75}
        
        if not social_point:
            social_point = {"post_count": 2, "sentiment_score": -0.3}
        
        current_time = get_current_timestamp()
        flood_risk = calculate_flood_risk(river_point["river_level_m"])
        
        # Generate contextual social posts
        posts = generate_contextual_posts(location, social_point["sentiment_score"], {
            "river_level": river_point["river_level_m"],
            "rainfall": weather_point["actual_rainfall_mm"]
        })
        
        return {
            "location": location,
            "timestamp": current_time.isoformat(),
            "river_conditions": {
                "level": river_point["river_level_m"],
                "change_rate": river_point["change_in_level_m"],
                "trend": "rising" if river_point["change_in_level_m"] > 0 else "falling" if river_point["change_in_level_m"] < 0 else "stable",
                "flood_risk": flood_risk,
                "sensor_id": river_point.get("sensor_id", "N/A")
            },
            "weather": {
                "rainfall_mm": weather_point["actual_rainfall_mm"],
                "temperature_c": weather_point["actual_temperature_c"],
                "humidity_percent": weather_point["actual_humidity_percent"],
                "rainfall_rate_hourly": weather_point["actual_rainfall_mm"] * 4  # Convert 15min to hourly
            },
            "social_activity": {
                "post_count": social_point["post_count"],
                "sentiment_score": social_point["sentiment_score"],
                "sentiment_level": "Highly Negative" if social_point["sentiment_score"] < -0.5 else "Negative" if social_point["sentiment_score"] < -0.3 else "Neutral",
                "recent_posts": posts,
                "activity_level": "HIGH" if social_point["post_count"] >= 6 else "MEDIUM" if social_point["post_count"] >= 3 else "LOW"
            },
            "insights": {
                "summary": f"{flood_risk} flood risk with {river_point['change_in_level_m']:+.3f}m/15min change",
                "recommendation": (
                    "Immediate evacuation recommended" if flood_risk == "CRITICAL" else
                    "Monitor closely and prepare to evacuate" if flood_risk == "HIGH" else
                    "Flooding likely - avoid travel and stay alert" if flood_risk == "MEDIUM" else
                    "Conditions deteriorating - monitor closely" if flood_risk == "ELEVATED" else
                    "Normal conditions - continue monitoring"
                ),
                "correlation": f"High rainfall ({weather_point['actual_rainfall_mm']}mm) correlating with {'rising' if river_point['change_in_level_m'] > 0 else 'stable'} river levels"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting real-time data: {str(e)}")

@app.get("/api/system-update")
async def get_system_update():
    """Get comprehensive system update for all locations"""
    try:
        locations_data = []
        available_locations = list(set([d["location"] for d in river_data if "location" in d]))
        # available_locations = ["St. Augustine", "Chaguanas", "Las Lomas", "Cunupia", "Caroni"]
        
        for location in available_locations:
            river_point = get_location_data(location, "river")
            if river_point:
                flood_risk = calculate_flood_risk(river_point["river_level_m"])
                locations_data.append({
                    "name": location,
                    "flood_risk": flood_risk,
                    "sensor_id": river_point.get("sensor_id", "N/A"),
                    "latitude": river_point.get("latitude", 10.6918),
                    "longitude": river_point.get("longitude", -61.2225),
                    "river_level": river_point["river_level_m"],
                    "change_rate": river_point["change_in_level_m"],
                    "current_risk": calculate_flood_risk(river_point["river_level_m"]),
                    "last_updated": get_current_timestamp().isoformat()
                })
        
        alerts = generate_alerts()
        
        return ComprehensiveUpdate(
            locations=locations_data,
            system_status={
                "active_sensors": len(set([d.get("sensor_id") for d in river_data if d.get("sensor_id")])),
                "data_cycle_progress": f"{(current_data_index / max(len(river_data), 1) * 100):.1f}%",
                "next_update_seconds": data_interval_seconds,
                "total_alerts": len(alerts)
            },
            alerts=alerts,
            timestamp=get_current_timestamp()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system update: {str(e)}")

@app.get("/api/timeline/{location}")
async def get_location_timeline(location: str, minutes: int = 5):
    """Get timeline data for location"""
    try:
        location_river_data = [d for d in river_data if d["location"] == location]
        if not location_river_data:
            raise HTTPException(status_code=404, detail=f"No data found for {location}")
        
        points_to_show = min(minutes * 4, len(location_river_data))  # 4 points per minute
        timeline = []
        
        for i in range(points_to_show):
            data_idx = (current_data_index - i) % len(location_river_data)
            point = location_river_data[data_idx]
            
            timeline.append({
                "timestamp": (get_current_timestamp() - timedelta(seconds=i * data_interval_seconds)).isoformat(),
                "river_level": point["river_level_m"],
                "change_rate": point["change_in_level_m"],
                "flood_risk": calculate_flood_risk(point["river_level_m"]),
                "minutes_ago": i // 4
            })
        
        return {
            "location": location,
            "timeline": list(reversed(timeline)),
            "summary": {
                "trend": "Rising" if timeline[0]["river_level"] > timeline[-1]["river_level"] else "Falling",
                "max_level": max(p["river_level"] for p in timeline),
                "min_level": min(p["river_level"] for p in timeline),
                "avg_change": sum(p["change_rate"] for p in timeline) / len(timeline)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting timeline: {str(e)}")

@app.get("/api/history/{location}")
async def get_location_history(location: str, points: int = 20):
    """
    Get historical data points for sparkline visualization
    Returns simplified data optimized for sparkline charts
    Default: last 20 points (last 5 minutes at 15s intervals)
    """
    try:
        # Limit points to prevent overload
        points = min(points, 100)  # Max 100 points (25 minutes)
        
        location_river_data = [d for d in river_data if d["location"] == location]
        if not location_river_data:
            raise HTTPException(status_code=404, detail=f"No data found for {location}")
        
        history = []
        for i in range(points):
            data_idx = (current_data_index - i) % len(location_river_data)
            point = location_river_data[data_idx]
            
            history.append({
                "timestamp": (get_current_timestamp() - timedelta(seconds=i * data_interval_seconds)).isoformat(),
                "value": point["river_level_m"],
                "change": point["change_in_level_m"],
            })
        
        # Reverse to get chronological order (oldest to newest)
        history = list(reversed(history))
        
        # Calculate trend indicators
        if len(history) >= 2:
            recent_avg = sum(p["value"] for p in history[-5:]) / min(5, len(history))
            older_avg = sum(p["value"] for p in history[:5]) / min(5, len(history))
            overall_trend = "rising" if recent_avg > older_avg else "falling" if recent_avg < older_avg else "stable"
            trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            overall_trend = "stable"
            trend_percentage = 0
        
        current_level = history[-1]["value"] if history else 0
        current_risk = calculate_flood_risk(current_level)
        
        return {
            "location": location,
            "current": {
                "value": current_level,
                "risk": current_risk,
                "change": history[-1]["change"] if history else 0,
                "timestamp": history[-1]["timestamp"] if history else get_current_timestamp().isoformat()
            },
            "history": history,
            "trend": {
                "direction": overall_trend,
                "percentage": round(trend_percentage, 2),
                "color": "red" if overall_trend == "rising" and current_risk in ["HIGH", "CRITICAL"] else 
                        "orange" if overall_trend == "rising" else
                        "green" if overall_trend == "falling" else
                        "blue"
            },
            "stats": {
                "max": max(p["value"] for p in history),
                "min": min(p["value"] for p in history),
                "avg": sum(p["value"] for p in history) / len(history),
                "points": len(history)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")

@app.get("/api/locations")
async def get_available_locations():
    """Get list of available locations with current status"""
    locations = []
    available_locations = list(set([d["location"] for d in river_data if "location" in d]))
    
    if not available_locations:
        available_locations = ["St. Augustine", "Chaguanas", "Las Lomas", "Cunupia", "Caroni"]
    
    for location in available_locations:
        river_point = get_location_data(location, "river")
        if river_point:
            locations.append({
                "name": location,
                "latitude": river_point.get("latitude", 10.6918),
                "longitude": river_point.get("longitude", -61.2225),
                "sensor_id": river_point.get("sensor_id", "N/A"),
                "current_risk": calculate_flood_risk(river_point["river_level_m"]),
                "has_data": True
            })
        else:
            locations.append({
                "name": location,
                "latitude": 10.6918,  # Default coordinates
                "longitude": -61.2225,
                "sensor_id": "N/A",
                "current_risk": "UNKNOWN",
                "has_data": False
            })
    
    return {"locations": locations, "total": len(locations)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)