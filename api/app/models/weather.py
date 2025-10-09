from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class Weather(Base):
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Enable timezone support
    
    # Predicted values
    predicted_rainfall_mm = Column(Float, nullable=False)
    predicted_temperature_c = Column(Float, nullable=False)
    predicted_humidity_percent = Column(Float, nullable=False)
    predicted_windspeed_kmh = Column(Float, nullable=False)
    predicted_storm = Column(Boolean, nullable=False, default=False)
    
    # Actual values
    actual_rainfall_mm = Column(Float, nullable=False)
    actual_temperature_c = Column(Float, nullable=False)
    actual_humidity_percent = Column(Float, nullable=False)
    actual_windspeed_kmh = Column(Float, nullable=False)
    actual_storm = Column(Boolean, nullable=False, default=False)
    
    # Relationship
    location = relationship("Location", back_populates="weather_data")
