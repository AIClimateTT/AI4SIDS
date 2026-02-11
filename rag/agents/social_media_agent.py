"""
Social Media Intelligence Agent — Self-contained specialist for community sentiment analysis.
Fetches its own data from the backend API and provides domain-specific LLM analysis.
"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from clients.backend_client import BackendClient


SYSTEM_PROMPT = """You are the Social Media Intelligence Agent for AI4SIDS, a climate resilience system monitoring community sentiment in Trinidad & Tobago.

You will receive aggregated social media data below. Your job is to ANALYZE and INTERPRET this data — do NOT simply list sentiment scores and post counts. The user needs to understand what communities are saying and feeling, and what that means for situational awareness.

HOW TO RESPOND:
1. Start with the overall mood: "Community sentiment is currently [calm/concerned/alarmed]..."
2. Explain what the sentiment scores mean in human terms (e.g., "A sentiment of 0.05 is essentially neutral — people aren't worried right now")
3. Identify which communities are most active or concerned, and speculate why
4. Compare social media reports against sensor data: are people's experiences matching what the instruments show?
5. Flag any discrepancies (e.g., "Sensors show safe conditions but community posts suggest localized issues — worth investigating")
6. Note activity levels: low activity during a storm could mean comms are down, not that everything is fine

Sentiment Scale (for your reference — explain in plain language):
- Highly Negative (< -0.3): Panic, fear, active flooding reports
- Negative (-0.3 to -0.1): Concern, worry, preparation activity
- Neutral (-0.1 to 0.1): Normal chatter, no alarm
- Positive (> 0.1): Calm, confident, possibly recovery

Be conversational and direct. Use "I" when referring to data ("I'm seeing...", "The community is...").
Never just list sentiment numbers — always explain what people are feeling and what it means for the situation."""


class SocialMediaAgent:
    """Self-contained agent for community sentiment and social media intelligence."""

    def __init__(self, llm, backend: BackendClient):
        self.llm = llm
        self.backend = backend
        self.name = "Social Media Intelligence Agent"

    def process(self, query: str, location: str = None,
                history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a social-media / sentiment query.

        Returns:
            {"response": str, "data": dict}
        """
        data: Dict[str, Any] = {}

        # Always fetch the aggregate summary
        social = self.backend.get_social_summary()
        data["social_summary"] = social

        # If a location was specified, also get per-location real-time data
        if location:
            real_time = self.backend.get_real_time(location)
            data["real_time"] = real_time

        context = self._build_context(data, location)

        if not context:
            return {
                "response": "I don't have current social media data available right now.",
                "data": data,
            }

        response = self._analyze(query, context, history)
        return {"response": response, "data": data}

    def _build_context(self, data: Dict[str, Any], location: Optional[str]) -> str:
        """Build a data context string from backend API responses."""
        parts = []

        social = data.get("social_summary")
        if social:
            avg = social.get("overall_avg_sentiment", 0)
            classification = social.get("sentiment_classification", "unknown")
            total = social.get("total_posts", 0)
            parts.append(f"**Overall Community Sentiment:** {avg:.3f} ({classification})")
            parts.append(f"**Total Posts Tracked:** {total}")

            locations_data = social.get("locations", [])
            if locations_data:
                parts.append(f"\n**Per-Community Breakdown ({len(locations_data)} communities):**")
                for loc in locations_data:
                    name = loc.get("name", "?")
                    posts = loc.get("post_count", 0)
                    score = loc.get("sentiment_score", 0)
                    activity = loc.get("activity_level", "LOW")
                    parts.append(f"  - {name}: {posts} posts, sentiment {score:.3f} [{activity}]")

        # Per-location real-time social data
        real_time = data.get("real_time")
        if real_time:
            social_activity = real_time.get("social_activity", {})
            if social_activity:
                loc_name = real_time.get("location", location or "?")
                parts.append(f"\n**{loc_name} Social Activity (real-time):**")
                parts.append(f"  Post count: {social_activity.get('post_count', 0)}")
                parts.append(f"  Sentiment: {social_activity.get('sentiment_score', 0):.3f} ({social_activity.get('sentiment_level', 'Unknown')})")
                parts.append(f"  Activity level: {social_activity.get('activity_level', 'LOW')}")
                recent_posts = social_activity.get("recent_posts", [])
                if recent_posts:
                    parts.append("  Recent posts:")
                    for post in recent_posts[:3]:
                        parts.append(f"    - \"{post}\"")

        return "\n".join(parts) if parts else ""

    def _analyze(self, query: str, context: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Invoke the LLM with social-media-specialist prompt and data context."""
        system_content = f"{SYSTEM_PROMPT}\n\n**Current Social Media Data:**\n{context}"
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
            print(f"[SocialMediaAgent] LLM error: {e}")
            if context:
                return f"Here's what I'm seeing from community reports:\n\n{context}"
            return "I'm having trouble analyzing community sentiment right now. Please try again."
