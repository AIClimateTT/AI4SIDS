"""
Risk assessment tools for AI4SIDS
"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from config.settings import RISK_THRESHOLDS, WEATHER_THRESHOLDS

@tool
def assess_flood_risk(sensor_data: Dict, location: str) -> Dict[str, Any]:
    """
    Assess flood risk based on sensor readings
    
    Args:
        sensor_data: Dictionary containing raw_data list
        location: Location name to assess
        
    Returns:
        Risk assessment with level, score, and factors
    """
    print(f"🌊 Assessing flood risk for: {location}")
    
    raw_data = sensor_data.get('raw_data', [])
    location_data = [d for d in raw_data if d.get('Location') == location]
    
    if not location_data:
        print(f"⚠️  No data found for {location}")
        return {
            "location": location,
            "risk_level": "unknown",
            "score": 0,
            "factors": ["No data available"],
            "timestamp": None
        }
    
    # Get latest reading
    latest = location_data[0]
    risk_score = 0
    risk_factors = []
    
    # Rainfall risk assessment
    rainfall = latest.get('Actual Rainfall (mm)', 0)
    if rainfall >= WEATHER_THRESHOLDS['heavy_rainfall']:
        risk_score += 35
        risk_factors.append(f"Heavy rainfall: {rainfall:.1f}mm")
    elif rainfall >= WEATHER_THRESHOLDS['moderate_rainfall']:
        risk_score += 20
        risk_factors.append(f"Moderate rainfall: {rainfall:.1f}mm")
    
    # Windspeed risk assessment
    windspeed = latest.get('Actual Windspeed (km/h)', 0)
    if windspeed >= WEATHER_THRESHOLDS['high_windspeed']:
        risk_score += 25
        risk_factors.append(f"High windspeed: {windspeed:.1f}km/h")
    
    # Humidity risk assessment
    humidity = latest.get('Actual Humidity (%)', 0)
    if humidity >= WEATHER_THRESHOLDS['high_humidity']:
        risk_score += 15
        risk_factors.append(f"High humidity: {humidity:.1f}%")
    
    # Storm condition assessment
    storm = latest.get('Actual Storm', '')
    if storm == 'Storm':
        risk_score += 25
        risk_factors.append("Active storm detected")
    elif storm == 'Rainy':
        risk_score += 10
        risk_factors.append("Rainy conditions")
    
    # Check if flood already occurred
    flood_event = latest.get('Flood Event', 'No')
    if flood_event == 'Yes':
        risk_score = 100
        risk_factors.insert(0, "FLOOD EVENT IN PROGRESS")
    
    # Determine risk level based on score
    if risk_score >= RISK_THRESHOLDS['critical']:
        risk_level = "critical"
    elif risk_score >= RISK_THRESHOLDS['high']:
        risk_level = "high"
    elif risk_score >= RISK_THRESHOLDS['moderate']:
        risk_level = "moderate"
    else:
        risk_level = "low"
    
    result = {
        "location": location,
        "risk_level": risk_level,
        "score": risk_score,
        "factors": risk_factors if risk_factors else ["Normal conditions"],
        "timestamp": latest.get('Timestamp'),
        "sensor_id": latest.get('Sensor ID')
    }
    
    # Print assessment
    risk_emoji = {
        "critical": "🔴",
        "high": "🟠",
        "moderate": "🟡",
        "low": "🟢",
        "unknown": "⚪"
    }
    
    print(f"   {risk_emoji[risk_level]} Risk Level: {risk_level.upper()}")
    print(f"   📊 Risk Score: {risk_score}/100")
    if risk_factors:
        print(f"   ⚠️  Factors: {', '.join(risk_factors)}")
    
    return result


@tool
def calculate_risk_trend(location_history: List[Dict]) -> Dict[str, Any]:
    """
    Calculate risk trend over time for a location
    
    Args:
        location_history: List of historical risk assessments
        
    Returns:
        Trend analysis (increasing, decreasing, stable)
    """
    if len(location_history) < 2:
        return {
            "trend": "insufficient_data",
            "change": 0
        }
    
    # Calculate average risk score change
    recent_scores = [h['score'] for h in location_history[-5:]]
    older_scores = [h['score'] for h in location_history[-10:-5]] if len(location_history) >= 10 else []
    
    if not older_scores:
        return {
            "trend": "insufficient_data",
            "change": 0
        }
    
    recent_avg = sum(recent_scores) / len(recent_scores)
    older_avg = sum(older_scores) / len(older_scores)
    
    change = recent_avg - older_avg
    
    if change > 10:
        trend = "increasing"
    elif change < -10:
        trend = "decreasing"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "change": change,
        "recent_avg": recent_avg,
        "older_avg": older_avg
    }


@tool
def generate_recommendations(risk_level: str) -> List[str]:
    """
    Generate action recommendations based on risk level
    
    Args:
        risk_level: Current risk level (low, moderate, high, critical)
        
    Returns:
        List of recommended actions
    """
    recommendations = {
        "low": [
            "Continue normal monitoring",
            "Review emergency supplies inventory",
            "Stay informed of weather updates",
            "Ensure emergency contacts are up to date"
        ],
        "moderate": [
            "Monitor situation closely every 2-4 hours",
            "Prepare emergency kit (water, food, medications)",
            "Identify evacuation routes from your area",
            "Stay tuned to official emergency channels",
            "Charge all communication devices",
            "Secure loose outdoor items"
        ],
        "high": [
            "Prepare to evacuate if ordered by authorities",
            "Move valuables and important documents to higher ground",
            "Secure outdoor furniture and items",
            "Keep emergency kit accessible and ready",
            "Maintain fully charged communication devices",
            "Avoid unnecessary travel",
            "Monitor official alerts continuously",
            "Check on vulnerable neighbors"
        ],
        "critical": [
            "⚠️ EVACUATE IMMEDIATELY if instructed by authorities",
            "Move to designated emergency shelter NOW",
            "Do NOT attempt to cross flooded areas",
            "Follow emergency services instructions precisely",
            "Take only essential items and emergency kit",
            "Turn off utilities if time permits and safe to do so",
            "Avoid contact with floodwater (contamination risk)",
            "Stay on high ground until authorities declare all-clear"
        ]
    }
    
    return recommendations.get(risk_level, recommendations["moderate"])