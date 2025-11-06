# app/entities/weekforecast.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import math

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship, Session
from app.entities.base import Base  # <-- uses your shared declarative base

# -----------------------
# SQLAlchemy model
# -----------------------
class WeekForecast(Base):
    __tablename__ = "week_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(200), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)         # the day the forecast applies to
    generated_at = Column(DateTime, nullable=False)         # when the forecast was generated
    rainfall_mm = Column(Integer, nullable=False)
    risk = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    # Optional: a JSON column to store baseline or meta for the generation
    meta = Column(JSON, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "location": self.location,
            "date": self.date.isoformat() if isinstance(self.date, (datetime,)) else str(self.date),
            "generated_at": self.generated_at.isoformat() if isinstance(self.generated_at, (datetime,)) else str(self.generated_at),
            "rainfall_mm": int(self.rainfall_mm),
            "risk": self.risk,
            "confidence": float(self.confidence),
            "meta": self.meta,
        }

# -----------------------
# Pydantic models (unchanged except tiny field name alignment)
# -----------------------
class ForecastDay(BaseModel):
    date: datetime
    label: str                # e.g., Today / Tomorrow / Oct 18
    rainfall_mm: int
    risk: str                 # SAFE / LOW / MODERATE / HIGH / CRITICAL
    confidence: float         # 0..1

class ForecastResponse(BaseModel):
    location: str
    generated_at: datetime
    baseline: Dict[str, Any]
    forecast: List[ForecastDay]

# -----------------------
# Helpers (same logic as your simulator)
# -----------------------
def _clamp(x, a, b):
    return max(a, min(b, x))

def _risk_from_mm(mm: float) -> str:
    if mm > 100:
        return "CRITICAL"
    if mm > 60:
        return "HIGH"
    if mm > 30:
        return "MODERATE"
    if mm > 15:
        return "LOW"
    return "SAFE"

def simulate_7_day_forecast(
    base_daily_mm: float,
    base_conf: float = 0.9,
    sentiment: float = 0.0,
    days: int = 7,
    start_date: Optional[datetime] = None,
    location: str = "unknown",
    baseline: Optional[Dict[str, Any]] = None
) -> ForecastResponse:
    """
    Produce a ForecastResponse containing a list of ForecastDay objects.
    Rules:
     - Exponential decay from base_daily_mm, with daily jitter +/-15%
     - ~12% chance for a storm uplift on a given day (up to +60%)
     - Confidence decreases by 0.03/day plus random noise, slightly lowered by negative sentiment
    """
    if start_date is None:
        start_date = datetime.utcnow()

    if baseline is None:
        baseline = {"base_daily_mm": base_daily_mm, "base_conf": base_conf, "sentiment": sentiment}

    results = []
    base_daily_mm = float(max(base_daily_mm, 0.0))

    sentiment_penalty = 0.0
    if isinstance(sentiment, (int, float)) and sentiment < 0:
        sentiment_penalty = _clamp(abs(sentiment) * 0.12, 0.0, 0.3)

    for i in range(days):
        decay = math.pow(0.72, i)
        jitter = (random.random() * 0.3) - 0.15
        storm = 1.0
        if random.random() < 0.12:
            storm = 1.0 + random.random() * 0.6

        mm = base_daily_mm * decay * (1 + jitter) * storm
        mm = int(round(_clamp(mm, 0.0, 9999.0)))

        conf = _clamp(base_conf - i * 0.03 - sentiment_penalty - (random.random() * 0.02), 0.35, 0.99)
        risk = _risk_from_mm(mm)

        day_dt = (start_date + timedelta(days=i))
        label = _label_for_index(i, start_date)

        results.append(ForecastDay(
            date=day_dt,
            label=label,
            rainfall_mm=mm,
            risk=risk,
            confidence=round(conf, 3)
        ))

    response = ForecastResponse(
        location=location,
        generated_at=start_date,
        baseline=baseline,
        forecast=results
    )
    return response

def _label_for_index(i: int, start_date: datetime) -> str:
    if i == 0:
        return "Today"
    if i == 1:
        return "Tomorrow"
    # else return short date like 'Oct 18'
    return (start_date + timedelta(days=i)).strftime("%b %d")

# -----------------------
# Persistence helper: store ForecastResponse into DB session
# -----------------------
def persist_forecast(db_session: Session, forecast_resp: ForecastResponse) -> List[WeekForecast]:
    """
    Persist each ForecastDay in forecast_resp.forecast into the database.
    Returns the list of persisted WeekForecast objects (not necessarily refreshed).
    """
    stored = []
    for day in forecast_resp.forecast:
        wf = WeekForecast(
            location=forecast_resp.location,
            date=day.date.date() if isinstance(day.date, datetime) else day.date,
            generated_at=forecast_resp.generated_at,
            rainfall_mm=day.rainfall_mm,
            risk=day.risk,
            confidence=day.confidence,
            meta=forecast_resp.baseline
        )
        db_session.add(wf)
        stored.append(wf)

    # NOTE: commit / flush left to caller so they can control transactions:
    # db_session.commit()
    return stored

# -----------------------
# Convenience: simulate + persist (example)
# -----------------------
def simulate_and_store(
    db_session: Session,
    location: str,
    base_daily_mm: float,
    **simulate_kwargs
) -> ForecastResponse:
    """
    Convenience wrapper: simulate, persist (but don't commit), and return the response.
    Caller should commit the session when ready.
    """
    start_date = simulate_kwargs.get("start_date", None)
    response = simulate_7_day_forecast(
        base_daily_mm=base_daily_mm,
        location=location,
        start_date=start_date,
        **simulate_kwargs
    )

    persist_forecast(db_session, response)
    return response

# -----------------------
# End of file
# -----------------------
