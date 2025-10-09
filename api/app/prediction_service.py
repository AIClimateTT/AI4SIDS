"""
Prediction service - Comprehensive river level and weather forecasting
Integrates the robust forecast_service.py with database models
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Location, RiverLevel, Weather, RiverPrediction

# Configuration from forecast_service
FLOOD_THRESHOLD_M = 3.0          # flood onset threshold
DEFAULT_HORIZON_SECONDS = 1800   # 30 minutes
DEFAULT_STEP_SECONDS = 15        # 15s cadence
DEFAULT_WINDOW_MINUTES = 15      # history window per sensor

# Simulator timestamp format
GEN_TS_FMT = "%m/%d/%Y %I:%M:%S %p"


# -------------------------------------------------------------------
# Parsing / coercion helpers (from forecast_service)
# -------------------------------------------------------------------
def _to_dt(ts: Any) -> Optional[datetime]:
    """Robust timestamp parser that tolerates your CSV and simulator formats."""
    if isinstance(ts, datetime):
        return ts
    s = str(ts)
    # Try common formats first
    for fmt in (
        GEN_TS_FMT,                   # "09/30/2025 03:15:12 PM"
        "%m/%d/%Y %H:%M",            # "04/12/2025 09:03"  (fallback samples)
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    # Last resort: pandas
    try:
        dt = pd.to_datetime(s, errors="coerce")
        return None if pd.isna(dt) else dt.to_pydatetime()
    except Exception:
        return None


def _coerce_float(x: Any, default: float = np.nan) -> float:
    try:
        v = float(x)
        if np.isfinite(v):
            return v
        return default
    except Exception:
        return default


def _latest_nonnull(series: pd.Series, default=None):
    if series is None or series.empty:
        return default
    s = series.dropna()
    return s.iloc[-1] if not s.empty else default


# -------------------------------------------------------------------
# Forecast core (from forecast_service)
# -------------------------------------------------------------------
def _fit_trend(times: List[datetime], values: List[float]) -> Tuple[float, float]:
    """
    Fit y ~ a*t + b where t is seconds since first sample.
    Returns (a = slope per second, b = intercept).
    Falls back to flat at last value if insufficient data.
    """
    if len(times) < 3 or len(values) < 3:
        last = values[-1] if values else 0.0
        return 0.0, last

    t0 = times[0]
    x = np.array([(t - t0).total_seconds() for t in times], dtype=float)
    y = np.array(values, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 3:
        return 0.0, (y[-1] if len(y) else 0.0)

    a, b = np.polyfit(x, y, 1)
    return float(a), float(b)


def _future_times(last_ts: datetime, horizon_s: int, step_s: int) -> List[datetime]:
    return [last_ts + timedelta(seconds=i) for i in range(step_s, horizon_s + step_s, step_s)]


# -------------------------------------------------------------------
# Database integration functions
# -------------------------------------------------------------------
def load_historical_data(session: Session, location_id: int, window_minutes: int = DEFAULT_WINDOW_MINUTES) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load historical river and weather data from database"""
    cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
    
    # Load river data
    river_data = session.query(RiverLevel).filter(
        RiverLevel.location_id == location_id,
        RiverLevel.timestamp >= cutoff_time
    ).order_by(RiverLevel.timestamp.asc()).all()
    
    # Load weather data
    weather_data = session.query(Weather).filter(
        Weather.location_id == location_id,
        Weather.timestamp >= cutoff_time
    ).order_by(Weather.timestamp.asc()).all()
    
    # Convert to DataFrames in forecast_service format
    river_records = []
    for r in river_data:
        river_records.append({
            "timestamp": r.timestamp,
            "sensor_id": f"river_{location_id}",
            "latitude": getattr(r.location, 'latitude', None),
            "longitude": getattr(r.location, 'longitude', None),
            "location": getattr(r.location, 'name', f"Location {location_id}"),
            "river_level_m": r.river_level_m,
            "change_in_level_m": r.change_in_level_m or 0.0
        })
    
    weather_records = []
    for w in weather_data:
        weather_records.append({
            "timestamp": w.timestamp,
            "sensor_id": f"weather_{location_id}",
            "latitude": getattr(w.location, 'latitude', None),
            "longitude": getattr(w.location, 'longitude', None),
            "location": getattr(w.location, 'name', f"Location {location_id}"),
            "actual_rainfall_mm": w.actual_rainfall_mm or 0.0,
            "actual_windspeed_kmh": w.actual_windspeed_kmh or 0.0,
            "actual_temperature_c": w.actual_temperature_c or 20.0,
            "actual_humidity_percent": w.actual_humidity_percent or 50.0,
            "actual_storm": "Yes" if w.actual_storm else "No"
        })
    
    # Normalize data using forecast_service functions
    river_df = normalize_river_data(river_records)
    weather_df = normalize_weather_data(weather_records)
    
    return river_df, weather_df


