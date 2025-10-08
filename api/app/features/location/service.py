"""
Location service - Business logic for location-related operations
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Location, RiverLevel, Weather, Social


def calculate_flood_risk(river_level: float) -> str:
    """Calculate flood risk based on river level - calibrated to actual data"""
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


def get_latest_river_data(session: Session, location_name: str) -> Optional[RiverLevel]:
    """Get latest river level data for a location"""
    location = session.query(Location).filter(Location.name == location_name).first()
    if not location:
        return None
    
    return session.query(RiverLevel)\
        .filter(RiverLevel.location_id == location.id)\
        .order_by(desc(RiverLevel.timestamp))\
        .first()


def get_latest_weather_data(session: Session, location_name: str) -> Optional[Weather]:
    """Get latest weather data for a location"""
    location = session.query(Location).filter(Location.name == location_name).first()
    if not location:
        return None
    
    return session.query(Weather)\
        .filter(Weather.location_id == location.id)\
        .order_by(desc(Weather.timestamp))\
        .first()


def get_latest_social_data(session: Session, location_name: str) -> Optional[Social]:
    """Get latest social data for a location"""
    location = session.query(Location).filter(Location.name == location_name).first()
    if not location:
        return None
    
    return session.query(Social)\
        .filter(Social.location_id == location.id)\
        .order_by(desc(Social.timestamp))\
        .first()


def get_location_history_data(session: Session, location_name: str, points: int = 20) -> List[RiverLevel]:
    """Get historical river level data for sparklines"""
    location = session.query(Location).filter(Location.name == location_name).first()
    if not location:
        return []
    
    return session.query(RiverLevel)\
        .filter(RiverLevel.location_id == location.id)\
        .order_by(desc(RiverLevel.timestamp))\
        .limit(points)\
        .all()


def get_all_locations(session: Session) -> List[Location]:
    """Get all locations from database"""
    return session.query(Location).all()


def get_location_timeline_data(session: Session, location_name: str, minutes: int = 5) -> List[RiverLevel]:
    """Get timeline data for a location"""
    location = session.query(Location).filter(Location.name == location_name).first()
    if not location:
        return []
    
    # Calculate how many points we need (4 points per minute at 15s intervals)
    points_needed = minutes * 4
    
    return session.query(RiverLevel)\
        .filter(RiverLevel.location_id == location.id)\
        .order_by(desc(RiverLevel.timestamp))\
        .limit(points_needed)\
        .all()


def generate_system_alerts(session: Session) -> List[Dict[str, str]]:
    """Generate system alerts based on current conditions"""
    alerts = []
    locations = get_all_locations(session)
    
    for location in locations:
        river_data = get_latest_river_data(session, location.name)
        if river_data:
            risk = calculate_flood_risk(river_data.river_level_m)
            if risk in ["ELEVATED", "MEDIUM", "HIGH", "CRITICAL"]:
                alerts.append({
                    "level": risk.lower(),
                    "location": location.name,
                    "message": f"{risk} flood risk in {location.name} - River level: {river_data.river_level_m}m",
                    "timestamp": datetime.now().isoformat()
                })
    
    return alerts