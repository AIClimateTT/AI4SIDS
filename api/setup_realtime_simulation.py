#!/usr/bin/env python3
"""
Database Migration Script for Denormalized Social Data
"""
import asyncio
from app.core.db import engine
from app.models.base import Base
from app.data_simulator import generate_realtime_data

def recreate_database():
    """Recreate database with updated schema"""
    print("🗄️ Recreating database with denormalized social table...")
    
    # Drop all tables and recreate them with new schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database recreated successfully!")
    print("📊 New social table structure:")
    print("   - location_id (FK to locations)")
    print("   - timestamp")
    print("   - post_count")
    print("   - sentiment_score")
    print("   ❌ Removed: st_augustine, piarco, cunupia, st_helena columns")

async def start_simulation():
    """Start the real-time data generation"""
    print("\n🌊 Starting real-time data simulation...")
    print("📍 Generating data for 8 sensor locations:")
    print("   - St. Augustine, Cunupia, Piarco, St. Helena")
    print("   - Chaguanas, Kelly Village, Las Lomas, Caroni")
    print("\n⏰ Data generation interval: 15 seconds")
    print("💾 Data persistence: SQLite database")
    print("🧹 Auto-cleanup: Keep last 24 hours")
    
    await generate_realtime_data()

if __name__ == "__main__":
    print("🏗️ AI4SIDS Database Migration & Real-time Simulation")
    print("=" * 60)
    
    # Recreate database with new schema
    recreate_database()
    
    print("\n🚀 Starting real-time data simulation...")
    print("Press Ctrl+C to stop the simulation")
    
    try:
        # Start the simulation
        asyncio.run(start_simulation())
    except KeyboardInterrupt:
        print("\n⏹️ Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")