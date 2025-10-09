# Timezone-Aware DateTime Fix

## Additional Issue Found

After the initial timezone fix, a new error appeared:

```
Cannot subtract tz-naive and tz-aware datetime-like objects
```

## Root Cause

SQLite doesn't store timezone information natively. Even though we define columns as `DateTime(timezone=True)` in SQLAlchemy, when timestamps are retrieved from SQLite, they come back as **naive datetimes** (without timezone info). This caused errors when trying to:

- Subtract timedeltas from database timestamps
- Compare database timestamps with `datetime.now(timezone.utc)`
- Calculate time differences in prediction algorithms

## Solution

Ensure all timestamps retrieved from the database are converted to **timezone-aware** datetimes by explicitly setting `tzinfo=timezone.utc` if the timestamp is naive.

## Files Modified (Additional Fixes)

### 1. `/api/app/enhanced_prediction_service.py`

**Changes:**

- `normalize_river_from_db()`: Added timezone-awareness check for `record.timestamp`
  ```python
  timestamp = record.timestamp
  if timestamp.tzinfo is None:
      timestamp = timestamp.replace(tzinfo=timezone.utc)
  ```
- `normalize_weather_from_db()`: Added same timezone-awareness check
- `get_enhanced_prediction_accuracy()`: Added timezone-awareness check for `prediction.predicted_for_time`

### 2. `/api/app/features/location/service.py`

**Changes:**

- `get_analytics_data()`: Added timezone-awareness checks when formatting timestamps:
  ```python
  "timestamp": (level.timestamp.replace(tzinfo=timezone.utc) if level.timestamp.tzinfo is None else level.timestamp).isoformat()
  ```
  Applied to both historical data and prediction data formatting.

### 3. `/api/app/features/location/contoller.py`

**Changes:**

- `get_location_timeline()`: Added timezone-awareness check before calling `.isoformat()`
- `get_location_history()`: Added timezone-awareness check for history data points

## Pattern Used

Wherever we access `.timestamp` from database records, we now use:

```python
timestamp = record.timestamp
if timestamp.tzinfo is None:
    timestamp = timestamp.replace(tzinfo=timezone.utc)
```

This ensures:

1. All timestamps are timezone-aware (UTC)
2. Arithmetic operations with timedelta work correctly
3. Comparisons with `datetime.now(timezone.utc)` work correctly
4. `.isoformat()` outputs include timezone info (e.g., "2025-10-09T14:30:00+00:00")

## Testing

After restarting the API server, predictions should generate without errors and all timestamps should be consistent across the application.
