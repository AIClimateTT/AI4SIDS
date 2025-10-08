# enhanced_api.py - FastAPI with Advanced Playback Controls and Time Manipulation
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
import os
from contextlib import asynccontextmanager
from enum import Enum
import math
from api.app.data_simulator import generate_realtime_data, river_data, weather_data, social_data

from api.app.data_simulator import generate_realtime_data

class PlaybackState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"

class PlaybackController:
    """Advanced playback controller for time-series data manipulation"""
    
    def __init__(self):
        self.state = PlaybackState.STOPPED
        self.speed = 1.0  # 1x normal speed
        self.virtual_index = 0
        self.virtual_start_time = datetime.now()
        self.paused_time = None
        self.loop_enabled = False
        self.loop_start = None
        self.loop_end = None
        self.bookmarks = {}  # Named bookmarks for quick navigation
        self.events = []     # Detected significant events
        
    def play(self, speed: float = None):
        """Start or resume playback"""
        if speed is not None:
            self.speed = speed
            
        if self.state == PlaybackState.PAUSED and self.paused_time:
            # Resume from pause - adjust virtual start time
            elapsed_real = (datetime.now() - self.paused_time).total_seconds()
            self.virtual_start_time = datetime.now() - timedelta(seconds=self.virtual_index * 15 / self.speed)
        else:
            # Start fresh
            self.virtual_start_time = datetime.now()
            
        self.state = PlaybackState.PLAYING
        self.paused_time = None
        
    def pause(self):
        """Pause playback"""
        if self.state == PlaybackState.PLAYING:
            self.state = PlaybackState.PAUSED
            self.paused_time = datetime.now()
            
    def stop(self):
        """Stop playback and reset to beginning"""
        self.state = PlaybackState.STOPPED
        self.virtual_index = 0
        self.paused_time = None
        
    def seek(self, index: int):
        """Seek to specific data point"""
        self.virtual_index = max(0, index)
        if self.state == PlaybackState.PLAYING:
            # Adjust virtual start time for new position
            self.virtual_start_time = datetime.now() - timedelta(seconds=self.virtual_index * 15 / self.speed)
        
    def seek_to_time(self, target_time: str):
        """Seek to specific timestamp (ISO format)"""
        # Convert target time to data index
        # This would need the actual data timestamps to calculate properly
        # For now, using a simple approach
        pass
        
    def get_current_index(self, max_data_points: int) -> int:
        """Calculate current data index based on virtual time"""
        if self.state == PlaybackState.STOPPED:
            return 0
        elif self.state == PlaybackState.PAUSED:
            return min(self.virtual_index, max_data_points - 1)
        elif self.state == PlaybackState.PLAYING:
            # Calculate elapsed virtual time
            elapsed_real = (datetime.now() - self.virtual_start_time).total_seconds()
            elapsed_virtual = elapsed_real * self.speed
            new_index = int(elapsed_virtual / 15)  # 15 seconds per data point
            
            # Handle looping
            if self.loop_enabled and self.loop_start is not None and self.loop_end is not None:
                loop_length = self.loop_end - self.loop_start
                if new_index >= self.loop_end:
                    new_index = self.loop_start + ((new_index - self.loop_start) % loop_length)
            else:
                # Stop at end of data
                if new_index >= max_data_points:
                    self.state = PlaybackState.STOPPED
                    new_index = max_data_points - 1
                    
            self.virtual_index = new_index
            return new_index
        
        return 0
        
    def set_loop(self, start_index: int, end_index: int):
        """Set loop points"""
        self.loop_start = start_index
        self.loop_end = end_index
        self.loop_enabled = True
        
    def disable_loop(self):
        """Disable looping"""
        self.loop_enabled = False
        
    def add_bookmark(self, name: str, index: int):
        """Add a bookmark at specific index"""
        self.bookmarks[name] = index
        
    def jump_to_bookmark(self, name: str):
        """Jump to a named bookmark"""
        if name in self.bookmarks:
            self.seek(self.bookmarks[name])
            
    def get_status(self, max_data_points: int) -> Dict[str, Any]:
        """Get current playback status"""
        current_idx = self.get_current_index(max_data_points)
        progress = (current_idx / max(max_data_points - 1, 1)) * 100
        
        return {
            "state": self.state.value,
            "speed": self.speed,
            "current_index": current_idx,
            "progress_percent": round(progress, 1),
            "total_points": max_data_points,
            "loop_enabled": self.loop_enabled,
            "loop_start": self.loop_start,
            "loop_end": self.loop_end,
            "bookmarks": self.bookmarks,
            "virtual_time": self.get_virtual_timestamp().isoformat() if max_data_points > 0 else None
        }
        
    def get_virtual_timestamp(self) -> datetime:
        """Get the current virtual timestamp"""
        # Base timestamp + (current_index * 15 seconds)
        base = datetime(2025, 4, 12, 9, 0, 0)
        return base + timedelta(seconds=self.virtual_index * 15)

