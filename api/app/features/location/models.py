"""
Pydantic models for location feature
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional


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


class LocationHistoryPoint(BaseModel):
    timestamp: str
    value: float
    change: float


class LocationHistory(BaseModel):
    location: str
    current: Dict[str, Any]
    history: List[LocationHistoryPoint]
    trend: Dict[str, Any]
    stats: Dict[str, Any]


class LocationTimeline(BaseModel):
    location: str
    timeline: List[Dict[str, Any]]
    summary: Dict[str, Any]


class LocationsResponse(BaseModel):
    locations: List[Dict[str, Any]]
    total: int