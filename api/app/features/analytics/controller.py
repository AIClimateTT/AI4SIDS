"""
Analytics controller - API endpoints for location analytics and predictions
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.db import SessionDep
from app.features.location.service import get_analytics_data, generate_and_store_predictions
from app.models import Location


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/{location_id}")
async def get_location_analytics(
    location_id: int,
    session: SessionDep,
    hours_back: int = Query(default=24, ge=1, le=168, description="Hours of historical data to include (1-168)")
) -> Dict[str, Any]:
    """
    Get comprehensive analytics data for a specific location
    
    Returns:
    - Historical river level data for the specified time period
    - Current predictions for the next 30 minutes
    - Summary statistics (min, max, average levels, trend)
    - Prediction accuracy metrics
    """
    # Verify location exists
    location = session.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")
    
    analytics_data = get_analytics_data(session, location_id, hours_back)
    
    if not analytics_data:
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics data")
    
    return analytics_data


@router.get("/by-name/{location_name}")
async def get_location_analytics_by_name(
    location_name: str,
    session: SessionDep,
    hours_back: int = Query(default=24, ge=1, le=168, description="Hours of historical data to include (1-168)")
) -> Dict[str, Any]:
    """
    Get comprehensive analytics data for a specific location by name
    
    Returns:
    - Historical river level data for the specified time period
    - Current predictions for the next 30 minutes
    - Summary statistics (min, max, average levels, trend)
    - Prediction accuracy metrics
    """
    # Find location by name
    location = session.query(Location).filter(Location.name == location_name).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
    
    analytics_data = get_analytics_data(session, location.id, hours_back)
    
    if not analytics_data:
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics data")
    
    return analytics_data


@router.post("/{location_id}/predictions")
async def generate_predictions(
    location_id: int,
    session: SessionDep
) -> Dict[str, Any]:
    """
    Generate new predictions for a specific location
    
    This endpoint triggers the prediction algorithm to generate
    new forecasts for the next 30 minutes based on current conditions.
    """
    # Verify location exists
    location = session.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")
    
    result = generate_and_store_predictions(session, location_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/by-name/{location_name}/predictions")
async def generate_predictions_by_name(
    location_name: str,
    session: SessionDep
) -> Dict[str, Any]:
    """
    Generate new predictions for a specific location by name
    
    This endpoint triggers the prediction algorithm to generate
    new forecasts for the next 30 minutes based on current conditions.
    """
    # Find location by name
    location = session.query(Location).filter(Location.name == location_name).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
    
    result = generate_and_store_predictions(session, location.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/")
async def get_all_locations_summary(
    session: SessionDep
) -> Dict[str, Any]:
    """
    Get analytics summary for all locations
    
    Returns basic analytics data for all locations to help users
    choose which location to analyze in detail.
    """
    locations = session.query(Location).all()
    
    summary_data = []
    for location in locations:
        # Get basic analytics for each location (last 6 hours only for summary)
        analytics = get_analytics_data(session, location.id, hours_back=6)
        
        if analytics:
            summary_data.append({
                "location_id": location.id,
                "location_name": location.name,
                "current_level": analytics["summary_stats"]["current_level"],
                "trend": analytics["summary_stats"]["trend"],
                "flood_risk": analytics["historical_data"][-1]["flood_risk"] if analytics["historical_data"] else "UNKNOWN",
                "data_points": analytics["data_counts"]["historical_points"],
                "predictions_available": analytics["data_counts"]["prediction_points"] > 0,
                "prediction_accuracy": analytics["accuracy_metrics"]["accuracy_percentage"]
            })
    
    return {
        "locations_count": len(locations),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "locations_summary": summary_data
    }