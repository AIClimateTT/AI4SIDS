"""
Data processing tools for AI4SIDS
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from langchain_core.tools import tool

@tool
def process_sensor_data(csv_path: str) -> Dict[str, Any]:
    """
    Process incoming sensor data from CSV files
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Dictionary with processed metrics
    """
    try:
        print(f" Processing sensor data from: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Strip whitespace from headers
        df.columns = df.columns.str.strip()
        
        # Basic validation
        required_cols = ['Sensor ID', 'Location', 'Actual Rainfall (mm)', 
                        'Actual Windspeed (km/h)', 'Actual Storm', 'Flood Event']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return {
                "error": f"Missing required columns: {missing_cols}",
                "status": "failed"
            }
        
        # Calculate key metrics
        metrics = {
            "status": "success",
            "total_sensors": int(df['Sensor ID'].nunique()),
            "locations": df['Location'].unique().tolist(),
            "total_readings": len(df),
            "avg_actual_rainfall": float(df['Actual Rainfall (mm)'].mean()),
            "max_actual_rainfall": float(df['Actual Rainfall (mm)'].max()),
            "avg_actual_windspeed": float(df['Actual Windspeed (km/h)'].mean()),
            "flood_events": int((df['Flood Event'] == 'Yes').sum()),
            "storm_conditions": int((df['Actual Storm'] == 'Storm').sum()),
            "timestamp": str(df['Timestamp'].iloc[0]) if len(df) > 0 else None,
            "raw_data": df.to_dict('records')
        }
        
        print(f" Processed {len(df)} readings from {metrics['total_sensors']} sensors")
        print(f"   Locations: {', '.join(metrics['locations'])}")
        print(f"   Avg Rainfall: {metrics['avg_actual_rainfall']:.1f}mm")
        print(f"   Flood Events: {metrics['flood_events']}")
        
        return metrics
        
    except FileNotFoundError:
        return {
            "error": f"File not found: {csv_path}",
            "status": "failed"
        }
    except Exception as e:
        return {
            "error": f"Processing error: {str(e)}",
            "status": "failed"
        }


@tool
def calculate_prediction_accuracy(data: List[Dict]) -> Dict[str, float]:
    """
    Calculate model prediction accuracy metrics
    
    Args:
        data: List of dictionaries with prediction and actual values
        
    Returns:
        Dictionary with accuracy metrics
    """
    try:
        print(" Calculating prediction accuracy...")
        df = pd.DataFrame(data)
        
        metrics = {}
        
        # Rainfall accuracy (MAE and percentage)
        if 'Actual Rainfall (mm)' in df.columns and 'Predicted Rainfall (mm)' in df.columns:
            rainfall_mae = np.abs(
                df['Actual Rainfall (mm)'] - df['Predicted Rainfall (mm)']
            ).mean()
            
            # Avoid division by zero
            actual_mean = df['Actual Rainfall (mm)'].mean()
            if actual_mean > 0:
                rainfall_accuracy = 100 - (rainfall_mae / actual_mean * 100)
            else:
                rainfall_accuracy = 0
                
            metrics['rainfall_mae'] = float(rainfall_mae)
            metrics['rainfall_accuracy'] = float(max(0, rainfall_accuracy))
        
        # Windspeed accuracy
        if 'Actual Windspeed (km/h)' in df.columns and 'Predicted Windspeed (km/h)' in df.columns:
            windspeed_mae = np.abs(
                df['Actual Windspeed (km/h)'] - df['Predicted Windspeed (km/h)']
            ).mean()
            metrics['windspeed_mae'] = float(windspeed_mae)
        
        # Storm prediction accuracy (categorical)
        if 'Actual Storm' in df.columns and 'Predicted Storm' in df.columns:
            storm_match = (df['Actual Storm'] == df['Predicted Storm']).sum()
            metrics['storm_accuracy'] = float((storm_match / len(df)) * 100)
        
        # Overall accuracy (average of available metrics)
        accuracy_values = [v for k, v in metrics.items() if 'accuracy' in k]
        if accuracy_values:
            metrics['overall_accuracy'] = float(np.mean(accuracy_values))
        
        print(f" Accuracy Metrics:")
        for key, value in metrics.items():
            if 'accuracy' in key:
                print(f"   {key}: {value:.1f}%")
            else:
                print(f"   {key}: {value:.2f}")
        
        return metrics
        
    except Exception as e:
        print(f" Error calculating accuracy: {str(e)}")
        return {"error": str(e)}


@tool
def validate_sensor_reading(reading: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate individual sensor reading for anomalies
    
    Args:
        reading: Dictionary with sensor data
        
    Returns:
        Validation result with anomalies flagged
    """
    anomalies = []
    
    # Check for unrealistic values
    rainfall = reading.get('Actual Rainfall (mm)', 0)
    if rainfall < 0 or rainfall > 500:
        anomalies.append(f"Unrealistic rainfall: {rainfall}mm")
    
    windspeed = reading.get('Actual Windspeed (km/h)', 0)
    if windspeed < 0 or windspeed > 300:
        anomalies.append(f"Unrealistic windspeed: {windspeed}km/h")
    
    temperature = reading.get('Actual Temperature (C)', 0)
    if temperature < -50 or temperature > 60:
        anomalies.append(f"Unrealistic temperature: {temperature}C")
    
    humidity = reading.get('Actual Humidity (%)', 0)
    if humidity < 0 or humidity > 100:
        anomalies.append(f"Invalid humidity: {humidity}%")
    
    return {
        "valid": len(anomalies) == 0,
        "anomalies": anomalies,
        "reading": reading
    }