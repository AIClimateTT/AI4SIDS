"""
Configuration settings for AI4SIDS
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# LLM Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
USE_OLLAMA = not bool(NVIDIA_API_KEY)  # Use Ollama if no NVIDIA key

# LLM Model Selection
if USE_OLLAMA:
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
    LLM_TEMPERATURE = 0.1
else:
    LLM_MODEL = "meta/llama-3.1-70b-instruct"
    LLM_TEMPERATURE = 0.1

# LangSmith (Optional Monitoring)
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "ai4sids")

# Risk Thresholds
RISK_THRESHOLDS = {
    "critical": 75,
    "high": 50,
    "moderate": 25,
    "low": 0
}

# Weather Thresholds
WEATHER_THRESHOLDS = {
    "heavy_rainfall": 40,  # mm
    "moderate_rainfall": 30,  # mm
    "high_windspeed": 25,  # km/h
    "high_humidity": 85,  # %
}

# Alert Configuration
ALERT_CHANNELS = ["sms", "mobile_app", "tv", "radio", "social_media"]
ALERT_LANGUAGES = ["en", "es", "fr", "ht"]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_llm():
    """Get configured LLM instance"""
    if USE_OLLAMA:
        from langchain_community.llms import Ollama
        print(f"Using Ollama with model: {LLM_MODEL}")
        return Ollama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE
        )
    else:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        print(f"Using NVIDIA NIM with model: {LLM_MODEL}")
        return ChatNVIDIA(
            model=LLM_MODEL,
            api_key=NVIDIA_API_KEY,
            temperature=LLM_TEMPERATURE
        )

print(f"""
{'='*60}
AI4SIDS Configuration Loaded
{'='*60}
LLM Backend: {'Ollama (Local)' if USE_OLLAMA else 'NVIDIA NIM (Cloud)'}
Model: {LLM_MODEL}
Data Directory: {DATA_DIR}
Logs Directory: {LOGS_DIR}
LangSmith Tracing: {'Enabled' if LANGCHAIN_TRACING_V2 else 'Disabled'}
{'='*60}
""")