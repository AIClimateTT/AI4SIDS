"""
Enhanced Prediction Service - Combining robust forecasting with database integration
Merges the comprehensive approach from forecast_service.py with database integration
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Location, RiverLevel, Weather, RiverPrediction, WeekForecast


# Configuration constants
FLOOD_THRESHOLD_M = 3.0
DEFAULT_HORIZON_SECONDS = 1800  # 30 minutes
DEFAULT_STEP_SECONDS = 15       # 15-second cadence (vs my original 5-minute)
DEFAULT_WINDOW_MINUTES = 15     # history window per sensor


def _to_float(x: Any, default: float = np.nan) -> float:
    """Robust float conversion"""
    try:
        v = float(x)
        return v if np.isfinite(v) else default
    except (ValueError, TypeError):
        return default


def _fit_trend_robust(times: List[datetime], values: List[float]) -> Tuple[float, float]:
    """
    Enhanced trend fitting using numpy (more robust than my original)
    Returns (slope_per_second, intercept)
    """
    if len(times) < 2 or len(values) < 2:
        last_val = values[-1] if values else 2.0
        return 0.0, last_val
    
    # Convert to seconds since first timestamp (like your approach)
    t0 = times[0]
    x = np.array([(t - t0).total_seconds() for t in times])
    y = np.array(values)
    
    # Filter out invalid values
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    
    if len(x) < 2:
        return 0.0, (y[-1] if len(y) > 0 else 2.0)
    
    # Use numpy's polyfit for better numerical stability
    try:
        slope, intercept = np.polyfit(x, y, 1)
        return float(slope), float(intercept)
    except np.linalg.LinAlgError:
        return 0.0, float(y[-1]) if len(y) > 0 else 2.0


def normalize_river_from_db(river_records: List[RiverLevel]) -> pd.DataFrame:
    """
    Convert SQLAlchemy RiverLevel objects to normalized DataFrame
    Compatible with your normalize_river function structure
    """
    if not river_records:
        return pd.DataFrame(columns=['dt', 'sensor_id', 'latitude', 'longitude', 'location', 'river_level_m', 'change_in_level_m'])
    
    data = []
    for record in river_records:
        # Ensure timestamp is timezone-aware (SQLite returns naive datetimes)
        timestamp = record.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        data.append({
            'dt': timestamp,
            'sensor_id': record.location.sensor_id if record.location else None,
            'latitude': record.location.latitude if record.location else None,
            'longitude': record.location.longitude if record.location else None,
            'location': record.location.name if record.location else None,
            'river_level_m': record.river_level_m,
            'change_in_level_m': record.change_in_level_m
        })
    
    df = pd.DataFrame(data)
    df['river_level_m'] = pd.to_numeric(df['river_level_m'], errors='coerce')
    df['change_in_level_m'] = pd.to_numeric(df['change_in_level_m'], errors='coerce')
    
    return df.dropna(subset=['dt', 'river_level_m']).sort_values('dt')


def normalize_weather_from_db(weather_records: List[Weather]) -> pd.DataFrame:
    """
    Convert SQLAlchemy Weather objects to normalized DataFrame
    """
    if not weather_records:
        return pd.DataFrame(columns=['dt', 'sensor_id', 'latitude', 'longitude', 'location', 
                                   'actual_rainfall_mm', 'actual_windspeed_kmh', 
                                   'actual_temperature_c', 'actual_humidity_percent'])
    
    data = []
    for record in weather_records:
        # Ensure timestamp is timezone-aware (SQLite returns naive datetimes)
        timestamp = record.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        data.append({
            'dt': timestamp,
            'sensor_id': record.location.sensor_id if record.location else None,
            'latitude': record.location.latitude if record.location else None,
            'longitude': record.location.longitude if record.location else None,
            'location': record.location.name if record.location else None,
            'actual_rainfall_mm': record.actual_rainfall_mm,
            'actual_windspeed_kmh': record.actual_windspeed_kmh,
            'actual_temperature_c': record.actual_temperature_c,
            'actual_humidity_percent': record.actual_humidity_percent
        })
    
    df = pd.DataFrame(data)
    for col in ['actual_rainfall_mm', 'actual_windspeed_kmh', 'actual_temperature_c', 'actual_humidity_percent']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df.dropna(subset=['dt']).sort_values('dt')


def calculate_enhanced_weather_influence(weather_df: pd.DataFrame, location_name: str) -> float:
    """
    Enhanced weather influence calculation using your approach but with database data
    """
    if weather_df.empty:
        return 1.0
    
    location_weather = weather_df[weather_df['location'] == location_name]
    if location_weather.empty:
        return 1.0
    
    # Get recent data (last hour)
    recent_weather = location_weather.tail(12)  # Last 12 readings
    
    if recent_weather.empty:
        return 1.0
    
    # Enhanced influence calculation
    avg_rainfall = recent_weather['actual_rainfall_mm'].mean()
    avg_windspeed = recent_weather['actual_windspeed_kmh'].mean()
    
    # More sophisticated influence factor
    rainfall_factor = 1.0 + min(avg_rainfall * 0.1, 0.5)  # Your original approach
    wind_factor = 1.0 + min(avg_windspeed * 0.01, 0.2)    # Additional wind influence
    
    combined_factor = (rainfall_factor + wind_factor) / 2
    return combined_factor


def generate_enhanced_predictions(session: Session, location_id: int, 
                                horizon_seconds: int = DEFAULT_HORIZON_SECONDS,
                                step_seconds: int = DEFAULT_STEP_SECONDS,
                                window_minutes: int = DEFAULT_WINDOW_MINUTES) -> List[Dict]:
    """
    Enhanced prediction generation combining both approaches
    """
    # Get location info
    location = session.query(Location).filter(Location.id == location_id).first()
    if not location:
        return []
    
    # Get recent river data (your improved approach with configurable window)
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    
    river_data = session.query(RiverLevel).filter(
        RiverLevel.location_id == location_id,
        RiverLevel.timestamp >= cutoff_time
    ).order_by(RiverLevel.timestamp.asc()).all()
    
    if len(river_data) < 3:
        return []
    
    # Get weather data for influence calculation
    weather_data = session.query(Weather).filter(
        Weather.location_id == location_id,
        Weather.timestamp >= cutoff_time
    ).order_by(Weather.timestamp.asc()).all()
    
    # Normalize to DataFrames (your approach)
    river_df = normalize_river_from_db(river_data)
    weather_df = normalize_weather_from_db(weather_data)
    
    if river_df.empty:
        return []
    
    # Extract data for trend calculation
    times = river_df['dt'].tolist()
    levels = river_df['river_level_m'].tolist()
    
    # Use enhanced trend fitting (your numpy approach)
    slope_per_second, intercept = _fit_trend_robust(times, levels)
    
    # Enhanced weather influence
    weather_factor = calculate_enhanced_weather_influence(weather_df, location.name)
    
    # Calculate confidence (my approach with your data consistency idea)
    recent_changes = river_df['change_in_level_m'].tail(5).abs()
    avg_volatility = recent_changes.mean() if not recent_changes.empty else 0.1
    base_confidence = max(0.3, min(0.95, 1.0 - avg_volatility * 2))
    
    # Generate predictions at your 15-second cadence
    predictions = []
    current_time = datetime.now(timezone.utc)
    latest_level = levels[-1]
    t0 = times[0]
    
    # Calculate number of steps (your approach)
    num_steps = horizon_seconds // step_seconds
    
    for i in range(1, num_steps + 1):
        prediction_time = current_time + timedelta(seconds=i * step_seconds)
        seconds_ahead = i * step_seconds
        
        # Base prediction from enhanced trend
        seconds_from_start = (prediction_time - t0).total_seconds()
        predicted_level = slope_per_second * seconds_from_start + intercept
        
        # Apply weather influence (scaled over time)
        weather_influence = (weather_factor - 1.0) * (seconds_ahead / horizon_seconds)
        predicted_level = predicted_level + weather_influence
        
        # Add slight inertia from recent change (your approach)
        if len(levels) >= 2:
            recent_delta = levels[-1] - levels[-2]
            predicted_level += 0.1 * recent_delta
        
        # Ensure realistic bounds
        predicted_level = max(0.0, min(predicted_level, 6.0))
        
        # Time-decay confidence
        time_confidence = base_confidence * (1.0 - (seconds_ahead / horizon_seconds) * 0.3)
        
        # Flood classification (your approach)
        flood_event = "Yes" if predicted_level >= FLOOD_THRESHOLD_M else "No"
        
        predictions.append({
            "prediction_timestamp": current_time,
            "predicted_for_time": prediction_time,
            "predicted_level_m": round(predicted_level, 3),
            "confidence_score": round(time_confidence, 3),
            "weather_factor_influence": round(weather_influence, 3),
            "predicted_flood_event": flood_event,
            "time_sensor_id": f"{prediction_time.strftime('%Y-%m-%d %H:%M:%S')}-{location.sensor_id}",
            "sensor_id": location.sensor_id,
            "location": location.name,
            "latitude": location.latitude,
            "longitude": location.longitude
        })
    
    return predictions


def store_enhanced_predictions(session: Session, location_id: int, predictions: List[Dict]) -> None:
    """Enhanced prediction storage with additional metadata"""
    for pred_data in predictions:
        # Check if prediction already exists (avoid duplicates)
        existing = session.query(RiverPrediction).filter(
            RiverPrediction.location_id == location_id,
            RiverPrediction.predicted_for_time == pred_data["predicted_for_time"],
            RiverPrediction.prediction_timestamp >= datetime.now(timezone.utc) - timedelta(minutes=5)
        ).first()
        
        if not existing:
            prediction = RiverPrediction(
                location_id=location_id,
                prediction_timestamp=pred_data["prediction_timestamp"],
                predicted_for_time=pred_data["predicted_for_time"],
                predicted_level_m=pred_data["predicted_level_m"],
                confidence_score=pred_data["confidence_score"],
                weather_factor_influence=pred_data["weather_factor_influence"]
            )
            session.add(prediction)
    
    session.commit()


def get_enhanced_prediction_accuracy(session: Session, location_id: int, hours_back: int = 24) -> Dict:
    """
    Enhanced accuracy calculation with more detailed metrics
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    
    # Get predictions that can be validated
    past_predictions = session.query(RiverPrediction).filter(
        RiverPrediction.location_id == location_id,
        RiverPrediction.prediction_timestamp >= cutoff_time,
        RiverPrediction.predicted_for_time <= datetime.now(timezone.utc)
    ).all()
    
    if not past_predictions:
        return {
            "accuracy_percentage": 0,
            "average_error": 0,
            "total_predictions": 0,
            "accurate_predictions": 0,
            "rmse": 0,
            "mae": 0
        }
    
    errors = []
    accurate_count = 0
    
    for prediction in past_predictions:
        # Ensure predicted_for_time is timezone-aware (SQLite returns naive datetimes)
        predicted_time = prediction.predicted_for_time
        if predicted_time.tzinfo is None:
            predicted_time = predicted_time.replace(tzinfo=timezone.utc)
        
        # Find closest actual value
        actual_data = session.query(RiverLevel).filter(
            RiverLevel.location_id == location_id,
            RiverLevel.timestamp <= predicted_time + timedelta(minutes=2),
            RiverLevel.timestamp >= predicted_time - timedelta(minutes=2)
        ).order_by(RiverLevel.timestamp.desc()).first()
        
        if actual_data:
            error = abs(prediction.predicted_level_m - actual_data.river_level_m)
            errors.append(error)
            
            # Accurate if within 10cm
            if error <= 0.1:
                accurate_count += 1
    
    if not errors:
        return {
            "accuracy_percentage": 0,
            "average_error": 0,
            "total_predictions": len(past_predictions),
            "accurate_predictions": 0,
            "rmse": 0,
            "mae": 0
        }
    
    accuracy_percentage = (accurate_count / len(errors)) * 100
    mae = np.mean(errors)  # Mean Absolute Error
    rmse = np.sqrt(np.mean([e**2 for e in errors]))  # Root Mean Square Error
    
    return {
        "accuracy_percentage": round(accuracy_percentage, 1),
        "average_error": round(mae, 3),
        "total_predictions": len(past_predictions),
        "accurate_predictions": accurate_count,
        "rmse": round(rmse, 3),
        "mae": round(mae, 3)
    }


