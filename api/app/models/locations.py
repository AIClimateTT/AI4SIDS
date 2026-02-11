from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    sensor_id = Column(String, unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Relationships
    river_levels = relationship("RiverLevel", back_populates="location")
    weather_data = relationship("Weather", back_populates="location")
    social_data = relationship("Social", back_populates="location")
    predictions = relationship("RiverPrediction", back_populates="location")
