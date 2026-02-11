# TO DELETE
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


@tool
def process_river_gauge_data(csv_path: str) -> Dict[str, Any]:
    """
    Process river gauge data from CSV files

    Args:
        csv_path: Path to river gauge CSV file

    Returns:
        Dictionary with processed river metrics
    """
    try:
        print(f"[RIVER] Processing river gauge data from: {csv_path}")
        df = pd.read_csv(csv_path)

        # Strip whitespace from headers
        df.columns = df.columns.str.strip()

        # Basic validation
        required_cols = ['Sensor ID', 'Location', 'River Level (m)',
                        'Change in Level (m)', 'Flood Event', 'Timestamp']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            return {
                "error": f"Missing required columns: {missing_cols}",
                "status": "failed"
            }

        # Convert timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # Get latest readings for each gauge
        latest_readings = df.sort_values('Timestamp').groupby('Sensor ID').last()

        # Calculate statistics
        gauges_data = []
        for sensor_id, row in latest_readings.iterrows():
            gauge_info = {
                'sensor_id': sensor_id,
                'location': row['Location'],
                'current_level': float(row['River Level (m)']),
                'change_rate': float(row['Change in Level (m)']),
                'flood_event': row['Flood Event'] == 'Yes',
                'latitude': float(row.get('Latitude', 0)),
                'longitude': float(row.get('Longitude', 0)),
                'timestamp': str(row['Timestamp'])
            }
            gauges_data.append(gauge_info)

        # Calculate overall metrics
        metrics = {
            "status": "success",
            "total_gauges": int(df['Sensor ID'].nunique()),
            "locations": df['Location'].unique().tolist(),
            "total_readings": len(df),
            "avg_river_level": float(df['River Level (m)'].mean()),
            "max_river_level": float(df['River Level (m)'].max()),
            "gauges_rising": int((latest_readings['Change in Level (m)'] > 0).sum()),
            "gauges_falling": int((latest_readings['Change in Level (m)'] < 0).sum()),
            "flood_events": int((df['Flood Event'] == 'Yes').sum()),
            "timestamp": str(df['Timestamp'].max()),
            "gauges": gauges_data,
            "raw_data": df.to_dict('records')
        }

        print(f"[OK] Processed {len(df)} readings from {metrics['total_gauges']} river gauges")
        print(f"   Locations: {', '.join(metrics['locations'][:3])}...")
        print(f"   Avg River Level: {metrics['avg_river_level']:.2f}m")
        print(f"   Gauges Rising: {metrics['gauges_rising']}, Falling: {metrics['gauges_falling']}")
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
def process_social_media_data(csv_path: str) -> Dict[str, Any]:
    """
    Process social media aggregated data from CSV files

    Args:
        csv_path: Path to social media CSV file

    Returns:
        Dictionary with processed social media metrics
    """
    try:
        print(f"[SOCIAL] Processing social media data from: {csv_path}")
        df = pd.read_csv(csv_path)

        # Strip whitespace from headers
        df.columns = df.columns.str.strip()

        # Basic validation
        required_cols = ['hourly_timestamp', 'Average of sentiment_score',
                        'Count of post_id']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            return {
                "error": f"Missing required columns: {missing_cols}",
                "status": "failed"
            }

        # Convert timestamp to datetime
        df['hourly_timestamp'] = pd.to_datetime(df['hourly_timestamp'])

        # Get community columns (Cunupia, Piarco, St. Augustine, St. Helena)
        community_cols = [col for col in df.columns if col in ['Cunupia', 'Piarco', 'St. Augustine', 'St. Helena']]

        # Calculate latest metrics
        latest_timestamp = df['hourly_timestamp'].max()
        latest_data = df[df['hourly_timestamp'] == latest_timestamp]

        # Aggregate by community
        community_stats = {}
        for community in community_cols:
            total_posts = int(df[community].sum())
            recent_posts = int(latest_data[community].sum())
            community_stats[community] = {
                'total_posts': total_posts,
                'recent_posts': recent_posts
            }

        # Overall sentiment analysis
        avg_sentiment = float(df['Average of sentiment_score'].mean())
        latest_sentiment = float(latest_data['Average of sentiment_score'].mean())

        # Classify sentiment
        def classify_sentiment(score):
            if score < -0.3:
                return "highly_negative"
            elif score < -0.1:
                return "negative"
            elif score < 0.1:
                return "neutral"
            elif score < 0.3:
                return "positive"
            else:
                return "highly_positive"

        metrics = {
            "status": "success",
            "total_posts": int(df['Count of post_id'].sum()),
            "avg_sentiment": avg_sentiment,
            "latest_sentiment": latest_sentiment,
            "sentiment_classification": classify_sentiment(latest_sentiment),
            "total_records": len(df),
            "timestamp": str(latest_timestamp),
            "communities": community_stats,
            "raw_data": df.to_dict('records')
        }

        print(f"[OK] Processed {metrics['total_posts']} social media posts")
        print(f"   Overall Sentiment: {avg_sentiment:.3f} ({classify_sentiment(avg_sentiment)})")
        print(f"   Latest Sentiment: {latest_sentiment:.3f} ({metrics['sentiment_classification']})")
        print(f"   Communities: {', '.join(community_cols)}")

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
def analyze_river_trends(gauge_data: Dict[str, Any], location: str = None) -> Dict[str, Any]:
    """
    Analyze river level trends and predict risks

    Args:
        gauge_data: Processed river gauge data from process_river_gauge_data
        location: Optional specific location to analyze

    Returns:
        Dictionary with trend analysis and risk predictions
    """
    try:
        if gauge_data.get("status") != "success":
            return {"error": "Invalid gauge data", "status": "failed"}

        gauges = gauge_data.get("gauges", [])

        if location:
            # Filter to specific location
            gauges = [g for g in gauges if location.lower() in g['location'].lower()]

        if not gauges:
            return {"error": f"No gauge data found for location: {location}", "status": "failed"}

        analysis = {
            "status": "success",
            "gauges_analyzed": len(gauges),
            "trends": []
        }

        for gauge in gauges:
            level = gauge['current_level']
            change = gauge['change_rate']

            # Determine trend
            if abs(change) < 0.1:
                trend = "stable"
                risk = "low"
            elif change > 0.5:
                trend = "rapidly_rising"
                risk = "high"
            elif change > 0.2:
                trend = "rising"
                risk = "moderate"
            elif change < -0.5:
                trend = "rapidly_falling"
                risk = "low"
            else:
                trend = "falling"
                risk = "low"

            # Check absolute level thresholds
            if level > 3.5:
                risk = "critical"
            elif level > 3.0 and risk != "critical":
                risk = "high"

            gauge_analysis = {
                "location": gauge['location'],
                "sensor_id": gauge['sensor_id'],
                "current_level": level,
                "change_rate": change,
                "trend": trend,
                "risk_level": risk,
                "flood_event_active": gauge['flood_event']
            }

            analysis['trends'].append(gauge_analysis)

        return analysis

    except Exception as e:
        return {"error": f"Analysis error: {str(e)}", "status": "failed"}


