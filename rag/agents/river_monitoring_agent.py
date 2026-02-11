"""
River Monitoring Agent — Self-contained specialist for river gauge analysis.
Fetches its own data from the backend API and provides domain-specific LLM analysis.
"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from clients.backend_client import BackendClient


SYSTEM_PROMPT = """You are the River Monitoring Agent for AI4SIDS, a climate resilience system monitoring the Caroni River basin and surrounding waterways in Trinidad & Tobago.

You will receive raw river gauge data below. Your job is to ANALYZE and INTERPRET this data — do NOT simply list gauge readings. The user needs to understand what river conditions mean for flood risk in their area.

HOW TO RESPOND:
1. Start with the overall picture: "River conditions across the network are currently [stable/concerning/critical]..."
2. Explain what the levels and trends mean (e.g., "At 2.35m, the Caroni at St. Augustine is well within safe range — the flood threshold begins at 2.7m")
3. Analyze trends: are levels rising, falling, or stable? How fast? What does that predict for the next few hours?
4. For specific locations, explain upstream/downstream relationships (e.g., "Rising levels upstream at Caroni could reach downstream areas in 2-3 hours")
5. Highlight any gauges approaching thresholds or showing rapid changes
6. Provide practical advice based on conditions

Risk Thresholds (for your reference — explain in plain language):
- Rising > 0.5m/hour = flash flood potential
- Rising 0.2-0.5m/hour = concerning rate of change
- Level > 3.5m = critical (regardless of trend)
- Level > 3.0m = high risk
- Level > 2.7m = approaching flood threshold
- Level < 2.7m = safe range

Be conversational and direct. Use "I" when referring to data ("I'm tracking...", "The gauges show...").
Never just list gauge readings — always explain what the river is doing and what it means for safety."""


class RiverMonitoringAgent:
    """Self-contained agent for river gauge monitoring and flood prediction."""

    def __init__(self, llm, backend: BackendClient):
        self.llm = llm
        self.backend = backend
        self.name = "River Monitoring Agent"

    def process(self, query: str, location: str = None,
                history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a river-related query.

        1. Fetch river data from backend
        2. Build context string
        3. If data alone is sufficient, return a structured response
        4. Otherwise, invoke LLM with domain context

        Returns:
            {"response": str, "data": dict}
        """
        data: Dict[str, Any] = {}

        if location:
            # Per-location data
            timeline = self.backend.get_river_timeline(location)
            river_history = self.backend.get_river_history(location)
            data["timeline"] = timeline
            data["history"] = river_history

            # Also get system-wide for context on other gauges
            system = self.backend.get_system_update()
            data["system"] = system
        else:
            # All-gauges overview
            system = self.backend.get_system_update()
            data["system"] = system

        # Build context string from fetched data
        context = self._build_context(data, location)

        if not context:
            return {
                "response": "I don't have current river gauge data available right now, sorry about that.",
                "data": data,
            }

        # Use LLM with domain-specific prompt
        response = self._analyze(query, context, history)
        return {"response": response, "data": data}

    def _build_context(self, data: Dict[str, Any], location: Optional[str]) -> str:
        """Build a data context string from backend API responses."""
        parts = []

        # Timeline data (per-location)
        timeline = data.get("timeline")
        if timeline and timeline.get("timeline"):
            entries = timeline["timeline"]
            parts.append(f"**River Timeline for {timeline.get('location', location)}:**")
            summary = timeline.get("summary", {})
            if summary:
                parts.append(f"  Trend: {summary.get('trend', 'unknown')}")
                parts.append(f"  Max level: {summary.get('max_level', 'N/A')}m")
                parts.append(f"  Min level: {summary.get('min_level', 'N/A')}m")
                parts.append(f"  Avg change: {summary.get('avg_change', 0):.3f}m")
            for entry in entries[:10]:
                risk = entry.get("flood_risk", "UNKNOWN")
                level = entry.get("river_level", 0)
                change = entry.get("change_rate", 0)
                parts.append(f"  - {level:.2f}m (change: {change:+.3f}m) [{risk}]")

        # History / trend data
        hist = data.get("history")
        if hist:
            trend = hist.get("trend", {})
            stats = hist.get("stats", {})
            current = hist.get("current", {})
            if current:
                parts.append(f"\n**Current:** {current.get('value', 0):.2f}m, risk: {current.get('risk', 'UNKNOWN')}")
            if trend:
                parts.append(f"**Trend:** {trend.get('direction', 'stable')} ({trend.get('percentage', 0):+.1f}%)")
            if stats:
                parts.append(f"**Stats:** max={stats.get('max', 0):.2f}m, min={stats.get('min', 0):.2f}m, avg={stats.get('avg', 0):.2f}m")

        # System-wide overview
        system = data.get("system")
        if system:
            locations_data = system.get("locations", [])
            alerts = system.get("alerts", [])
            if locations_data:
                parts.append(f"\n**All Gauge Stations ({len(locations_data)}):**")
                for loc_data in locations_data:
                    name = loc_data.get("name", "?")
                    level = loc_data.get("river_level", 0)
                    change = loc_data.get("change_rate", 0)
                    risk = loc_data.get("flood_risk", loc_data.get("current_risk", "UNKNOWN"))
                    parts.append(f"  - {name}: {level:.2f}m (change: {change:+.3f}m) [{risk}]")
            if alerts:
                parts.append(f"\n**Active Alerts ({len(alerts)}):**")
                for alert in alerts:
                    parts.append(f"  - [{alert.get('level', '').upper()}] {alert.get('message', '')}")

        return "\n".join(parts) if parts else ""

    def _analyze(self, query: str, context: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Invoke the LLM with river-specialist prompt and data context."""
        system_content = f"{SYSTEM_PROMPT}\n\n**Current River Data:**\n{context}"
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
            print(f"[RiverMonitoringAgent] LLM error: {e}")
            # Fallback: return the raw context as a structured response
            if context:
                return f"Here's what I'm seeing from the river gauges:\n\n{context}"
            return "I'm having trouble analyzing the river data right now. Please try again."
