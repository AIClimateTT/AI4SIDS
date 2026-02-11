from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class RiverLevel(Base):
    __tablename__ = "river_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Enable timezone support
    river_level_m = Column(Float, nullable=False)
    change_in_level_m = Column(Float, nullable=False)
    
    # Relationship
    location = relationship("Location", back_populates="river_levels")
