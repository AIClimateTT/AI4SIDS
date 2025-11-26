"""
AI4SIDS Main Workflow
=====================
Simple command-line interface to run the multi-agent system
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_llm, DATA_DIR
from tools.data_processing import process_sensor_data
from agents.data_ingestion_agent import DataIngestionAgent
from agents.flood_risk_agent import FloodRiskAgent
from langchain_core.messages import HumanMessage


def print_banner():
    """Print welcome banner"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🌊 AI4SIDS CLIMATE RESILIENCE 🌊              ║
║                                                           ║
║        Multi-Agent System for Disaster Preparedness       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")


def run_simplified_workflow(csv_file: str):
    """
    Run simplified workflow with just 2 agents for testing
    
    Args:
        csv_file: Path to CSV data file
    """
    print_banner()
    print(f"🚀 Starting AI4SIDS Workflow")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📄 Data File: {csv_file}\n")
    
    # Initialize LLM
    try:
        llm = get_llm()
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {str(e)}")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Check your .env file exists and has NVIDIA_API_KEY")
        print("   2. OR install Ollama and run: ollama pull llama3")
        return
    
    # Initialize agents
    print("\n🤖 Initializing Agents...")
    data_agent = DataIngestionAgent(llm)
    risk_agent = FloodRiskAgent(llm)
    print("✅ Agents ready\n")
    
    # Initialize state
    state = {
        "messages": [HumanMessage(content=f"Process weather data from {csv_file}")],
        "current_data": {},
        "risk_assessment": {},
        "prediction_accuracy": {},
        "alerts_generated": [],
        "educational_content": [],
        "feedback_metrics": {},
        "next_agent": "data_ingestion"
    }
    
    # Step 1: Process data
    print("="*60)
    print("STEP 1: DATA INGESTION")
    print("="*60)
    
    sensor_data = process_sensor_data.invoke({"csv_path": csv_file})
    state["current_data"] = sensor_data
    
    if sensor_data.get("status") != "success":
        print(f"\n❌ Data processing failed: {sensor_data.get('error')}")
        return
    
    # Step 2: Data Ingestion Agent
    state = data_agent.process(state)
    
    # Step 3: Flood Risk Agent
    print("\n" + "="*60)
    print("STEP 2: FLOOD RISK ASSESSMENT")
    print("="*60)
    
    state = risk_agent.process(state)
    
    # Display Results
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    # Risk Assessments
    print("\n🌊 RISK ASSESSMENTS:")
    for location, risk in state.get("risk_assessment", {}).items():
        risk_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "moderate": "🟡",
            "low": "🟢"
        }.get(risk["risk_level"], "⚪")
        
        print(f"\n📍 {location}")
        print(f"   {risk_emoji} Risk Level: {risk['risk_level'].upper()}")
        print(f"   📊 Risk Score: {risk['score']}/100")
        
        if risk.get("factors"):
            print(f"   ⚠️  Risk Factors:")
            for factor in risk["factors"]:
                print(f"      • {factor}")
        
        if risk.get("recommendations"):
            print(f"   💡 Recommendations:")
            for i, rec in enumerate(risk["recommendations"][:3], 1):
                print(f"      {i}. {rec}")
    
    # Alerts
    alerts = [
        risk for risk in state.get("risk_assessment", {}).values()
        if risk["risk_level"] in ["high", "critical"]
    ]
    
    if alerts:
        print("\n🚨 ALERTS GENERATED:")
        for alert in alerts:
            print(f"   ⚠️  {alert['location']}: {alert['risk_level'].upper()} RISK")
    else:
        print("\n✅ No alerts required - All locations at acceptable risk levels")
    
    print("\n" + "="*60)
    print("✅ Workflow Complete!")
    print("="*60 + "\n")


def main():
    """Main entry point"""
    
    # Check for CSV file argument
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Use sample data
        sample_files = list(Path(DATA_DIR / "sample").glob("*.csv"))
        
        if not sample_files:
            print("❌ No CSV files found in data/sample/")
            print("\n💡 Usage:")
            print("   python main.py <path_to_csv_file>")
            print("\n   OR place CSV files in: data/sample/")
            return
        
        csv_file = str(sample_files[0])
        print(f"📂 Using sample file: {csv_file}")
    
    # Check if file exists
    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        return
    
    # Run workflow
    try:
        run_simplified_workflow(csv_file)
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()