# Export the main functions for use in the analytics service
def generate_predictions(session: Session, location_id: int, prediction_minutes: int = 30) -> List[Dict]:
    """
    Wrapper function to maintain compatibility with existing analytics service
    Converts prediction_minutes to seconds for the enhanced function
    """
    horizon_seconds = prediction_minutes * 60
    return generate_enhanced_predictions(session, location_id, horizon_seconds)


def store_predictions(session: Session, location_id: int, predictions: List[Dict]) -> None:
    """Wrapper to maintain compatibility"""
    return store_enhanced_predictions(session, location_id, predictions)


def get_prediction_accuracy(session: Session, location_id: int, hours_back: int = 24) -> Dict:
    """Wrapper to maintain compatibility"""
    return get_enhanced_prediction_accuracy(session, location_id, hours_back)


def cleanup_old_predictions(session: Session, hours_to_keep: int = 48) -> None:
    """Remove old predictions to keep database clean"""
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_to_keep)
    
    session.query(RiverPrediction).filter(
        RiverPrediction.prediction_timestamp < cutoff_time
    ).delete()
    
    session.commit()

def generate_week_forecast_for_location(
    session: Session,
    location_id: int,
    base_daily_mm: float,
    start_date: Optional[datetime] = None,
    base_conf: float = 0.9,
    sentiment: float = 0.0,
) -> Any:
    location = session.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise ValueError(f"Location id {location_id} not found")

    if start_date is None:
        start_date = datetime.now(timezone.utc)
    elif start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    forecast_resp = simulate_7_day_forecast(
        base_daily_mm=base_daily_mm,
        base_conf=base_conf,
        sentiment=sentiment,
        days=7,
        start_date=start_date,
        location=location.name,
        baseline={"source": "simulator", "location_id": location_id, "base_daily_mm": base_daily_mm}
    )
    return forecast_resp

