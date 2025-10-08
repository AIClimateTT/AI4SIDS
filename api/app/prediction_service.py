"""
Prediction service - Simple river level prediction based on historical data and weather
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Location, RiverLevel, Weather, RiverPrediction


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
    Generate river level predictions for the next X minutes
    Uses linear trend + weather influence
    """
    # Get recent river level data (last 2 hours for trend calculation)
    cutoff_time = datetime.now() - timedelta(hours=2)
    
    historical_data = session.query(RiverLevel).filter(
        RiverLevel.location_id == location_id,
        RiverLevel.timestamp >= cutoff_time
    ).order_by(RiverLevel.timestamp.asc()).all()
    
    if len(historical_data) < 3:
        return []  # Need at least 3 points for meaningful prediction
    
    # Extract data for trend calculation
    levels = [point.river_level_m for point in historical_data]
    timestamps = [point.timestamp for point in historical_data]
    
    # Calculate linear trend
    slope, intercept = calculate_linear_trend(levels, timestamps)
    
    # Get weather influence
    weather_factor = calculate_weather_influence(session, location_id)
    
    # Calculate confidence based on data consistency
    # More consistent data = higher confidence
    recent_changes = [abs(historical_data[i].change_in_level_m) for i in range(-5, 0) if i + len(historical_data) >= 0]
    avg_volatility = sum(recent_changes) / len(recent_changes) if recent_changes else 0.1
    confidence = max(0.3, min(0.95, 1.0 - avg_volatility * 2))  # Scale volatility to confidence
    
    # Generate predictions every 5 minutes
    predictions = []
    current_time = datetime.now()
    latest_level = levels[-1]
    
    for i in range(1, (prediction_minutes // 5) + 1):
        prediction_time = current_time + timedelta(minutes=i * 5)
        minutes_ahead = i * 5
        
        # Base prediction from linear trend
        predicted_level = latest_level + (slope * minutes_ahead)
        
        # Apply weather influence
        weather_influence = (weather_factor - 1.0) * (minutes_ahead / 30.0)  # Scale influence over time
        predicted_level = predicted_level + weather_influence
        
        # Ensure realistic bounds (never negative, reasonable max)
        predicted_level = max(0.0, min(predicted_level, 6.0))
        
        # Decrease confidence slightly for further predictions
        time_confidence = confidence * (1.0 - (minutes_ahead / prediction_minutes) * 0.2)
        
        predictions.append({
            "prediction_timestamp": current_time,
            "predicted_for_time": prediction_time,
            "predicted_level_m": round(predicted_level, 3),
            "confidence_score": round(time_confidence, 3),
            "weather_factor_influence": round(weather_influence, 3)
        })
    
    return predictions


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