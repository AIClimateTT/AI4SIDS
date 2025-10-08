"""
Location routes/controller - API endpoints for location-related operations
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List

from app.core.db import SessionDep
from app.features.location.models import (
    RealTimeConditions, ComprehensiveUpdate, LocationHistory, 
    LocationTimeline, LocationsResponse
)
from app.features.location.service import (
    get_latest_river_data, get_latest_weather_data, get_latest_social_data,
    get_location_history_data, get_all_locations, get_location_timeline_data,
    generate_system_alerts, calculate_flood_risk, generate_contextual_posts
)

router = APIRouter(prefix="/api", tags=["locations"])


@router.get("/real-time/{location}")
async def get_real_time_conditions(location: str, session: SessionDep):
    """Get comprehensive real-time conditions for a location"""
    try:
        # Get current data for location
        river_point = get_latest_river_data(session, location)
        weather_point = get_latest_weather_data(session, location)
        social_point = get_latest_social_data(session, location)
        
        if not river_point:
            raise HTTPException(status_code=404, detail=f"No river data found for {location}")
        
        current_time = datetime.now()
        flood_risk = calculate_flood_risk(river_point.river_level_m)
        
        # Generate contextual social posts
        sentiment_score = social_point.sentiment_score if social_point else -0.3
        posts = generate_contextual_posts(location, sentiment_score, {
            "river_level": river_point.river_level_m,
            "rainfall": weather_point.actual_rainfall_mm if weather_point else 1.0
        })
        
        return {
            "location": location,
            "timestamp": current_time.isoformat(),
            "river_conditions": {
                "level": river_point.river_level_m,
                "change_rate": river_point.change_in_level_m,
                "trend": "rising" if river_point.change_in_level_m > 0 else "falling" if river_point.change_in_level_m < 0 else "stable",
                "flood_risk": flood_risk,
                "sensor_id": river_point.location.sensor_id
            },
            "weather": {
                "rainfall_mm": weather_point.actual_rainfall_mm if weather_point else 1.0,
                "temperature_c": weather_point.actual_temperature_c if weather_point else 27.0,
                "humidity_percent": weather_point.actual_humidity_percent if weather_point else 75,
                "rainfall_rate_hourly": (weather_point.actual_rainfall_mm * 4) if weather_point else 4.0
            },
            "social_activity": {
                "post_count": social_point.post_count if social_point else 2,
                "sentiment_score": sentiment_score,
                "sentiment_level": "Highly Negative" if sentiment_score < -0.5 else "Negative" if sentiment_score < -0.3 else "Neutral",
                "recent_posts": posts,
                "activity_level": "HIGH" if (social_point and social_point.post_count >= 6) else "MEDIUM" if (social_point and social_point.post_count >= 3) else "LOW"
            },
            "insights": {
                "summary": f"{flood_risk} flood risk with {river_point.change_in_level_m:+.3f}m/15min change",
                "recommendation": (
                    "Immediate evacuation recommended" if flood_risk == "CRITICAL" else
                    "Monitor closely and prepare to evacuate" if flood_risk == "HIGH" else
                    "Flooding likely - avoid travel and stay alert" if flood_risk == "MEDIUM" else
                    "Conditions deteriorating - monitor closely" if flood_risk == "ELEVATED" else
                    "Normal conditions - continue monitoring"
                ),
                "correlation": f"High rainfall ({weather_point.actual_rainfall_mm if weather_point else 1.0}mm) correlating with {'rising' if river_point.change_in_level_m > 0 else 'stable'} river levels"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting real-time data: {str(e)}")


@router.get("/system-update")
async def get_system_update(session: SessionDep):
    """Get comprehensive system update for all locations"""
    try:
        locations_data = []
        locations = get_all_locations(session)
        
        for location in locations:
            river_point = get_latest_river_data(session, location.name)
            if river_point:
                flood_risk = calculate_flood_risk(river_point.river_level_m)
                locations_data.append({
                    "name": location.name,
                    "flood_risk": flood_risk,
                    "sensor_id": location.sensor_id,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "river_level": river_point.river_level_m,
                    "change_rate": river_point.change_in_level_m,
                    "current_risk": flood_risk,
                    "last_updated": datetime.now().isoformat()
                })
        
        alerts = generate_system_alerts(session)
        
        return ComprehensiveUpdate(
            locations=locations_data,
            system_status={
                "active_sensors": len(locations),
                "data_cycle_progress": "100%",
                "next_update_seconds": 15,
                "total_alerts": len(alerts)
            },
            alerts=alerts,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system update: {str(e)}")


@router.get("/timeline/{location}")
async def get_location_timeline(location: str, session: SessionDep, minutes: int = 5):
    """Get timeline data for location"""
    try:
        timeline_data = get_location_timeline_data(session, location, minutes)
        if not timeline_data:
            raise HTTPException(status_code=404, detail=f"No data found for {location}")
        
        timeline = []
        
        for i, point in enumerate(reversed(timeline_data)):
            timeline.append({
                "timestamp": point.timestamp.isoformat(),
                "river_level": point.river_level_m,
                "change_rate": point.change_in_level_m,
                "flood_risk": calculate_flood_risk(point.river_level_m),
                "minutes_ago": i // 4
            })
        
        return LocationTimeline(
            location=location,
            timeline=timeline,
            summary={
                "trend": "Rising" if timeline[0]["river_level"] < timeline[-1]["river_level"] else "Falling",
                "max_level": max(p["river_level"] for p in timeline),
                "min_level": min(p["river_level"] for p in timeline),
                "avg_change": sum(p["change_rate"] for p in timeline) / len(timeline)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting timeline: {str(e)}")


@router.get("/history/{location}")
async def get_location_history(location: str, session: SessionDep, points: int = 20):
    """Get historical data points for sparkline visualization"""
    try:
        # Limit points to prevent overload
        points = min(points, 100)
        
        history_data = get_location_history_data(session, location, points)
        if not history_data:
            raise HTTPException(status_code=404, detail=f"No data found for {location}")
        
        # Convert to sparkline format (oldest to newest)
        history = []
        for point in reversed(history_data):
            history.append({
                "timestamp": point.timestamp.isoformat(),
                "value": point.river_level_m,
                "change": point.change_in_level_m,
            })
        
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
        
        return LocationHistory(
            location=location,
            current={
                "value": current_level,
                "risk": current_risk,
                "change": history[-1]["change"] if history else 0,
                "timestamp": history[-1]["timestamp"] if history else datetime.now().isoformat()
            },
            history=history,
            trend={
                "direction": overall_trend,
                "percentage": round(trend_percentage, 2),
                "color": "red" if overall_trend == "rising" and current_risk in ["HIGH", "CRITICAL"] else 
                        "orange" if overall_trend == "rising" else
                        "green" if overall_trend == "falling" else
                        "blue"
            },
            stats={
                "max": max(p["value"] for p in history),
                "min": min(p["value"] for p in history),
                "avg": sum(p["value"] for p in history) / len(history),
                "points": len(history)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


@router.get("/locations")
async def get_available_locations(session: SessionDep):
    """Get list of available locations with current status"""
    try:
        locations = get_all_locations(session)
        locations_data = []
        
        for location in locations:
            river_point = get_latest_river_data(session, location.name)
            current_risk = calculate_flood_risk(river_point.river_level_m) if river_point else "UNKNOWN"
            
            locations_data.append({
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "sensor_id": location.sensor_id,
                "current_risk": current_risk,
                "has_data": river_point is not None
            })
        
        return LocationsResponse(locations=locations_data, total=len(locations_data))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting locations: {str(e)}")