@tool
def analyze_sentiment_trends(social_data: Dict[str, Any], community: str = None) -> Dict[str, Any]:
    """
    Analyze social media sentiment trends and detect anomalies

    Args:
        social_data: Processed social media data from process_social_media_data
        community: Optional specific community to analyze

    Returns:
        Dictionary with sentiment analysis and alerts
    """
    try:
        if social_data.get("status") != "success":
            return {"error": "Invalid social media data", "status": "failed"}

        communities = social_data.get("communities", {})

        if community and community not in communities:
            return {"error": f"Community not found: {community}", "status": "failed"}

        analysis = {
            "status": "success",
            "overall_sentiment": social_data['avg_sentiment'],
            "latest_sentiment": social_data['latest_sentiment'],
            "classification": social_data['sentiment_classification'],
            "community_analysis": []
        }

        # Analyze each community
        for comm_name, comm_data in communities.items():
            if community and comm_name != community:
                continue

            # Determine alert level based on posts and sentiment
            posts = comm_data['recent_posts']
            alert_level = "normal"

            if posts > 10 and social_data['latest_sentiment'] < -0.3:
                alert_level = "critical"
            elif posts > 5 and social_data['latest_sentiment'] < -0.1:
                alert_level = "high"
            elif posts > 3:
                alert_level = "moderate"

            comm_analysis = {
                "community": comm_name,
                "total_posts": comm_data['total_posts'],
                "recent_posts": comm_data['recent_posts'],
                "alert_level": alert_level
            }

            analysis['community_analysis'].append(comm_analysis)

        return analysis

    except Exception as e:
        return {"error": f"Analysis error: {str(e)}", "status": "failed"}