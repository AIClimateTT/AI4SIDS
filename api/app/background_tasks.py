"""
Background task service for automatic prediction generation
Runs predictions for all locations every 5 minutes and stores them in database
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Location, RiverPrediction
from app.features.predictions.service.enhanced import generate_predictions, store_predictions, cleanup_old_predictions

logger = logging.getLogger(__name__)


class PredictionTaskManager:
    """
    Manages background prediction generation tasks
    """
    
    def __init__(self):
        self.running = False
        self.task: asyncio.Task = None
        
        # === VIDEO RECORDING MODE ===
        self.prediction_interval = 30   # 30 seconds (fast predictions for video)
        self.cleanup_interval = 600      # 10 minutes (faster cleanup)
        
        # === NORMAL PRODUCTION MODE (COMMENTED OUT) ===
        # self.prediction_interval = 300  # 5 minutes in seconds
        # self.cleanup_interval = 3600   # 1 hour in seconds
        
        self.last_cleanup = datetime.now(timezone.utc)
    
    async def start(self):
        """Start the background prediction task"""
        if self.running:
            logger.warning("Prediction task manager is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_prediction_loop())
        logger.info("Started background prediction task manager")
    
    async def stop(self):
        """Stop the background prediction task"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped background prediction task manager")
    
    async def _run_prediction_loop(self):
        """Main prediction loop that runs continuously"""
        while self.running:
            try:
                await self._generate_predictions_for_all_locations()
                await self._cleanup_old_predictions_if_needed()
                
                # Wait for next interval
                await asyncio.sleep(self.prediction_interval)
                
            except asyncio.CancelledError:
                logger.info("Prediction loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in prediction loop: {e}", exc_info=True)
                # Wait a bit before retrying on error
                await asyncio.sleep(60)
    
    async def _generate_predictions_for_all_locations(self):
        """Generate predictions for all locations in the database"""
        try:
            # Get database session
            db_gen = get_db()
            session: Session = next(db_gen)
            
            try:
                # Get all locations
                locations = session.query(Location).all()
                
                if not locations:
                    logger.info("No locations found for prediction generation")
                    return
                
                predictions_generated = 0
                
                for location in locations:
                    try:
                        # Generate predictions for this location
                        predictions = generate_predictions(
                            session, 
                            location.id, 
                            prediction_minutes=30
                        )
                        
                        if predictions:
                            # Remove existing predictions for the same time range to avoid duplicates
                            await self._cleanup_duplicate_predictions(session, location.id, predictions)
                            
                            # Store new predictions
                            store_predictions(session, location.id, predictions)
                            predictions_generated += len(predictions)
                            
                            logger.debug(f"Generated {len(predictions)} predictions for location {location.name}")
                        else:
                            logger.debug(f"No predictions generated for location {location.name} (insufficient data)")
                    
                    except Exception as e:
                        logger.error(f"Error generating predictions for location {location.name}: {e}")
                        continue
                
                logger.info(f"Generated {predictions_generated} total predictions for {len(locations)} locations")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error in prediction generation: {e}", exc_info=True)
    
    async def _cleanup_duplicate_predictions(self, session: Session, location_id: int, new_predictions: List[dict]):
        """Remove existing predictions that overlap with new predictions"""
        if not new_predictions:
            return
        
        # Get time range of new predictions
        min_time = min(pred["predicted_for_time"] for pred in new_predictions)
        max_time = max(pred["predicted_for_time"] for pred in new_predictions)
        
        # Delete existing predictions in this time range
        session.query(RiverPrediction).filter(
            RiverPrediction.location_id == location_id,
            RiverPrediction.predicted_for_time >= min_time,
            RiverPrediction.predicted_for_time <= max_time
        ).delete()
        
        session.commit()
    
    async def _cleanup_old_predictions_if_needed(self):
        """Clean up old predictions if enough time has passed"""
        now = datetime.now(timezone.utc)
        if (now - self.last_cleanup).total_seconds() < self.cleanup_interval:
            return
        
        try:
            # Get database session
            db_gen = get_db()
            session: Session = next(db_gen)
            
            try:
                cleanup_old_predictions(session, hours_to_keep=48)
                self.last_cleanup = now
                logger.info("Cleaned up old predictions")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error cleaning up old predictions: {e}")
    
    def get_status(self) -> dict:
        """Get current status of the prediction task manager"""
        return {
            "running": self.running,
            "prediction_interval_seconds": self.prediction_interval,
            "cleanup_interval_seconds": self.cleanup_interval,
            "last_cleanup": self.last_cleanup.isoformat() if self.last_cleanup else None,
            "task_active": self.task is not None and not self.task.done() if self.task else False
        }


# Global instance
prediction_manager = PredictionTaskManager()


async def start_prediction_tasks():
    """Start background prediction tasks - called during app startup"""
    await prediction_manager.start()


async def stop_prediction_tasks():
    """Stop background prediction tasks - called during app shutdown"""
    await prediction_manager.stop()


def get_prediction_task_status() -> dict:
    """Get status of prediction tasks"""
    return prediction_manager.get_status()


async def force_prediction_generation():
    """Manually trigger prediction generation for all locations"""
    logger.info("Manually triggering prediction generation")
    await prediction_manager._generate_predictions_for_all_locations()