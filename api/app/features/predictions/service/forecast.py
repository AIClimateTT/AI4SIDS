# 15-second cadence forecasting for river & weather

from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
FLOOD_THRESHOLD_M = 3.0          # flood onset threshold
DEFAULT_HORIZON_SECONDS = 1800   # 30 minutes
DEFAULT_STEP_SECONDS = 15        # 15s cadence
DEFAULT_WINDOW_MINUTES = 15      # history window per sensor

# Simulator timestamp format ("MM/DD/YYYY hh:mm:ss AM/PM")
GEN_TS_FMT = "%m/%d/%Y %I:%M:%S %p"


# -------------------------------------------------------------------
# Parsing / coercion helpers
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
# Normalizers (accept CSV loader schema AND simulator schema)
# -------------------------------------------------------------------
def normalize_river(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Returns canonical columns:
      dt, sensor_id, latitude, longitude, location, river_level_m, change_in_level_m
    Accepts:
      - CSV loader keys: "Timestamp", "Sensor ID", "River Level (m)", "Change in Level (m)"
      - Simulator keys:  "timestamp", "sensor_id", "river_level_m", "level_delta"
    """
    cols = ["dt","sensor_id","latitude","longitude","location","river_level_m","change_in_level_m"]
    if not records:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(records).copy()

    # Timestamp
    ts_col = "timestamp" if "timestamp" in df.columns else ("Timestamp" if "Timestamp" in df.columns else None)
    df["dt"] = df[ts_col].apply(_to_dt) if ts_col else pd.NaT

    # Sensor ID
    sid_col = "sensor_id" if "sensor_id" in df.columns else ("Sensor ID" if "Sensor ID" in df.columns else None)
    df["sensor_id"] = df[sid_col] if sid_col else None

    # Geo/meta
    for out, cands in (
        ("latitude", ("latitude","Latitude")),
        ("longitude", ("longitude","Longitude")),
        ("location", ("location","Location")),
    ):
        if out not in df.columns:
            for c in cands:
                if c in df.columns:
                    df[out] = df[c]
                    break
        if out not in df.columns:
            df[out] = None

    # Level + change
    if "river_level_m" in df.columns:
        lvl = df["river_level_m"]
    elif "River Level (m)" in df.columns:
        lvl = df["River Level (m)"]
    else:
        lvl = pd.Series([np.nan] * len(df))

    if "change_in_level_m" in df.columns:
        chg = df["change_in_level_m"]
    elif "Change in Level (m)" in df.columns:
        chg = df["Change in Level (m)"]
    elif "level_delta" in df.columns:  # simulator
        chg = df["level_delta"]
    else:
        chg = pd.Series([np.nan] * len(df))

    df["river_level_m"] = pd.to_numeric(lvl, errors="coerce")
    df["change_in_level_m"] = pd.to_numeric(chg, errors="coerce")

    out = df[["dt","sensor_id","latitude","longitude","location","river_level_m","change_in_level_m"]]
    out = out.dropna(subset=["dt","sensor_id","river_level_m"])
    return out.sort_values("dt")


def normalize_weather(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Returns canonical columns:
      dt, sensor_id, latitude, longitude, location,
      actual_rainfall_mm, actual_windspeed_kmh, actual_temperature_c, actual_humidity_percent, actual_storm
    Accepts CSV loader keys and simulator keys (act_*).
    """
    cols = [
        "dt","sensor_id","latitude","longitude","location",
        "actual_rainfall_mm","actual_windspeed_kmh","actual_temperature_c","actual_humidity_percent","actual_storm"
    ]
    if not records:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(records).copy()

    # Timestamp
    ts_col = "timestamp" if "timestamp" in df.columns else ("Timestamp" if "Timestamp" in df.columns else None)
    df["dt"] = df[ts_col].apply(_to_dt) if ts_col else pd.NaT

    # Sensor ID
    sid_col = "sensor_id" if "sensor_id" in df.columns else ("Sensor ID" if "Sensor ID" in df.columns else None)
    df["sensor_id"] = df[sid_col] if sid_col else None

    # Geo/meta
    for out, cands in (
        ("latitude", ("latitude","Latitude")),
        ("longitude", ("longitude","Longitude")),
        ("location", ("location","Location")),
    ):
        if out not in df.columns:
            for c in cands:
                if c in df.columns:
                    df[out] = df[c]
                    break
        if out not in df.columns:
            df[out] = None

    # Actuals: prefer CSV "Actual ..." else simulator "act_*"
    def pick_actual(*names):
        for n in names:
            if n in df.columns:
                return pd.to_numeric(df[n], errors="coerce")
        return pd.Series([np.nan] * len(df))

    df["actual_rainfall_mm"]      = pick_actual("Actual Rainfall (mm)", "act_rainfall")
    df["actual_windspeed_kmh"]    = pick_actual("Actual Windspeed (km/h)", "act_windspeed")
    df["actual_temperature_c"]    = pick_actual("Actual Temperature (°C)", "act_temp")
    df["actual_humidity_percent"] = pick_actual("Actual Humidity (%)", "act_humidity")

    # Storm flag: handle Yes/No, 1/0, True/False
    if "Actual Storm" in df.columns:
        st = df["Actual Storm"]
    elif "actual_storm" in df.columns:
        st = df["actual_storm"]
    else:
        st = pd.Series(["No"] * len(df))

    def _norm_yesno(x: Any) -> str:
        if isinstance(x, (int, float)) and not pd.isna(x):
            return "Yes" if x != 0 else "No"
        s = str(x).strip().lower()
        return "Yes" if s in ("yes", "true", "1") else "No"

    df["actual_storm"] = st.map(_norm_yesno)

    out = df[[
        "dt","sensor_id","latitude","longitude","location",
        "actual_rainfall_mm","actual_windspeed_kmh","actual_temperature_c","actual_humidity_percent","actual_storm"
    ]]
    out = out.dropna(subset=["dt","sensor_id"])
    return out.sort_values("dt")


# -------------------------------------------------------------------
# Forecast core
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


def predict_river(
    df: pd.DataFrame,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    horizon_s: int = DEFAULT_HORIZON_SECONDS,
    step_s: int = DEFAULT_STEP_SECONDS,
) -> List[Dict[str, Any]]:
    """
    Forecast river level for each sensor for the next horizon at given cadence.
    Output keys align with your existing style:
      timestamp (ISO), sensor_id, time_sensor_id, latitude, longitude, location,
      predicted_river_level_m, predicted_change_in_level_m, predicted_flood_event
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
                "timestamp": ts.isoformat(),
                "sensor_id": sid,
                "time_sensor_id": f"{ts.strftime('%Y-%m-%d %H:%M:%S')}-{sid}",
                "latitude": _coerce_float(lat, None),
                "longitude": _coerce_float(lon, None),
                "location": loc,
                "predicted_river_level_m": float(round(lvl, 2)),
                # per-step change (approx): slope/sec * step_s
                "predicted_change_in_level_m": float(round(a * step_s, 3)),
                "predicted_flood_event": flood,
            })
    return preds


def predict_weather(
    df: pd.DataFrame,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    horizon_s: int = DEFAULT_HORIZON_SECONDS,
    step_s: int = DEFAULT_STEP_SECONDS,
) -> List[Dict[str, Any]]:
    """
    Forecast weather ACTUALS forward (then write them into `predicted_*` fields).
    Output keys:
      timestamp (ISO), sensor_id, time_sensor_id, latitude, longitude, location,
      predicted_rainfall_mm, predicted_windspeed_kmh, predicted_temperature_c,
      predicted_humidity_percent, predicted_storm, predicted_weather_flood_risk
    """
    preds: List[Dict[str, Any]] = []
    if df.empty:
        return preds

    # (pred_key, act_key, (min, max), rounding dp)
    fields = [
        ("predicted_rainfall_mm",      "actual_rainfall_mm",      (0, None), 2),
        ("predicted_windspeed_kmh",    "actual_windspeed_kmh",    (0, None), 1),
        ("predicted_temperature_c",    "actual_temperature_c",    (None, None), 1),
        ("predicted_humidity_percent", "actual_humidity_percent", (0, 100), 2),
    ]

    for sid, g in df.groupby("sensor_id"):
        g = g.sort_values("dt")
        last_ts = g["dt"].iloc[-1]
        cutoff = last_ts - timedelta(minutes=window_minutes)
        gw = g[g["dt"] >= cutoff]
        if gw.empty:
            continue

        lat = _latest_nonnull(g["latitude"])
        lon = _latest_nonnull(g["longitude"])
        loc = _latest_nonnull(g["location"])
        last_storm = str(_latest_nonnull(g["actual_storm"], "No")).strip().lower()
        last_storm_yes = last_storm in ("yes", "true", "1")

        # Fit trends on ACTUALS in the recent window
        trends: Dict[str, Tuple[float, float]] = {}
        for pred_key, act_key, _bounds, _dp in fields:
            vals = pd.to_numeric(gw[act_key], errors="coerce").dropna().tolist()
            ts   = gw.loc[gw[act_key].notna(), "dt"].tolist()
            a, b = _fit_trend(ts, vals) if len(vals) >= 1 else (0.0, np.nan)
            trends[pred_key] = (a, b)

        fts = _future_times(last_ts, horizon_s, step_s)
        t0 = gw["dt"].iloc[0]

        for ts in fts:
            sec = (ts - t0).total_seconds()
            out: Dict[str, Any] = {
                "timestamp": ts.isoformat(),
                "sensor_id": sid,
                "time_sensor_id": f"{ts.strftime('%Y-%m-%d %H:%M:%S')}-{sid}",
                "latitude": _coerce_float(lat, None),
                "longitude": _coerce_float(lon, None),
                "location": loc,
            }

            # Project each metric with sanity bounds + rounding
            for (pred_key, _act_key, (mn, mx), dp) in fields:
                a, b = trends[pred_key]
                val = (a * sec + b) if np.isfinite(b) else np.nan
                if mn is not None:
                    val = max(mn, val)
                if mx is not None:
                    val = min(mx, val)
                out[pred_key] = round(float(val), dp)

            # Simple storm persistence (swap to classifier if you add one later)
            out["predicted_storm"] = "Yes" if last_storm_yes else "No"

            # Optional derived risk purely from weather (rain + storm)
            rain = out.get("predicted_rainfall_mm", 0.0)
            out["predicted_weather_flood_risk"] = "Yes" if (rain > 3.0 and out["predicted_storm"] == "Yes") else "No"

            preds.append(out)

    return preds


# -------------------------------------------------------------------
# Convenience helpers to use from  API
# -------------------------------------------------------------------
def predict_from_buffers(
    river_records: List[Dict[str, Any]],
    weather_records: List[Dict[str, Any]],
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    horizon_seconds: int = DEFAULT_HORIZON_SECONDS,
    step_seconds: int = DEFAULT_STEP_SECONDS,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    One-shot forecaster that ingests  in-memory buffers and returns
    (river_predictions, weather_predictions).
    """
    r_df = normalize_river(river_records)
    w_df = normalize_weather(weather_records)

    river_preds = predict_river(r_df, window_minutes, horizon_seconds, step_seconds)
    weather_preds = predict_weather(w_df, window_minutes, horizon_seconds, step_seconds)
    return river_preds, weather_preds


def export_predictions_to_json(
    river_preds: List[Dict[str, Any]],
    weather_preds: List[Dict[str, Any]],
    output_dir: str = "data/"
) -> str:
    """
    Optional utility: write predictions to JSON files
    """
    import os, json
    os.makedirs(output_dir, exist_ok=True)
    rp = f"{output_dir.rstrip('/')}/river_predictions_15s.json"
    wp = f"{output_dir.rstrip('/')}/weather_predictions_15s.json"
    with open(rp, "w") as f:
        json.dump(river_preds, f, indent=2)
    with open(wp, "w") as f:
        json.dump(weather_preds, f, indent=2)
    return output_dir


# Explicit re-exports (useful if you `from forecast_service import *`)
__all__ = [
    "normalize_river", "normalize_weather",
    "predict_river", "predict_weather",
    "predict_from_buffers", "export_predictions_to_json",
    "FLOOD_THRESHOLD_M",
]
