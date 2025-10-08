from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Weather(Base):
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    predicted_rainfall_mm = Column(Float, nullable=False)
    actual_rainfall_mm = Column(Float, nullable=False)
    actual_temperature_c = Column(Float, nullable=False)
    actual_humidity_percent = Column(Float, nullable=False)
    actual_windspeed_kmh = Column(Float, nullable=False)
    
    # Relationship
    location = relationship("Location", back_populates="weather_data")
