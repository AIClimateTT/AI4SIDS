"""
Flood Risk Assessment Agent — Self-contained specialist for multi-source risk synthesis.
Fetches its own data from the backend API and provides domain-specific LLM analysis.
"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from clients.backend_client import BackendClient


SYSTEM_PROMPT = """You are the Flood Risk Assessment Agent for AI4SIDS, a climate resilience system monitoring flood-prone areas in Trinidad & Tobago.

You will receive raw sensor data below. Your job is to ANALYZE and INTERPRET this data — do NOT simply list or reformat the numbers. The user is a community member or emergency responder who needs to understand what the data MEANS for their safety.

HOW TO RESPOND:
1. Start with a clear, plain-language assessment: "Right now, conditions are safe/concerning/dangerous because..."
2. Explain what the numbers mean in context (e.g., "A river level of 2.3m is well below the 2.7m flood threshold")
3. Identify patterns or trends (e.g., "All 8 locations are currently safe, with river levels stable and no significant changes")
4. If there are risks, explain what factors are contributing and how they interact
5. End with practical recommendations appropriate to the current risk level
6. If the user asks about a specific location, focus your analysis there but mention relevant nearby conditions

Multi-Source Risk Assessment Framework:
- Cross-validate sensors, river gauges, and community reports
- If ALL sources agree = HIGH CONFIDENCE in assessment
- If sources disagree = FLAG and explain the discrepancy

Risk Level Thresholds (for your reference — explain these in plain language, don't just state the label):
- CRITICAL (>= 4.2m river): Immediate evacuation territory
- HIGH (>= 3.6m): Serious concern, prepare to evacuate
- MODERATE (>= 3.0m): Flooding likely, avoid travel
- LOW (>= 2.7m): Approaching concern, keep monitoring
- SAFE (< 2.7m): Normal conditions

Be conversational and direct. Use "I" when referring to data ("I'm seeing...", "Based on what I'm tracking...").
Never just dump a list of locations and numbers — always interpret what the data means."""


class FloodRiskAgent:
    """Self-contained agent for multi-source flood risk assessment."""

    def __init__(self, llm, backend: BackendClient):
        self.llm = llm
        self.backend = backend
        self.name = "Flood Risk Assessment Agent"

    def process(self, query: str, location: str = None,
                history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a flood risk or evacuation query.

        Returns:
            {"response": str, "data": dict, "risk_level": str | None}
        """
        data: Dict[str, Any] = {}
        risk_level = None

        if location:
            # Per-location: get comprehensive real-time data
            real_time = self.backend.get_real_time(location)
            data["real_time"] = real_time
            if real_time:
                risk_level = real_time.get("river_conditions", {}).get("flood_risk")
        else:
            # All-locations summary
            risk_summary = self.backend.get_risk_summary()
            system_update = self.backend.get_system_update()
            data["risk_summary"] = risk_summary
            data["system_update"] = system_update

        context = self._build_context(data, location)

        if not context:
            return {
                "response": "I don't have current risk assessment data available right now.",
                "data": data,
                "risk_level": None,
            }

        response = self._analyze(query, context, history)
        return {"response": response, "data": data, "risk_level": risk_level}

    def _build_context(self, data: Dict[str, Any], location: Optional[str]) -> str:
        """Build a data context string from backend API responses."""
        parts = []

        # Per-location real-time data
        real_time = data.get("real_time")
        if real_time:
            loc_name = real_time.get("location", location or "?")
            river = real_time.get("river_conditions", {})
            weather = real_time.get("weather", {})
            social = real_time.get("social_activity", {})
            insights = real_time.get("insights", {})

            parts.append(f"**{loc_name} — Real-Time Conditions:**")
            parts.append(f"  Flood Risk: {river.get('flood_risk', 'UNKNOWN')}")
            parts.append(f"  River Level: {river.get('level', 0):.2f}m")
            parts.append(f"  Change Rate: {river.get('change_rate', 0):+.3f}m")
            parts.append(f"  Trend: {river.get('trend', 'stable')}")
            parts.append(f"  Rainfall: {weather.get('rainfall_mm', 0):.1f}mm")
            parts.append(f"  Temperature: {weather.get('temperature_c', 0):.1f}C")
            parts.append(f"  Humidity: {weather.get('humidity_percent', 0):.0f}%")
            parts.append(f"  Community Sentiment: {social.get('sentiment_score', 0):.3f} ({social.get('sentiment_level', 'Unknown')})")
            parts.append(f"  Community Activity: {social.get('activity_level', 'LOW')} ({social.get('post_count', 0)} posts)")
            if insights:
                parts.append(f"  Summary: {insights.get('summary', '')}")
                parts.append(f"  Recommendation: {insights.get('recommendation', '')}")
                parts.append(f"  Correlation: {insights.get('correlation', '')}")

        # All-locations risk summary
        risk_summary = data.get("risk_summary")
        if risk_summary:
            total = risk_summary.get("total_locations", 0)
            high_risk = risk_summary.get("high_risk_count", 0)
            by_level = risk_summary.get("by_level", {})

            parts.append(f"\n**Risk Summary — {total} Locations Monitored:**")
            parts.append(f"  High-risk locations: {high_risk}")

            for level in ["CRITICAL", "HIGH", "MODERATE", "LOW", "SAFE"]:
                locs = by_level.get(level, [])
                if locs:
                    parts.append(f"\n  **{level}** ({len(locs)}):")
                    for loc in locs:
                        parts.append(f"    - {loc['name']}: {loc['river_level_m']:.2f}m (change: {loc['change_rate_m']:+.3f}m)")

        # System-wide alerts
        system = data.get("system_update")
        if system:
            alerts = system.get("alerts", [])
            if alerts:
                parts.append(f"\n**Active Alerts ({len(alerts)}):**")
                for alert in alerts:
                    parts.append(f"  - [{alert.get('level', '').upper()}] {alert.get('message', '')}")

        return "\n".join(parts) if parts else ""

    def _analyze(self, query: str, context: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Invoke the LLM with risk-specialist prompt and data context."""
        system_content = f"{SYSTEM_PROMPT}\n\n**Current Flood Risk Data:**\n{context}"
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
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            print(f"[FloodRiskAgent] LLM error: {e}")
            if context:
                return f"Here's the current risk assessment data:\n\n{context}"
            return "I'm having trouble assessing flood risk right now. Please try again."
