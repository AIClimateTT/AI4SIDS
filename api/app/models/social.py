from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Social(Base):
    __tablename__ = "social"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Enable timezone support
    post_count = Column(Integer, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    
    # Relationship
    location = relationship("Location", back_populates="social_data")