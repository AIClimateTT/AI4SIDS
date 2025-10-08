# AI4SIDS Forecaster Module
15-Second Cadence Real-Time Forecasting for River and Weather Data

## Overview
The `forecast_service.py` module extends the AI4SIDS Real-Time API by generating short-term predictive data for both river and weather conditions.  
It operates on live, in-memory buffers (`river_data` and `weather_data`) that are continuously updated by the simulator, and produces 30-minute forecasts at 15-second intervals.

This module is lightweight, built around NumPy and Pandas, and designed to integrate seamlessly with the existing FastAPI-based architecture.

---

## Architecture and Integration

### Data Flow
data_simulator.py ───▶ [river_data, weather_data]
│
▼
forecast_service.py
│
▼
api_v2.py (FastAPI)
│
▼
REST Endpoints for Predictions

yaml
Copy code

### Component Roles

| Component | Description |
|------------|--------------|
| **data_simulator.py** | Continuously generates new river, weather, and social data every 15 seconds. |
| **api_v2.py** | Hosts the FastAPI service that exposes real-time and playback APIs. |
| **forecast_service.py** | Reads the live data buffers, performs linear trend fitting, and projects future values for the next 30 minutes. |

---

## Installation

Ensure you have the following dependencies installed:

```bash
pip install fastapi uvicorn numpy pandas
All modules (data_simulator.py, api_v2.py, and forecast_service.py) should be located in the same project directory.

Configuration
Setting	Description	Default
DEFAULT_WINDOW_MINUTES	Duration of recent history used for model fitting.	15 minutes
DEFAULT_HORIZON_SECONDS	Total forecast duration.	1800 seconds (30 minutes)
DEFAULT_STEP_SECONDS	Time interval for each forecasted point.	15 seconds
FLOOD_THRESHOLD_M	Threshold for flood classification.	3.0 meters

File: forecast_service.py
Key Functions
Function	Description
normalize_river(records)	Standardizes river data from simulator or API sources.
normalize_weather(records)	Standardizes weather data from simulator or API sources.
predict_river(df)	Generates future river level predictions using linear regression.
predict_weather(df)	Generates future rainfall and weather metric predictions.
_fit_trend(times, values)	Fits a linear model (y = a·t + b) for short-term trend projection.
_future_times(last_ts, horizon_s, step_s)	Generates timestamps for forecast steps.

Optional utilities:

predict_from_buffers(river_data, weather_data) for direct buffer predictions.

export_predictions_to_json() for writing forecast results to JSON files.

Integration Steps
1. Import the forecaster in api_v2.py
Add these imports near the top of the file:

python
Copy code
from forecast_service import normalize_river, normalize_weather, predict_river, predict_weather
2. Add new API endpoints for forecasts
Insert the following routes into api_v2.py:

python
Copy code
@app.get("/forecast/river")
async def api_forecast_river(
    window_minutes: int = 15,
    horizon_seconds: int = 1800,
    step_seconds: int = 15
):
    df = normalize_river(river_data)
    preds = predict_river(df, window_minutes, horizon_seconds, step_seconds)
    return {
        "count": len(preds),
        "step_seconds": step_seconds,
        "horizon_seconds": horizon_seconds,
        "predictions": preds
    }

@app.get("/forecast/weather")
async def api_forecast_weather(
    window_minutes: int = 15,
    horizon_seconds: int = 1800,
    step_seconds: int = 15
):
    df = normalize_weather(weather_data)
    preds = predict_weather(df, window_minutes, horizon_seconds, step_seconds)
    return {
        "count": len(preds),
        "step_seconds": step_seconds,
        "horizon_seconds": horizon_seconds,
        "predictions": preds
    }
3. Run the API
From the project directory, run:

bash
Copy code
uvicorn enhanced_api:app --reload --port 8001
The data simulator will automatically begin populating live readings every 15 seconds, and the forecast endpoints will start producing predictive data.

Example Usage
River Forecast
Request:

bash
Copy code
GET http://localhost:8001/forecast/river
Example Response:

json
Copy code
{
  "count": 120,
  "predictions": [
    {
      "timestamp": "2025-04-12T09:15:15",
      "sensor_id": "CR-001",
      "location": "St. Augustine",
      "predicted_river_level_m": 3.45,
      "predicted_change_in_level_m": 0.02,
      "predicted_flood_event": "Yes"
    }
  ]
}
Weather Forecast
Request:

bash
Copy code
GET http://localhost:8001/forecast/weather
Response includes rainfall projections and related metrics per sensor.

Plotting Example
Example quick plot in Python:

python
Copy code
import requests, pandas as pd, matplotlib.pyplot as plt

API = "http://localhost:8001"
LOCATION = "St. Augustine"

# Forecast data
fc = requests.get(f"{API}/forecast/river").json()["predictions"]
df = pd.DataFrame([p for p in fc if p["location"] == LOCATION])
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Historical data
hist = requests.get(f"{API}/api/history/{LOCATION}", params={"points":60}).json()["history"]
hdf = pd.DataFrame(hist)
hdf["timestamp"] = pd.to_datetime(hdf["timestamp"])

# Plot
plt.figure(figsize=(10, 5))
plt.plot(hdf["timestamp"], hdf["value"], label="Observed")
plt.plot(df["timestamp"], df["predicted_river_level_m"], "--", label="Forecast")
plt.axhline(3.0, color="r", linestyle=":", label="Flood threshold")
plt.legend()
plt.title(f"River Level Forecast - {LOCATION}")
plt.tight_layout()
plt.show()
Technical Notes
Forecasts are generated via a simple linear regression fit (numpy.polyfit) over the most recent 15 minutes of data per sensor.

Results are computed independently for each sensor ID.

Forecast frequency and duration can be configured via the query parameters:

window_minutes

horizon_seconds

step_seconds

