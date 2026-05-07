"""
Weather Agent — Self-contained specialist for weather condition analysis.
Fetches its own data from the backend API and provides domain-specific LLM analysis.
"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from clients.backend_client import BackendClient


SYSTEM_PROMPT = """You are the Weather Analysis Agent for AI4SIDS, a climate resilience system monitoring Trinidad & Tobago.

You will receive raw weather sensor data below. Your job is to ANALYZE and INTERPRET this data — do NOT simply list the readings. The user needs to understand what the weather means for their safety and daily life.

HOW TO RESPOND:
1. Start with the big picture: "Right now in [location], conditions are [calm/rainy/stormy] with..."
2. Explain what the readings mean in context (e.g., "4.4mm of rainfall is light — well below the 40mm threshold that contributes to flooding")
3. Connect weather to flood risk: explain how current rainfall relates to river levels and flood potential
4. Highlight anything unusual or noteworthy (sudden changes, approaching thresholds)
5. Provide practical advice relevant to conditions (e.g., "Conditions are normal, no precautions needed" or "Heavy rain — avoid low-lying roads")
6. For multi-location overviews, identify patterns and outliers rather than listing every location

Weather Thresholds (for your reference — explain in plain language):
- Heavy rainfall: >= 40mm (significant flood contributor)
- Moderate rainfall: >= 30mm (potential flood contributor)
- High windspeed: >= 25 km/h (dangerous conditions)
- High humidity: >= 85% (saturated ground, poor drainage)

Be conversational and direct. Use "I" when referring to data ("I'm seeing...", "Right now in...").
Never just list raw numbers — always tell the user what the weather MEANS."""


class WeatherAgent:
    """Self-contained agent for weather condition analysis."""

    def __init__(self, llm, backend: BackendClient):
        self.llm = llm
        self.backend = backend
        self.name = "Weather Analysis Agent"

    def process(self, query: str, location: str = None,
                history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a weather query.

        Returns:
            {"response": str, "data": dict}
        """
        data: Dict[str, Any] = {}

        if location:
            real_time = self.backend.get_real_time(location)
            data["real_time"] = real_time
        else:
            # No specific location — get system-wide for an overview
            system = self.backend.get_system_update()
            data["system"] = system

        context = self._build_context(data, location)

        if not context:
            if location:
                return {
                    "response": f"I don't have current weather data for {location}.",
                    "data": data,
                }
            return {
                "response": "I don't have current weather data available. Try asking about a specific location like Cunupia, Piarco, or Chaguanas.",
                "data": data,
            }

        response, usage = self._analyze(query, context, history)
        return {"response": response, "data": data, "usage": usage}

    def _build_context(self, data: Dict[str, Any], location: Optional[str]) -> str:
        """Build a data context string from backend API responses."""
        parts = []

        real_time = data.get("real_time")
        if real_time:
            loc_name = real_time.get("location", location or "?")
            weather = real_time.get("weather", {})
            river = real_time.get("river_conditions", {})
            insights = real_time.get("insights", {})

            parts.append(f"**Current Weather in {loc_name}:**")
            parts.append(f"  Rainfall: {weather.get('rainfall_mm', 0):.1f}mm")
            parts.append(f"  Rainfall rate: {weather.get('rainfall_rate_hourly', 0):.1f}mm/hr")
            parts.append(f"  Temperature: {weather.get('temperature_c', 0):.1f}C")
            parts.append(f"  Humidity: {weather.get('humidity_percent', 0):.0f}%")
            parts.append(f"  Flood risk: {river.get('flood_risk', 'UNKNOWN')}")
            parts.append(f"  River level: {river.get('level', 0):.2f}m ({river.get('trend', 'stable')})")
            if insights:
                parts.append(f"  Correlation: {insights.get('correlation', '')}")

        system = data.get("system")
        if system:
            locations_data = system.get("locations", [])
            if locations_data:
                parts.append(f"**Weather Overview ({len(locations_data)} locations):**")
                for loc_data in locations_data:
                    name = loc_data.get("name", "?")
                    risk = loc_data.get("flood_risk", loc_data.get("current_risk", "UNKNOWN"))
                    level = loc_data.get("river_level", 0)
                    parts.append(f"  - {name}: risk={risk}, river={level:.2f}m")

        return "\n".join(parts) if parts else ""

    def _analyze(self, query: str, context: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Invoke the LLM with weather-specialist prompt and data context."""
        system_content = f"{SYSTEM_PROMPT}\n\n**Current Weather Data:**\n{context}"
        messages = [SystemMessage(content=system_content)]

        if history:
            for msg in history[-6:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=query))

        try:
            response = self.llm.invoke(messages)

            content = response.content if hasattr(response, "content") else str(response)
            usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            return content, usage

        except Exception as e:
            print(f"[WeatherAgent] LLM error: {e}")
            if context:
                return f"Here's the current weather data:\n\n{context}"
            return "I'm having trouble analyzing the weather right now. Please try again."
