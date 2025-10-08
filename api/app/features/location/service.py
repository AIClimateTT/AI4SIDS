"""
Location service - Business logic for location operations
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Location, RiverLevel, Weather, Social, RiverPrediction
from app.prediction_service import generate_predictions, store_predictions, get_prediction_accuracy


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


def get_data_statistics(session: Session) -> Dict[str, Any]:
    """Get statistics about the current data in the database"""
    try:
        # Count records by type
        river_count = session.query(RiverLevel).count()
        weather_count = session.query(Weather).count()
        social_count = session.query(Social).count()
        location_count = session.query(Location).count()
        
        # Get latest timestamp
        latest_river = session.query(RiverLevel).order_by(desc(RiverLevel.timestamp)).first()
        latest_timestamp = latest_river.timestamp if latest_river else None
        
        return {
            "total_locations": location_count,
            "active_locations": location_count,  # All locations are considered active
            "total_data_points": river_count + weather_count + social_count,
            "river_levels_count": river_count,
            "weather_data_count": weather_count,
            "social_posts_count": social_count,
            "latest_update": latest_timestamp.isoformat() if latest_timestamp else None
        }
    except Exception as e:
        return {
            "total_locations": 0,
            "active_locations": 0,
            "total_data_points": 0,
            "river_levels_count": 0,
            "weather_data_count": 0,
            "social_posts_count": 0,
            "latest_update": None,
            "error": str(e)
        }


def get_analytics_data(session: Session, location_id: int, hours_back: int = 24) -> Dict[str, Any]:
    """
    Get comprehensive analytics data for a location including historical trends and predictions
    """
    location = session.query(Location).filter(Location.id == location_id).first()
    if not location:
        return {}
    
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    # Get historical river level data
    historical_levels = session.query(RiverLevel).filter(
        RiverLevel.location_id == location_id,
        RiverLevel.timestamp >= cutoff_time
    ).order_by(RiverLevel.timestamp.asc()).all()
    
    # Get current predictions
    current_predictions = session.query(RiverPrediction).filter(
        RiverPrediction.location_id == location_id,
        RiverPrediction.predicted_for_time > datetime.now(),
        RiverPrediction.prediction_timestamp >= datetime.now() - timedelta(minutes=30)
    ).order_by(RiverPrediction.predicted_for_time.asc()).limit(6).all()  # Next 30 minutes
    
    # Get prediction accuracy metrics
    accuracy_stats = get_prediction_accuracy(session, location_id, hours_back=24)
    
    # Format historical data
    historical_data = [
        {
            "timestamp": level.timestamp.isoformat(),
            "river_level_m": level.river_level_m,
            "change_in_level_m": level.change_in_level_m,
            "flood_risk": calculate_flood_risk(level.river_level_m)
        }
        for level in historical_levels
    ]
    
    # Format prediction data
    prediction_data = [
        {
            "predicted_for_time": pred.predicted_for_time.isoformat(),
            "predicted_level_m": pred.predicted_level_m,
            "confidence_score": pred.confidence_score,
            "weather_influence": pred.weather_factor_influence,
            "flood_risk": calculate_flood_risk(pred.predicted_level_m)
        }
        for pred in current_predictions
    ]
    
    # Calculate summary statistics
    if historical_levels:
        levels = [level.river_level_m for level in historical_levels]
        summary_stats = {
            "min_level": min(levels),
            "max_level": max(levels),
            "avg_level": sum(levels) / len(levels),
            "current_level": levels[-1] if levels else 0,
            "trend": "rising" if len(levels) > 1 and levels[-1] > levels[-5] else "falling" if len(levels) > 1 and levels[-1] < levels[-5] else "stable"
        }
    else:
        summary_stats = {
            "min_level": 0,
            "max_level": 0,
            "avg_level": 0,
            "current_level": 0,
            "trend": "unknown"
        }
    
    return {
        "location": {
            "id": location.id,
            "name": location.name,
            "latitude": location.latitude,
            "longitude": location.longitude
        },
        "time_range": {
            "hours_back": hours_back,
            "start_time": cutoff_time.isoformat(),
            "end_time": datetime.now().isoformat()
        },
        "historical_data": historical_data,
        "predictions": prediction_data,
        "summary_stats": summary_stats,
        "accuracy_metrics": accuracy_stats,
        "data_counts": {
            "historical_points": len(historical_data),
            "prediction_points": len(prediction_data)
        }
    }


def generate_and_store_predictions(session: Session, location_id: int) -> Dict[str, Any]:
    """
    Generate new predictions for a location and store them in the database
    """
    try:
        predictions = generate_predictions(session, location_id, prediction_minutes=30)
        
        if predictions:
            store_predictions(session, location_id, predictions)
            return {
                "success": True,
                "predictions_generated": len(predictions),
                "message": f"Generated {len(predictions)} predictions for location {location_id}"
            }
        else:
            return {
                "success": False,
                "predictions_generated": 0,
                "message": "Insufficient data to generate predictions"
            }
    except Exception as e:
        return {
            "success": False,
            "predictions_generated": 0,
            "message": f"Error generating predictions: {str(e)}"
        }