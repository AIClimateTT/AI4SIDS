#!/usr/bin/env python3
"""
Timezone Verification Script
Run this script to verify that all timestamps in API responses are in UTC
"""
import requests
import json
from datetime import datetime, timezone

API_BASE_URL = "http://localhost:8000"

def check_timestamp_format(timestamp_str, field_name):
    """Check if a timestamp string is in UTC format"""
    try:
        # Try to parse the timestamp
        if timestamp_str.endswith('Z'):
            print(f"  ✅ {field_name}: {timestamp_str} (UTC with 'Z')")
            return True
        elif '+00:00' in timestamp_str or 'T' in timestamp_str:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            if dt.tzinfo is not None:
                print(f"  ✅ {field_name}: {timestamp_str} (UTC aware)")
                return True
            else:
                print(f"  ⚠️  {field_name}: {timestamp_str} (naive datetime - missing timezone)")
                return False
        else:
            print(f"  ❌ {field_name}: {timestamp_str} (not in UTC format)")
            return False
    except Exception as e:
        print(f"  ❌ {field_name}: Error parsing {timestamp_str} - {e}")
        return False

def test_system_update():
    """Test /api/system-update endpoint"""
    print("\n🔍 Testing /api/system-update")
    try:
        response = requests.get(f"{API_BASE_URL}/api/system-update")
        if response.status_code == 200:
            data = response.json()
            check_timestamp_format(str(data.get('timestamp', '')), 'system timestamp')
            
            # Check locations
            if 'locations' in data:
                for loc in data['locations'][:2]:  # Check first 2 locations
                    print(f"\n  Location: {loc.get('name')}")
                    check_timestamp_format(loc.get('last_updated', ''), 'last_updated')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_real_time_conditions():
    """Test /api/real-time/{location} endpoint"""
    print("\n🔍 Testing /api/real-time/St. Augustine")
    try:
        response = requests.get(f"{API_BASE_URL}/api/real-time/St. Augustine")
        if response.status_code == 200:
            data = response.json()
            check_timestamp_format(data.get('timestamp', ''), 'timestamp')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_analytics():
    """Test /api/analytics/{location_id} endpoint"""
    print("\n🔍 Testing /api/analytics/1")
    try:
        response = requests.get(f"{API_BASE_URL}/api/analytics/1")
        if response.status_code == 200:
            data = response.json()
            
            # Check time_range
            if 'time_range' in data:
                check_timestamp_format(data['time_range'].get('start_time', ''), 'time_range.start_time')
                check_timestamp_format(data['time_range'].get('end_time', ''), 'time_range.end_time')
            
            # Check historical data
            if 'historical_data' in data and len(data['historical_data']) > 0:
                print("\n  Checking first historical data point:")
                check_timestamp_format(data['historical_data'][0].get('timestamp', ''), 'historical_data[0].timestamp')
            
            # Check predictions
            if 'predictions' in data and len(data['predictions']) > 0:
                print("\n  Checking first prediction:")
                check_timestamp_format(data['predictions'][0].get('predicted_for_time', ''), 'predictions[0].predicted_for_time')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_history():
    """Test /api/history/{location} endpoint"""
    print("\n🔍 Testing /api/history/St. Augustine")
    try:
        response = requests.get(f"{API_BASE_URL}/api/history/St. Augustine")
        if response.status_code == 200:
            data = response.json()
            
            # Check current timestamp
            if 'current' in data:
                check_timestamp_format(data['current'].get('timestamp', ''), 'current.timestamp')
            
            # Check first history point
            if 'history' in data and len(data['history']) > 0:
                print("\n  Checking first history point:")
                check_timestamp_format(data['history'][0].get('timestamp', ''), 'history[0].timestamp')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🕐 TIMEZONE VERIFICATION SCRIPT")
    print("="*60)
    print(f"\nCurrent UTC time: {datetime.now(timezone.utc).isoformat()}")
    print(f"API Base URL: {API_BASE_URL}")
    
    test_system_update()
    test_real_time_conditions()
    test_analytics()
    test_history()
    
    print("\n" + "="*60)
    print("✅ Verification complete!")
    print("="*60)
    print("\nIf all timestamps show ✅, the timezone fix is working correctly.")
    print("If you see ⚠️ or ❌, there may still be timezone issues to address.")
