from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class RiverPrediction(Base):
    __tablename__ = "river_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    prediction_timestamp = Column(DateTime, nullable=False)  # When prediction was made
    predicted_for_time = Column(DateTime, nullable=False)    # Time being predicted for
    predicted_level_m = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)         # 0.0 to 1.0
    weather_factor_influence = Column(Float, nullable=False) # How much weather affected prediction
    
    # Relationship
    location = relationship("Location", back_populates="predictions")