def normalize_river_data(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Normalize river data to forecast_service format"""
    cols = ["dt","sensor_id","latitude","longitude","location","river_level_m","change_in_level_m"]
    if not records:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(records).copy()
    df["dt"] = pd.to_datetime(df["timestamp"])
    df["river_level_m"] = pd.to_numeric(df["river_level_m"], errors="coerce")
    df["change_in_level_m"] = pd.to_numeric(df["change_in_level_m"], errors="coerce")
    
    out = df[["dt","sensor_id","latitude","longitude","location","river_level_m","change_in_level_m"]]
    out = out.dropna(subset=["dt","sensor_id","river_level_m"])
    return out.sort_values("dt")


def normalize_weather_data(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Normalize weather data to forecast_service format"""
    cols = [
        "dt","sensor_id","latitude","longitude","location",
        "actual_rainfall_mm","actual_windspeed_kmh","actual_temperature_c","actual_humidity_percent","actual_storm"
    ]
    if not records:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(records).copy()
    df["dt"] = pd.to_datetime(df["timestamp"])
    df["actual_rainfall_mm"] = pd.to_numeric(df["actual_rainfall_mm"], errors="coerce")
    df["actual_windspeed_kmh"] = pd.to_numeric(df["actual_windspeed_kmh"], errors="coerce")
    df["actual_temperature_c"] = pd.to_numeric(df["actual_temperature_c"], errors="coerce")
    df["actual_humidity_percent"] = pd.to_numeric(df["actual_humidity_percent"], errors="coerce")
    
    out = df[[
        "dt","sensor_id","latitude","longitude","location",
        "actual_rainfall_mm","actual_windspeed_kmh","actual_temperature_c","actual_humidity_percent","actual_storm"
    ]]
    out = out.dropna(subset=["dt","sensor_id"])
    return out.sort_values("dt")


def predict_river_levels(
    df: pd.DataFrame,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    horizon_s: int = DEFAULT_HORIZON_SECONDS,
    step_s: int = DEFAULT_STEP_SECONDS,
) -> List[Dict[str, Any]]:
    """
    Forecast river level for each sensor for the next horizon at given cadence.
    Enhanced version from forecast_service.py
    """
    preds: List[Dict[str, Any]] = []
    if df.empty:
        return preds

    for sid, g in df.groupby("sensor_id"):
        g = g.sort_values("dt")
        last_ts = g["dt"].iloc[-1]
        cutoff = last_ts - timedelta(minutes=window_minutes)
        gw = g[g["dt"] >= cutoff]
        if gw.empty:
            continue

        times = gw["dt"].tolist()
        values = gw["river_level_m"].astype(float).tolist()
        a, b = _fit_trend(times, values)  # slope per second

        lat = _latest_nonnull(g["latitude"])
        lon = _latest_nonnull(g["longitude"])
        loc = _latest_nonnull(g["location"])
        t0 = times[0]
        fts = _future_times(last_ts, horizon_s, step_s)

        # gentle inertia toward last observed change
        last_delta = values[-1] - values[-2] if len(values) >= 2 else 0.0

        for ts in fts:
            sec = (ts - t0).total_seconds()
            lvl = a * sec + b + 0.1 * last_delta
            lvl = max(float(lvl), 0.0)
            flood = "Yes" if lvl >= FLOOD_THRESHOLD_M else "No"

            preds.append({
                "timestamp": ts,
                "predicted_level_m": round(lvl, 3),
                "predicted_change_in_level_m": round(a * step_s, 3),
                "predicted_flood_event": flood,
                "latitude": _coerce_float(lat, None),
                "longitude": _coerce_float(lon, None),
                "location": loc,
            })
    return preds


def calculate_linear_trend(data_points: List[float], timestamps: List[datetime]) -> Tuple[float, float]:
    """
    Calculate linear trend (slope and intercept) from data points
    Returns: (slope_per_minute, intercept)
    """
    if len(data_points) < 2:
        return 0.0, data_points[0] if data_points else 2.0
    
    # Convert timestamps to minutes from first timestamp
    base_time = timestamps[0]
    x_values = [(ts - base_time).total_seconds() / 60 for ts in timestamps]
    y_values = data_points
    
    # Simple linear regression
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    
    # Calculate slope and intercept
    denominator = n * sum_x2 - sum_x * sum_x
    if denominator == 0:
        slope = 0
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator
    
    intercept = (sum_y - slope * sum_x) / n
    
    return slope, intercept


def calculate_weather_influence(session: Session, location_id: int, minutes_back: int = 60) -> float:
    """
    Calculate weather influence factor based on recent rainfall
    Returns multiplier (0.0 to 2.0) where 1.0 = no influence
    """
    cutoff_time = datetime.now() - timedelta(minutes=minutes_back)
    
    recent_weather = session.query(Weather).filter(
        Weather.location_id == location_id,
        Weather.timestamp >= cutoff_time
    ).order_by(desc(Weather.timestamp)).limit(12).all()  # Last 12 readings (3 hours)
    
    if not recent_weather:
        return 1.0
    
    # Calculate average rainfall and create influence factor
    avg_rainfall = sum(w.actual_rainfall_mm for w in recent_weather) / len(recent_weather)
    
    # Influence factor: more rain = higher river levels predicted
    # 0mm rain = 1.0x, 1mm rain = 1.1x, 3mm rain = 1.3x, 5mm+ rain = 1.5x
    influence_factor = 1.0 + min(avg_rainfall * 0.1, 0.5)
    
    return influence_factor


def generate_predictions(session: Session, location_id: int, prediction_minutes: int = 30) -> List[Dict]:
    """
    Generate comprehensive river level predictions using enhanced forecast algorithms
    """
    # Load historical data from database
    river_df, weather_df = load_historical_data(session, location_id, DEFAULT_WINDOW_MINUTES)
    
    if river_df.empty:
        return []
    
    # Use enhanced prediction algorithm
    horizon_seconds = prediction_minutes * 60
    river_predictions = predict_river_levels(
        river_df,
        window_minutes=DEFAULT_WINDOW_MINUTES,
        horizon_s=horizon_seconds,
        step_s=DEFAULT_STEP_SECONDS
    )
    
    # Calculate weather influence factor
    weather_factor = calculate_weather_influence_enhanced(weather_df)
    
    # Convert predictions to database format
    predictions = []
    current_time = datetime.now()
    
    for pred in river_predictions:
        # Calculate confidence based on data consistency and time horizon
        minutes_ahead = (pred["timestamp"] - current_time).total_seconds() / 60
        base_confidence = calculate_prediction_confidence(river_df, weather_df)
        time_decay = max(0.3, 1.0 - (minutes_ahead / prediction_minutes) * 0.3)
        confidence = base_confidence * time_decay
        
        # Apply weather influence to prediction
        weather_influence = (weather_factor - 1.0) * (minutes_ahead / 30.0)
        adjusted_level = pred["predicted_level_m"] + weather_influence
        adjusted_level = max(0.0, min(adjusted_level, 6.0))  # Realistic bounds
        
        predictions.append({
            "prediction_timestamp": current_time,
            "predicted_for_time": pred["timestamp"],
            "predicted_level_m": round(adjusted_level, 3),
            "confidence_score": round(confidence, 3),
            "weather_factor_influence": round(weather_influence, 3)
        })
    
    return predictions


def calculate_weather_influence_enhanced(weather_df: pd.DataFrame) -> float:
    """
    Enhanced weather influence calculation using multiple factors
    """
    if weather_df.empty:
        return 1.0
    
    # Get recent weather data
    recent_data = weather_df.tail(12)  # Last 12 readings
    
    # Calculate rainfall influence
    avg_rainfall = recent_data["actual_rainfall_mm"].mean()
    rainfall_factor = 1.0 + min(avg_rainfall * 0.1, 0.5)
    
    # Calculate wind influence (higher wind can increase evaporation)
    avg_windspeed = recent_data["actual_windspeed_kmh"].mean()
    wind_factor = max(0.95, 1.0 - (avg_windspeed / 100) * 0.05)
    
    # Storm influence
    storm_count = (recent_data["actual_storm"] == "Yes").sum()
    storm_factor = 1.0 + (storm_count / len(recent_data)) * 0.2
    
    # Combined influence
    combined_factor = rainfall_factor * wind_factor * storm_factor
    return min(combined_factor, 2.0)  # Cap at 2x influence


def calculate_prediction_confidence(river_df: pd.DataFrame, weather_df: pd.DataFrame) -> float:
    """
    Calculate prediction confidence based on data quality and consistency
    """
    if river_df.empty:
        return 0.3
    
    # Data availability factor
    data_points = len(river_df)
    availability_factor = min(1.0, data_points / 10)  # 10 points = full confidence
    
    # Data consistency factor (low volatility = high confidence)
    level_changes = river_df["change_in_level_m"].abs()
    avg_volatility = level_changes.mean() if not level_changes.empty else 0.1
    consistency_factor = max(0.3, 1.0 - min(avg_volatility * 2, 0.7))
    
    # Weather data availability
    weather_factor = 1.0 if not weather_df.empty else 0.8
    
    base_confidence = availability_factor * consistency_factor * weather_factor
    return max(0.3, min(0.95, base_confidence))


def store_predictions(session: Session, location_id: int, predictions: List[Dict]) -> None:
    """Store predictions in database"""
    for pred_data in predictions:
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


def cleanup_old_predictions(session: Session, hours_to_keep: int = 48) -> None:
    """Remove old predictions to keep database clean"""
    cutoff_time = datetime.now() - timedelta(hours=hours_to_keep)
    
    session.query(RiverPrediction).filter(
        RiverPrediction.prediction_timestamp < cutoff_time
    ).delete()
    
    session.commit()


def get_prediction_accuracy(session: Session, location_id: int, hours_back: int = 24) -> Dict:
    """
    Calculate how accurate recent predictions were
    Compare predictions made in the past with actual values
    """
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    # Get predictions made in the past that we can now validate
    past_predictions = session.query(RiverPrediction).filter(
        RiverPrediction.location_id == location_id,
        RiverPrediction.prediction_timestamp >= cutoff_time,
        RiverPrediction.predicted_for_time <= datetime.now()  # Predictions for times that have passed
    ).all()
    
    if not past_predictions:
        return {"accuracy_percentage": 0, "average_error": 0, "total_predictions": 0}
    
    total_error = 0
    accurate_predictions = 0
    
    for prediction in past_predictions:
        # Find actual value closest to predicted time
        actual_data = session.query(RiverLevel).filter(
            RiverLevel.location_id == location_id,
            RiverLevel.timestamp <= prediction.predicted_for_time + timedelta(minutes=3),
            RiverLevel.timestamp >= prediction.predicted_for_time - timedelta(minutes=3)
        ).order_by(RiverLevel.timestamp.desc()).first()
        
        if actual_data:
            error = abs(prediction.predicted_level_m - actual_data.river_level_m)
            total_error += error
            
            # Consider prediction "accurate" if within 10cm
            if error <= 0.1:
                accurate_predictions += 1
    
    accuracy_percentage = (accurate_predictions / len(past_predictions)) * 100
    average_error = total_error / len(past_predictions)
    
    return {
        "accuracy_percentage": round(accuracy_percentage, 1),
        "average_error": round(average_error, 3),
        "total_predictions": len(past_predictions),
        "accurate_predictions": accurate_predictions
    }