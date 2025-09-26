# data_loader.py - Utility to load and process your CSV data
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any

class DataLoader:
    def __init__(self):
        self.river_data = []
        self.weather_data = []
        self.social_data = []
    
    def load_river_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """Load river level data from CSV"""
        try:
            # Read CSV with your column structure
            df = pd.read_csv(csv_path)
            
            # Convert to list of dictionaries
            river_data = []
            for _, row in df.iterrows():
                river_data.append({
                    "timestamp": row["Timestamp"],
                    "sensor_id": row["Sensor ID"],
                    "time_sensor_id": row["Time_Sensor_ID"],
                    "latitude": row["Latitude"],
                    "longitude": row["Longitude"],
                    "location": row["Location"],
                    "river_level_m": row["River Level (m)"],
                    "change_in_level_m": row["Change in Level (m)"],
                    "flood_event": row["Flood Event"]
                })
            
            self.river_data = river_data
            print(f"Loaded {len(river_data)} river data points")
            return river_data
            
        except Exception as e:
            print(f"Error loading river data: {e}")
            return []
    
    def load_weather_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """Load weather data from CSV"""
        try:
            # Try different encodings to handle special characters like °
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    print(f"Successfully loaded weather.csv with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Could not read CSV with any supported encoding")

            print(df.columns)
            
            weather_data = []
            for _, row in df.iterrows():
                weather_data.append({
                    "timestamp": row["Timestamp"],
                    "sensor_id": row["Sensor ID"],
                    "time_sensor_id": row["Time_Sensor_ID"],
                    "latitude": row["Latitude"],
                    "longitude": row["Longitude"],
                    "location": row["Location"],
                    "predicted_rainfall_mm": row["Predicted Rainfall (mm)"],
                    "actual_rainfall_mm": row["Actual Rainfall (mm)"],
                    "predicted_windspeed_kmh": row["Predicted Windspeed (km/h)"],
                    "actual_windspeed_kmh": row["Actual Windspeed (km/h)"],
                    "predicted_temperature_c": row["Predicted Temperature (°C)"],
                    "actual_temperature_c": row["Actual Temperature (°C)"],
                    "predicted_humidity_percent": row["Predicted Humidity (%)"],
                    "actual_humidity_percent": row["Actual Humidity (%)"],
                    "predicted_storm": row["Predicted Storm"],
                    "actual_storm": row["Actual Storm"]
                })
            
            self.weather_data = weather_data
            print(f"Loaded {len(weather_data)} weather data points")
            return weather_data
            
        except Exception as e:
            print(f"Error loading weather data: {e}")
            return []
    
    def load_social_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """Load social media data from CSV"""
        try:
            df = pd.read_csv(csv_path)
            
            social_data = []
            for _, row in df.iterrows():
                social_data.append({
                    "timestamp": row["hourly_timestamp"],
                    "datestamp_gauge": row["datestamp_gauge"],
                    "sentiment_score": row["Average of sentiment_score"],
                    "distance_to_gauge_km": row["Sum of distance_to_gauge_km"],
                    "post_count": row["Count of post_id"],
                    "cunupia": row["Cunupia"],
                    "piarco": row["Piarco"],
                    "st_augustine": row["St. Augustine"],
                    "st_helena": row["St. Helena"]
                })
            
            self.social_data = social_data
            print(f"Loaded {len(social_data)} social data points")
            return social_data
            
        except Exception as e:
            print(f"Error loading social data: {e}")
            return []
    
    def export_to_json(self, output_dir: str = "data/"):
        """Export loaded data to JSON files for FastAPI"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Export river data
        with open(f"{output_dir}/river_data.json", "w") as f:
            json.dump(self.river_data, f, indent=2, default=str)
        
        # Export weather data
        with open(f"{output_dir}/weather_data.json", "w") as f:
            json.dump(self.weather_data, f, indent=2, default=str)
        
        # Export social data
        with open(f"{output_dir}/social_data.json", "w") as f:
            json.dump(self.social_data, f, indent=2, default=str)
        
        print(f"Data exported to {output_dir}")
    
    def get_locations(self) -> List[str]:
        """Get unique locations from the data"""
        locations = set()
        
        for data in self.river_data:
            locations.add(data["location"])
        
        for data in self.weather_data:
            locations.add(data["location"])
        
        return list(locations)
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of loaded data"""
        return {
            "river_data_points": len(self.river_data),
            "weather_data_points": len(self.weather_data),
            "social_data_points": len(self.social_data),
            "locations": self.get_locations(),
            "time_range": {
                "start": min([d["timestamp"] for d in self.river_data]) if self.river_data else None,
                "end": max([d["timestamp"] for d in self.river_data]) if self.river_data else None
            },
            "sensors": list(set([d["sensor_id"] for d in self.river_data])) if self.river_data else []
        }

# Usage example
if __name__ == "__main__":
    loader = DataLoader()
    
    # Load your CSV files
    loader.load_river_data("river_level.csv")
    loader.load_weather_data("weather.csv") 
    loader.load_social_data("social.csv")
    
    # Export to JSON for FastAPI
    loader.export_to_json()
    
    # Print summary
    summary = loader.get_data_summary()
    print("\nData Summary:")
    print(json.dumps(summary, indent=2, default=str))