class EventDetector:
    """Detect significant events in the time-series data"""
    
    @staticmethod
    def detect_flood_events(river_data: List[Dict]) -> List[Dict]:
        """Detect flood threshold crossings and peaks"""
        events = []
        locations = set(d.get("location") for d in river_data)

        for location in locations:
            if not location:
                continue
                
            location_data = [d for d in river_data if d.get("location") == location]
            location_data.sort(key=lambda x: x.get("timestamp", ""))

            for i, point in enumerate(location_data):
                level = point.get("river_level_m", 0)
                
                # Flood threshold crossing (3.0m)
                if i > 0:
                    prev_level = location_data[i-1].get("river_level_m", 0)
                    if prev_level < 3.0 <= level:
                        events.append({
                            "type": "flood_threshold_crossed",
                            "location": location,
                            "index": i,
                            "timestamp": point.get("timestamp"),
                            "level": level,
                            "severity": "medium",
                            "description": f"Flood threshold crossed in {location} (3.0m)"
                        })
                        
                # Critical level (4.2m)
                if level >= 4.2:
                    events.append({
                        "type": "critical_level",
                        "location": location,
                        "index": i,
                        "timestamp": point.get("timestamp"),
                        "level": level,
                        "severity": "critical",
                        "description": f"Critical flood level in {location} ({level}m)"
                    })
                    
                # Peak detection (local maximum)
                if i > 0 and i < len(location_data) - 1:
                    prev_level = location_data[i-1].get("river_level_m", 0)
                    next_level = location_data[i+1].get("river_level_m", 0)
                    if level > prev_level and level > next_level and level > 2.5:
                        events.append({
                            "type": "peak",
                            "location": location,
                            "index": i,
                            "timestamp": point.get("timestamp"),
                            "level": level,
                            "severity": "low" if level < 3.0 else "medium" if level < 4.0 else "high",
                            "description": f"Peak water level in {location} ({level}m)"
                        })
        
        return sorted(events, key=lambda x: x["index"])
    
    @staticmethod
    def detect_weather_events(weather_data: List[Dict]) -> List[Dict]:
        """Detect significant weather events"""
        events = []
        locations = set(d.get("location") for d in weather_data)
        
        for location in locations:
            if not location:
                continue
                
            location_data = [d for d in weather_data if d.get("location") == location]
            
            for i, point in enumerate(location_data):
                rainfall = point.get("actual_rainfall_mm", 0)
                
                # Heavy rainfall events
                if rainfall > 1.5:
                    events.append({
                        "type": "heavy_rainfall",
                        "location": location,
                        "index": i,
                        "timestamp": point.get("timestamp"),
                        "rainfall": rainfall,
                        "severity": "medium" if rainfall < 2.0 else "high",
                        "description": f"Heavy rainfall in {location} ({rainfall}mm)"
                    })
        
        return events

