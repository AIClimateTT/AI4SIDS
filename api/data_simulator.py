# generate_realtime_data.py

import asyncio
import numpy as np
import random
from datetime import datetime, timedelta

# Global shared data
river_data = []
weather_data = []
social_data = []
current_data_index = 0

# Define sensor locations
SENSOR_LOCATIONS = {
    "CR-001": ("St. Augustine", 10.6406, -61.3994),
    "CR-002": ("Cunupia", 10.5682, -61.3702),
    "CR-003": ("Piarco", 10.5957, -61.3376),
    "CR-004": ("St. Helena", 10.5989, -61.3222),
    "CR-005": ("Chaguanas", 10.5164, -61.4115),
    "CR-006": ("Kelly Village", 10.6102, -61.3361),
    "CR-007": ("Las Lomas", 10.6261, -61.3647),
    "CR-008": ("Caroni", 10.5654, -61.4592)
}


async def generate_realtime_data():
    """Continuously generate new simulated data every 15 seconds."""
    global river_data, weather_data, social_data, current_data_index

    level_tracker = {sid: 2.2 for sid in SENSOR_LOCATIONS}  # initial levels
    cycle = 0

    while True:
        timestamp = datetime.now()
        river_batch = []
        weather_batch = []
        social_batch = []

        for sensor_id, (location, lat, lon) in SENSOR_LOCATIONS.items():
            # RIVER SIMULATION
            prev_level = level_tracker[sensor_id]
            change = np.random.normal(loc=0.02, scale=0.01)
            new_level = max(prev_level + change, 0)
            level_tracker[sensor_id] = new_level
            flood = new_level >= 3.0

            river_batch.append({
                "timestamp": timestamp.strftime("%m/%d/%Y %I:%M:%S %p"),
                "sensor_id": sensor_id,
                "time_sensor_id": f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}-{sensor_id}",
                "latitude": lat,
                "longitude": lon,
                "location": location,
                "river_level_m": round(new_level, 2),
                "level_delta": round(change, 3),
                "flood_event": "Yes" if flood else "No"
            })

            # WEATHER SIMULATION
            pred_rain = round(np.random.uniform(0.5, 1.5), 2)
            act_rain = pred_rain + np.random.normal(loc=0.1, scale=0.05)
            pred_wind = round(np.random.uniform(10, 15), 1)
            act_wind = pred_wind + np.random.normal(loc=2, scale=0.5)
            pred_temp = round(np.random.uniform(26, 28), 1)
            act_temp = pred_temp + np.random.normal(loc=-0.2, scale=0.2)
            pred_humid = round(np.random.uniform(70, 85), 1)
            act_humid = pred_humid + np.random.normal(loc=5, scale=1)
            pred_storm = 1 if random.random() < 0.3 else 0
            act_storm = 1 if random.random() < 0.3 else 0

            weather_batch.append({
                "timestamp": timestamp.strftime("%m/%d/%Y %I:%M:%S %p"),
                "sensor_id": sensor_id,
                "time_sensor_id": f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}-{sensor_id}",
                "latitude": lat,
                "longitude": lon,
                "location": location,
                "pred_rainfall": round(pred_rain, 2),
                "act_rainfall": round(act_rain, 2),
                "pred_windspeed": round(pred_wind, 1),
                "act_windspeed": round(act_wind, 1),
                "pred_temp": round(pred_temp, 1),
                "act_temp": round(act_temp, 1),
                "pred_humidity": round(pred_humid, 1),
                "act_humidity": round(act_humid, 1),
                "pred_storm": "Yes" if pred_storm else "No",
                "act_storm": "Yes" if act_storm else "No",
                "flood_event": "Yes" if act_rain > 3.0 and act_storm else "No"
            })

            # SOCIAL MEDIA SIMULATION
            user_location = random.choice(["Cunupia", "Piarco", "St. Augustine", "St. Helena"])
            sentiment = round(np.clip(np.random.normal(loc=-0.5, scale=0.3), -1, 1), 2)

            social_batch.append({
                "datestamp_gauge": f"{timestamp.strftime('%d-%m-%Y %H:%M:%S')}-{sensor_id}",
                "hourly_timestamp": timestamp,
                "avg_sentiment_score": sentiment,
                "dist_to_gauge_km": round(random.uniform(0.1, 5.0), 2),
                "post_id_count": 1,
                "cunupia": 1 if user_location == "Cunupia" else 0,
                "piarco": 1 if user_location == "Piarco" else 0,
                "st_augustine": 1 if user_location == "St. Augustine" else 0,
                "st_helena": 1 if user_location == "St. Helena" else 0
            })

        # Append to shared global lists
        river_data.extend(river_batch)
        weather_data.extend(weather_batch)
        social_data.extend(social_batch)

        current_data_index = len(river_data) - 1
        print(f"[{timestamp.strftime('%H:%M:%S')}] Generated data index: {current_data_index}")

        if cycle > 3:
            await asyncio.sleep(15)

        cycle += 1
