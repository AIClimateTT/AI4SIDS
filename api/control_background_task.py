#!/usr/bin/env python3
"""
Simple script to control background data generation
Usage: python control_background_task.py [start|stop|status]
"""

import sys
import requests

API_URL = "http://localhost:8000"  # Change to your deployed URL

def get_status():
    """Check current status"""
    response = requests.get(f"{API_URL}/api/data-generation/status")
    data = response.json()
    
    print("\n📊 Background Task Status:")
    print(f"  Running: {'✅ YES' if data['running'] else '❌ NO'}")
    print(f"  Enabled in ENV: {data['enabled_in_env']}")
    print(f"  Cycle Interval: {data['cycle_interval_seconds']}s")
    print(f"  Task Exists: {data['task_exists']}")
    print(f"  Locations: {data['locations_count']}")
    print()

def start_generation():
    """Start background generation"""
    response = requests.post(f"{API_URL}/api/data-generation/start")
    data = response.json()
    
    if data['success']:
        print(f"\n✅ {data['message']}\n")
    else:
        print(f"\n❌ {data['message']}\n")
    
    get_status()

def stop_generation():
    """Stop background generation"""
    response = requests.post(f"{API_URL}/api/data-generation/stop")
    data = response.json()
    
    if data['success']:
        print(f"\n✅ {data['message']}\n")
    else:
        print(f"\n❌ {data['message']}\n")
    
    get_status()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python control_background_task.py [start|stop|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "status":
            get_status()
        elif command == "start":
            start_generation()
        elif command == "stop":
            stop_generation()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python control_background_task.py [start|stop|status]")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API at {API_URL}")
        print("   Make sure the API is running!\n")
        sys.exit(1)