# Global variables
playback_controller = PlaybackController()
# river_data = []
# weather_data = []
# social_data = []
detected_events = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data and prepare event detection"""
    global detected_events
    asyncio.create_task(generate_realtime_data())
    await asyncio.sleep(3)
    # load_data_from_json()

    # Detect events in the data
    river_events = EventDetector.detect_flood_events(river_data)
    weather_events = EventDetector.detect_weather_events(weather_data)
    detected_events = river_events + weather_events
    
    # Create automatic bookmarks for significant events
    for event in detected_events:
        if event["severity"] in ["high", "critical"]:
            bookmark_name = f"{event['type']}_{event['location']}_{event['index']}"
            playback_controller.add_bookmark(bookmark_name, event["index"])
    
    print(f"AI4SIDS Enhanced API started - Detected {len(detected_events)} events")
    yield

app = FastAPI(
    title="AI4SIDS Enhanced Time-Series Playback API", 
    version="3.0.0", 
    lifespan=lifespan,
    description="Advanced playback controls for time-series flood monitoring data"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced data models
class PlaybackControlRequest(BaseModel):
    action: str  # "play", "pause", "stop", "seek"
    speed: Optional[float] = None
    index: Optional[int] = None
    timestamp: Optional[str] = None

class LoopRequest(BaseModel):
    start_index: int
    end_index: int

class BookmarkRequest(BaseModel):
    name: str
    index: Optional[int] = None  # If None, use current position

class TimelineResponse(BaseModel):
    total_points: int
    duration_minutes: float
    events: List[Dict[str, Any]]
    bookmarks: Dict[str, int]
    data_summary: Dict[str, Any]

# Data loading functions (copied from main.py)
def load_data_from_json():
    """Load data from JSON files or fallback to sample data"""
    global river_data, weather_data, social_data
    
    try:
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
        load_fallback_data()

def load_fallback_data():
    """Load extended fallback sample data for demo"""
    global river_data, weather_data, social_data
    
    # Generate more comprehensive sample data for better demo
    river_data = []
    weather_data = []
    social_data = []
    
    locations = [
        {"name": "St. Augustine", "id": "CR-001", "lat": 10.6406, "lng": -61.3994},
        {"name": "Chaguanas", "id": "CR-002", "lat": 10.5168, "lng": -61.4107},
        {"name": "Cunupia", "id": "CR-003", "lat": 10.5833, "lng": -61.3833},
        {"name": "Caroni", "id": "CR-004", "lat": 10.6500, "lng": -61.3667}
    ]
    
    # Generate 2 hours of data (480 points) with 15-second intervals
    base_time = datetime(2025, 4, 12, 9, 0, 0)
    
    for i in range(480):  # 2 hours = 120 minutes = 480 points (15-second intervals)
        timestamp = base_time + timedelta(seconds=i * 15)
        timestamp_str = timestamp.strftime("%m/%d/%Y %H:%M")
        
        for j, loc in enumerate(locations):
            # Simulate realistic flood progression
            time_factor = i / 480  # 0 to 1 progression
            
            # Different flood scenarios per location
            if loc["name"] == "St. Augustine":
                # Gradual flood development
                base_level = 2.2 + (time_factor * 2.5)  # 2.2m to 4.7m
                noise = 0.05 * math.sin(i * 0.1)  # Small variations
                river_level = base_level + noise
                change_rate = 0.01 + (time_factor * 0.08)  # Increasing change rate
            
            elif loc["name"] == "Chaguanas":
                # Rapid rise then stabilize
                if time_factor < 0.3:
                    river_level = 1.8 + (time_factor * 8)  # Rapid rise
                    change_rate = 0.1
                else:
                    river_level = 4.2 + 0.2 * math.sin(i * 0.05)  # Stabilize high
                    change_rate = 0.01
                    
            elif loc["name"] == "Cunupia":
                # Moderate steady rise
                river_level = 2.0 + (time_factor * 1.8)  # 2.0m to 3.8m
                change_rate = 0.02 + (time_factor * 0.03)
                
            else:  # Caroni
                # Late onset flood
                if time_factor < 0.6:
                    river_level = 2.1 + (time_factor * 0.8)  # Slow start
                    change_rate = 0.008
                else:
                    rapid_factor = (time_factor - 0.6) / 0.4
                    river_level = 2.58 + (rapid_factor * 2.2)  # Rapid late rise
                    change_rate = 0.05
            
            # Add river data
            river_data.append({
                "timestamp": timestamp_str,
                "sensor_id": loc["id"],
                "latitude": loc["lat"],
                "longitude": loc["lng"],
                "location": loc["name"],
                "river_level_m": round(river_level, 3),
                "change_in_level_m": round(change_rate, 3)
            })
            
            # Add weather data
            base_rainfall = 0.5 + (time_factor * 2.0)  # Increasing rainfall
            rainfall_spike = 0.3 * math.sin(i * 0.2) if time_factor > 0.3 else 0
            actual_rainfall = max(0, base_rainfall + rainfall_spike)
            
            weather_data.append({
                "timestamp": timestamp_str,
                "sensor_id": loc["id"],
                "location": loc["name"],
                "predicted_rainfall_mm": round(actual_rainfall * 0.95, 2),
                "actual_rainfall_mm": round(actual_rainfall, 2),
                "actual_temperature_c": round(26.5 + 1.5 * math.sin(i * 0.1), 1),
                "actual_humidity_percent": round(70 + 15 * time_factor, 1),
                "actual_windspeed_kmh": round(10 + 5 * math.sin(i * 0.15), 1)
            })
    
    # Generate social data (simplified)
    for i in range(480):
        timestamp = base_time + timedelta(seconds=i * 15)
        timestamp_str = timestamp.strftime("%m/%d/%Y %H:%M")
        time_factor = i / 480
        
        post_count = max(1, int(2 + time_factor * 12))  # Increasing social activity
        sentiment = -0.2 - (time_factor * 0.6)  # Increasingly negative
        
        social_data.append({
            "timestamp": timestamp_str,
            "location": "General",
            "post_count": post_count,
            "sentiment_score": round(sentiment, 2),
            "st_augustine": max(0, int(post_count * 0.4)),
            "chaguanas": max(0, int(post_count * 0.3)),
            "cunupia": max(0, int(post_count * 0.2)),
            "caroni": max(0, int(post_count * 0.1))
        })
    
    print(f"Generated sample data: {len(river_data)} river, {len(weather_data)} weather, {len(social_data)} social points")

def calculate_flood_risk(river_level: float) -> str:
    """Calculate flood risk based on river level"""
    if river_level >= 4.2:
        return "CRITICAL"
    elif river_level >= 3.6:
        return "HIGH"
    elif river_level >= 3.0:
        return "MEDIUM"
    elif river_level >= 2.7:
        return "ELEVATED"
    else:
        return "LOW"

def get_location_data_at_index(location: str, data_type: str, index: int):
    """Get data for a specific location at a specific index"""
    if data_type == "river":
        location_data = [d for d in river_data if d.get("location") == location]
    elif data_type == "weather":
        location_data = [d for d in weather_data if d.get("location") == location]
    elif data_type == "social":
        if index < len(social_data):
            return social_data[index]
        return None
    else:
        return None
    
    if not location_data or index >= len(location_data):
        return None
    
    return location_data[index % len(location_data)]

# New Enhanced API Endpoints

@app.get("/")
async def root():
    return {
        "message": "AI4SIDS Enhanced Time-Series Playback API",
        "version": "3.0.0",
        "features": [
            "Advanced playback controls (play/pause/stop/seek)",
            "Variable speed playback (0.1x to 10x)",
            "Event detection and smart navigation",
            "Bookmarking and looping",
            "Timeline scrubbing and visualization"
        ],
        "playback_status": playback_controller.get_status(len(river_data)),
        "detected_events": len(detected_events),
        "data_points": {
            "river": len(river_data),
            "weather": len(weather_data),
            "social": len(social_data)
        }
    }

@app.post("/api/playback/control")
async def control_playback(request: PlaybackControlRequest):
    """Control playback state and navigation"""
    try:
        if request.action == "play":
            playback_controller.play(request.speed)
        elif request.action == "pause":
            playback_controller.pause()
        elif request.action == "stop":
            playback_controller.stop()
        elif request.action == "seek":
            if request.index is not None:
                playback_controller.seek(request.index)
            elif request.timestamp:
                playback_controller.seek_to_time(request.timestamp)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        return {
            "success": True,
            "action": request.action,
            "status": playback_controller.get_status(len(river_data))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Playback control error: {str(e)}")

@app.get("/api/playback/status")
async def get_playback_status():
    """Get current playback status"""
    return playback_controller.get_status(len(river_data))

@app.get("/api/playback/timeline", response_model=TimelineResponse)
async def get_timeline():
    """Get timeline metadata including events and bookmarks"""
    total_points = max(len(river_data), len(weather_data), len(social_data))
    duration_minutes = (total_points * 15) / 60  # 15 seconds per point
    
    # Calculate data summary
    locations = list(set(d.get("location") for d in river_data if d.get("location")))
    summary = {
        "locations": locations,
        "total_duration_minutes": round(duration_minutes, 1),
        "data_interval_seconds": 15,
        "flood_events": len([e for e in detected_events if e["type"] in ["flood_threshold_crossed", "critical_level"]]),
        "weather_events": len([e for e in detected_events if e["type"] == "heavy_rainfall"])
    }
    
    return TimelineResponse(
        total_points=total_points,
        duration_minutes=duration_minutes,
        events=detected_events,
        bookmarks=playback_controller.bookmarks,
        data_summary=summary
    )

@app.post("/api/playback/loop")
async def set_loop(request: LoopRequest):
    """Set loop points for repeated playback"""
    playback_controller.set_loop(request.start_index, request.end_index)
    return {
        "success": True,
        "loop_start": request.start_index,
        "loop_end": request.end_index,
        "status": playback_controller.get_status(len(river_data))
    }

@app.delete("/api/playback/loop")
async def disable_loop():
    """Disable looping"""
    playback_controller.disable_loop()
    return {"success": True, "loop_disabled": True}

@app.post("/api/playback/bookmark")
async def add_bookmark(request: BookmarkRequest):
    """Add a bookmark at current or specified position"""
    index = request.index if request.index is not None else playback_controller.virtual_index
    playback_controller.add_bookmark(request.name, index)
    return {
        "success": True,
        "bookmark": request.name,
        "index": index
    }

@app.post("/api/playback/bookmark/{name}/jump")
async def jump_to_bookmark(name: str):
    """Jump to a named bookmark"""
    if name not in playback_controller.bookmarks:
        raise HTTPException(status_code=404, detail=f"Bookmark '{name}' not found")
    
    playback_controller.jump_to_bookmark(name)
    return {
        "success": True,
        "jumped_to": name,
        "index": playback_controller.bookmarks[name],
        "status": playback_controller.get_status(len(river_data))
    }

@app.get("/api/events")
async def get_detected_events():
    """Get all detected events with filtering options"""
    return {
        "events": detected_events,
        "summary": {
            "total": len(detected_events),
            "by_type": {},
            "by_severity": {},
            "by_location": {}
        }
    }

@app.get("/api/data/range/{start_index}/{end_index}")
async def get_data_range(start_index: int, end_index: int, location: Optional[str] = None):
    """Get data for a specific range of indices"""
    try:
        end_index = min(end_index, len(river_data) - 1)
        start_index = max(0, start_index)
        
        if location:
            locations = [location]
        else:
            locations = list(set(d.get("location") for d in river_data if d.get("location")))
        
        result = []
        for i in range(start_index, end_index + 1):
            timestamp = datetime(2025, 4, 12, 9, 0, 0) + timedelta(seconds=i * 15)
            
            for loc in locations:
                river_point = get_location_data_at_index(loc, "river", i)
                weather_point = get_location_data_at_index(loc, "weather", i)
                
                if river_point:
                    result.append({
                        "index": i,
                        "timestamp": timestamp.isoformat(),
                        "location": loc,
                        "river_level": river_point.get("river_level_m"),
                        "change_rate": river_point.get("change_in_level_m"),
                        "flood_risk": calculate_flood_risk(river_point.get("river_level_m", 0)),
                        "rainfall": weather_point.get("actual_rainfall_mm", 0) if weather_point else 0
                    })
        
        return {
            "range": f"{start_index}-{end_index}",
            "data": result,
            "total_points": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting data range: {str(e)}")

# Enhanced versions of original endpoints that work with playback controller
@app.get("/api/system-update")
async def get_system_update():
    """Get system update using current playback position"""
    try:
        current_index = playback_controller.get_current_index(len(river_data))
        locations_data = []
        
        available_locations = list(set([d["location"] for d in river_data if "location" in d]))
        
        for location in available_locations:
            river_point = get_location_data_at_index(location, "river", current_index)
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
                    "current_risk": flood_risk,
                    "last_updated": playback_controller.get_virtual_timestamp().isoformat()
                })
        
        # Generate alerts based on current data
        alerts = []
        for location_data in locations_data:
            if location_data["flood_risk"] in ["ELEVATED", "MEDIUM", "HIGH", "CRITICAL"]:
                alerts.append({
                    "level": location_data["flood_risk"].lower(),
                    "location": location_data["name"],
                    "message": f"{location_data['flood_risk']} flood risk in {location_data['name']} - River level: {location_data['river_level']}m",
                    "timestamp": location_data["last_updated"]
                })
        
        return {
            "locations": locations_data,
            "system_status": {
                "active_sensors": len(set([d.get("sensor_id") for d in river_data if d.get("sensor_id")])),
                "data_cycle_progress": f"{playback_controller.get_status(len(river_data))['progress_percent']:.1f}%",
                "playback_state": playback_controller.state.value,
                "playback_speed": f"{playback_controller.speed}x",
                "total_alerts": len(alerts),
                "virtual_time": playback_controller.get_virtual_timestamp().isoformat()
            },
            "alerts": alerts,
            "timestamp": playback_controller.get_virtual_timestamp(),
            "playback_info": playback_controller.get_status(len(river_data))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system update: {str(e)}")

@app.get("/api/real-time/{location}")
async def get_real_time_conditions(location: str):
    """Get real-time conditions using current playback position"""
    try:
        current_index = playback_controller.get_current_index(len(river_data))
        
        river_point = get_location_data_at_index(location, "river", current_index)
        weather_point = get_location_data_at_index(location, "weather", current_index)
        social_point = get_location_data_at_index(location, "social", current_index)
        
        if not river_point:
            river_point = {"river_level_m": 2.0, "change_in_level_m": 0.01, "sensor_id": "CR-999"}
        
        if not weather_point:
            weather_point = {"actual_rainfall_mm": 1.0, "actual_temperature_c": 27.0, "actual_humidity_percent": 75}
        
        if not social_point:
            social_point = {"post_count": 2, "sentiment_score": -0.3}
        
        current_time = playback_controller.get_virtual_timestamp()
        flood_risk = calculate_flood_risk(river_point["river_level_m"])
        
        return {
            "location": location,
            "timestamp": current_time.isoformat(),
            "playback_index": current_index,
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
                "rainfall_rate_hourly": weather_point["actual_rainfall_mm"] * 4
            },
            "social_activity": {
                "post_count": social_point["post_count"],
                "sentiment_score": social_point["sentiment_score"],
                "sentiment_level": "Highly Negative" if social_point["sentiment_score"] < -0.5 else "Negative" if social_point["sentiment_score"] < -0.3 else "Neutral",
                "activity_level": "HIGH" if social_point["post_count"] >= 6 else "MEDIUM" if social_point["post_count"] >= 3 else "LOW"
            },
            "playback_info": playback_controller.get_status(len(river_data))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting real-time data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)  # Different port to avoid conflicts
