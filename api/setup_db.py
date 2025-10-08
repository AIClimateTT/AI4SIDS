#!/usr/bin/env python3
"""
Migration script to set up database and load initial data
"""
import sys
import os

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.db import init_db
from app.core.data_loader import load_all_data


def main():
    """Run database initialization and data loading"""
    print("🚀 Starting AI4SIDS database setup...")
    
    try:
        # Initialize database tables
        print("📦 Creating database tables...")
        init_db()
        print("✅ Database tables created")
        
        # Load data from JSON files
        print("📊 Loading data from JSON files...")
        load_all_data()
        print("✅ Data loading completed")
        
        print("🎉 Setup completed successfully!")
        print("\n📋 Summary:")
        print("  - SQLite database: ai4sids_demo.db")
        print("  - Tables: locations, river_levels, weather, social")
        print("  - Data loaded from: data/*.json files")
        print("\n🚀 You can now start the API server:")
        print("  cd api && python -m uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()