"""
Prediction service modules
"""
from app.features.predictions.service.enhanced import (
    generate_predictions,
    store_predictions,
    get_prediction_accuracy,
    cleanup_old_predictions,
    generate_enhanced_predictions,
    store_enhanced_predictions,
    get_enhanced_prediction_accuracy,
    generate_week_forecast_for_location,
    store_week_forecast,
    get_stored_week_forecast
)

from app.features.predictions.service.forecast import (
    normalize_river,
    normalize_weather,
    predict_river,
    predict_weather,
    predict_from_buffers,
    FLOOD_THRESHOLD_M
)

__all__ = [
    # Enhanced prediction service
    "generate_predictions",
    "store_predictions",
    "get_prediction_accuracy",
    "cleanup_old_predictions",
    "generate_enhanced_predictions",
    "store_enhanced_predictions",
    "get_enhanced_prediction_accuracy",
    "generate_week_forecast_for_location",
    "store_week_forecast",
    "get_stored_week_forecast",
    # Forecast service
    "normalize_river",
    "normalize_weather",
    "predict_river",
    "predict_weather",
    "predict_from_buffers",
    "FLOOD_THRESHOLD_M"
]
