"""
Data loader to populate SQLite database from JSON files
"""
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Location, RiverLevel, Weather, Social
from app.core.db import engine, SessionLocal


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string to datetime object"""
    try:
        return datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M")
    except ValueError:
        # Fallback for different formats
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")


def load_locations(session: Session, data: list) -> dict:
    """Load unique locations from data and return location_id mapping"""
    location_map = {}
    
    # Extract unique locations from river data
    unique_locations = {}
    for item in data:
        location_name = item.get("location")
        if location_name and location_name not in unique_locations:
            unique_locations[location_name] = {
                "name": location_name,
                "sensor_id": item.get("sensor_id", f"CR-{len(unique_locations)+1:03d}"),
                "latitude": item.get("latitude", 10.6918),
                "longitude": item.get("longitude", -61.2225)
            }
    
    # Create or get locations in database
    for location_data in unique_locations.values():
        location = session.query(Location).filter(Location.name == location_data["name"]).first()
        if not location:
            location = Location(**location_data)
            session.add(location)
            session.commit()
            session.refresh(location)
        location_map[location_data["name"]] = location.id
    
    return location_map


def load_river_data(session: Session, file_path: str, location_map: dict):
    """Load river level data from JSON file"""
    if not os.path.exists(file_path):
        print(f"River data file not found: {file_path}")
        return
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    print(f"Loading {len(data)} river data points...")
    
    for item in data:
        location_name = item.get("location")
        if location_name not in location_map:
            continue
            
        river_level = RiverLevel(
            location_id=location_map[location_name],
            timestamp=parse_timestamp(item["timestamp"]),
            river_level_m=item["river_level_m"],
            change_in_level_m=item["change_in_level_m"]
        )
        session.add(river_level)
    
    session.commit()
    print(f"✅ Loaded river data")


def load_weather_data(session: Session, file_path: str, location_map: dict):
    """Load weather data from JSON file"""
    if not os.path.exists(file_path):
        print(f"Weather data file not found: {file_path}")
        return
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    print(f"Loading {len(data)} weather data points...")
    
    for item in data:
        location_name = item.get("location")
        if location_name not in location_map:
            continue
            
        weather = Weather(
            location_id=location_map[location_name],
            timestamp=parse_timestamp(item["timestamp"]),
            predicted_rainfall_mm=item["predicted_rainfall_mm"],
            actual_rainfall_mm=item["actual_rainfall_mm"],
            actual_temperature_c=item["actual_temperature_c"],
            actual_humidity_percent=item["actual_humidity_percent"],
            actual_windspeed_kmh=item["actual_windspeed_kmh"]
        )
        session.add(weather)
    
    session.commit()
    print(f"✅ Loaded weather data")


def load_social_data(session: Session, file_path: str, location_map: dict):
    """Load social media data from JSON file"""
    if not os.path.exists(file_path):
        print(f"Social data file not found: {file_path}")
        return
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    print(f"Loading {len(data)} social data points...")
    
    for item in data:
        location_name = item.get("location")
        if location_name not in location_map:
            continue
            
        social = Social(
            location_id=location_map[location_name],
            timestamp=parse_timestamp(item["timestamp"]),
            post_count=item["post_count"],
            sentiment_score=item["sentiment_score"],
            st_augustine=item.get("st_augustine", 0),
            piarco=item.get("piarco", 0),
            cunupia=item.get("cunupia", 0),
            st_helena=item.get("st_helena", 0)
        )
        session.add(social)
    
    session.commit()
    print(f"✅ Loaded social data")


def load_all_data():
    """Load all data from JSON files into SQLite database"""
    session = SessionLocal()
    
    try:
        # Clear existing data (for clean reload)
        session.query(Social).delete()
        session.query(Weather).delete()
        session.query(RiverLevel).delete()
        session.query(Location).delete()
        session.commit()
        
        print("🗑️  Cleared existing data")
        
        # Load river data first to extract locations
        river_file = "data/river_data.json"
        if os.path.exists(river_file):
            with open(river_file, "r") as f:
                river_data = json.load(f)
        else:
            print("❌ No river data file found")
            return
        
        # Create location mapping
        location_map = load_locations(session, river_data)
        print(f"✅ Loaded {len(location_map)} locations")
        
        # Load all data types
        load_river_data(session, "data/river_data.json", location_map)
        load_weather_data(session, "data/weather_data.json", location_map)
        load_social_data(session, "data/social_data.json", location_map)
        
        print("🎉 Data loading completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error loading data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    from app.core.db import init_db
    
    # Initialize database tables
    init_db()
    
    # Load data
    load_all_data()