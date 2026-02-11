"""
Quick Test Script for AI4SIDS
==============================
Tests individual components before running full workflow
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_1_environment():
    """Test 1: Check environment setup"""
    print("\n" + "="*60)
    print("TEST 1: Environment Setup")
    print("="*60)
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        nvidia_key = os.getenv("NVIDIA_API_KEY", "")
        
        if nvidia_key:
            print("✅ NVIDIA API Key found")
            print(f"   Key: {nvidia_key[:10]}...")
        else:
            print("⚠️  No NVIDIA API Key - will use Ollama")
            print("   Make sure Ollama is running: ollama serve")
        
        print("✅ Environment check passed")
        return True
        
    except Exception as e:
        print(f"❌ Environment check failed: {str(e)}")
        return False


def test_2_data_files():
    """Test 2: Check data files exist"""
    print("\n" + "="*60)
    print("TEST 2: Data Files")
    print("="*60)
    
    try:
        from config.settings import settings

        sample_dir = settings.DATA_DIR / "sample"
        csv_files = list(sample_dir.glob("*.csv"))
        
        if csv_files:
            print(f"✅ Found {len(csv_files)} CSV files:")
            for f in csv_files:
                print(f"   - {f.name}")
            return True
        else:
            print("⚠️  No CSV files found in data/sample/")
            print("   Please place your CSV files there")
            return False
            
    except Exception as e:
        print(f"❌ Data files check failed: {str(e)}")
        return False


def test_3_llm_connection():
    """Test 3: Test LLM connection"""
    print("\n" + "="*60)
    print("TEST 3: LLM Connection")
    print("="*60)
    
    try:
        from config.settings import settings

        print("🔧 Initializing LLM...")
        llm = settings.get_llm()
        
        print("📡 Testing LLM with simple query...")
        response = llm.invoke("Say 'Hello from AI4SIDS!' in one sentence.")
        
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        
        print(f"✅ LLM Response: {content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ LLM connection failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   For NVIDIA NIM:")
        print("   - Check your API key in .env file")
        print("   - Get key from: https://build.nvidia.com")
        print("\n   For Ollama:")
        print("   - Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("   - Run: ollama serve")
        print("   - Pull model: ollama pull llama3")
        return False


def test_4_data_processing():
    """Test 4: Test data processing tools"""
    print("\n" + "="*60)
    print("TEST 4: Data Processing")
    print("="*60)
    
    try:
        from config.settings import settings
        from tools.data_processing import process_sensor_data

        sample_dir = settings.DATA_DIR / "sample"
        csv_files = list(sample_dir.glob("*.csv"))
        
        if not csv_files:
            print("⚠️  No CSV files to test")
            return False
        
        # Filter to only weather sensor files (not gauge or social media)
        weather_files = [
            f for f in csv_files 
            if 'weather' in f.name.lower() and 'social_media' not in f.name.lower()
        ]
        
        if not weather_files:
            print("⚠️  No weather sensor CSV files found")
            print("   Looking for files with 'weather' in the name")
            print("   Note: Gauge and social_media CSVs have different formats")
            return False
        
        test_file = str(weather_files[0])
        print(f"📊 Processing: {weather_files[0].name}")
        
        result = process_sensor_data.invoke({"csv_path": test_file})
        
        if result.get("status") == "success":
            print("✅ Data processing successful")
            print(f"   Sensors: {result.get('total_sensors')}")
            print(f"   Locations: {', '.join(result.get('locations', []))}")
            print(f"   Readings: {result.get('total_readings')}")
            return True
        else:
            print(f"❌ Data processing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Data processing test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_5_risk_assessment():
    """Test 5: Test risk assessment tools"""
    print("\n" + "="*60)
    print("TEST 5: Risk Assessment")
    print("="*60)
    
    try:
        from tools.risk_assessment import assess_flood_risk
        
        # Mock sensor data
        mock_data = {
            "raw_data": [{
                "Location": "Test Location",
                "Actual Rainfall (mm)": 45,
                "Actual Windspeed (km/h)": 30,
                "Actual Humidity (%)": 88,
                "Actual Storm": "Storm",
                "Flood Event": "No",
                "Timestamp": "2025-03-01 12:00",
                "Sensor ID": "TEST-001"
            }]
        }
        
        print("🌊 Testing risk assessment with mock data...")
        risk = assess_flood_risk.invoke({
            "sensor_data": mock_data,
            "location": "Test Location"
        })
        
        print("✅ Risk assessment successful")
        print(f"   Risk Level: {risk['risk_level'].upper()}")
        print(f"   Risk Score: {risk['score']}/100")
        return True
        
    except Exception as e:
        print(f"❌ Risk assessment test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🧪 AI4SIDS SYSTEM TESTS 🧪                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    tests = [
        test_1_environment,
        test_2_data_files,
        test_3_llm_connection,
        test_4_data_processing,
        test_5_risk_assessment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} tests")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! Ready to run main workflow.")
        print("\nNext step: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")
    
    print()


if __name__ == "__main__":
    run_all_tests()