def store_week_forecast(session: Session, forecast_response: Any) -> None:
    location_name = forecast_response.location
    gen_at = forecast_response.generated_at

    # best-effort: try to resolve location_id but upsert keys by (location, date) — name-based
    loc = session.query(Location).filter(Location.name == location_name).first()
    location_id = loc.id if loc else None

    for day in forecast_response.forecast:
        day_date = day.date.date() if hasattr(day.date, "date") else day.date

        existing = session.query(WeekForecast).filter(
            WeekForecast.location == location_name,
            WeekForecast.date == day_date
        ).first()

        if existing:
            existing.generated_at = gen_at
            existing.rainfall_mm = int(day.rainfall_mm)
            existing.risk = day.risk
            existing.confidence = float(day.confidence)
            existing.meta = forecast_response.baseline
        else:
            new_row = WeekForecast(
                location=location_name,
                date=day_date,
                generated_at=gen_at,
                rainfall_mm=int(day.rainfall_mm),
                risk=day.risk,
                confidence=float(day.confidence),
                meta=forecast_response.baseline
            )
            session.add(new_row)

    session.commit()

def get_stored_week_forecast(session: Session, location_id: int, since_days: int = 14) -> List[Dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    location = session.query(Location).filter(Location.id == location_id).first()
    if not location:
        return []

    rows = session.query(WeekForecast).filter(
        WeekForecast.location == location.name,
        WeekForecast.generated_at >= cutoff
    ).order_by(WeekForecast.date.asc()).all()

    # if your WeekForecast model has to_dict(), use it; otherwise build dicts inline:
    result = []
    for r in rows:
        item = {
            "id": getattr(r, "id", None),
            "location": getattr(r, "location", None),
            "date": getattr(r, "date").isoformat() if getattr(r, "date", None) is not None else None,
            "generated_at": getattr(r, "generated_at").isoformat() if getattr(r, "generated_at", None) is not None else None,
            "rainfall_mm": getattr(r, "rainfall_mm", None),
            "risk": getattr(r, "risk", None),
            "confidence": getattr(r, "confidence", None),
            "meta": getattr(r, "meta", None),
        }
        result.append(item)

    return result
