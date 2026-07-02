"""
Conversational Coordinator Agent
=================================
Thin router that detects user intent and delegates to specialist agents.
Uses a single LLM call to classify intent AND extract/match location.
Each agent fetches its own data from the backend API and runs domain-specific analysis.
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from clients.backend_client import BackendClient
from agents.river_monitoring_agent import RiverMonitoringAgent
from agents.social_media_agent import SocialMediaAgent
from agents.flood_risk_agent import FloodRiskAgent
from agents.weather_agent import WeatherAgent
from agents.knowledge_agent import KnowledgeAgent


# This prompt template has {locations} injected at runtime
ROUTER_PROMPT_TEMPLATE = """You are a routing assistant for a climate resilience system monitoring Trinidad & Tobago.

Given a user message, determine TWO things:
1. **intent** — what the user wants
2. **location** — which monitored location they're asking about (if any)

INTENTS (pick exactly one):
- flood_risk — wants current flood risk data, danger levels, safety assessment. ("Is Cunupia safe?", "What's the flood risk?")
- weather — wants current weather readings: rainfall, temperature, wind, humidity. ("What's the weather in Piarco?", "Is it raining?")
- river — wants river gauge data, water levels, trends. ("What are the river levels?", "Is the water rising?")
- social_media — wants community sentiment, social media reports. ("What are people saying?", "Community mood?")
- evacuation — wants evacuation advice, shelter info, emergency actions. ("Should I evacuate?", "Where do I go?")
- all_locations — wants a summary across ALL locations. ("Overview of everything", "All areas status")
- knowledge — educational, conceptual, or general question about climate, floods, rivers, weather, or disaster preparedness. ("How does weather affect the environment?", "What causes flooding?", "Tell me about SIDS")
- off_topic — the message has NO meaningful connection to weather, flooding, rivers, climate, safety, or disaster preparedness. The entire message is about something unrelated.

IMPORTANT — distinguish data requests from educational questions:
- "What's the weather in Piarco?" → weather (wants current sensor data)
- "How does weather affect flooding?" → knowledge (educational question)
- "What is flood risk?" → knowledge (conceptual question)
- "What's the flood risk in Cunupia?" → flood_risk (wants current data)

IMPORTANT — off_topic vs. conversational messages with a climate angle:
- Use off_topic ONLY when the message has NO connection to climate, weather, flooding, rivers, safety, or disaster preparedness.
- If a message is conversational but contains a real climate/safety question, classify by that question — NOT off_topic.
- Examples:
  - "How do I cook pork?" → off_topic (zero climate relevance)
  - "What's the best recipe for curry?" → off_topic
  - "What's the weather like in Cunupia? I want to know if it's safe to go get groceries" → weather (the real question is about weather/safety)
  - "Is it raining? I need to pick up my kids" → weather (asking about current conditions)
  - "Should I go out? I heard there's flooding" → flood_risk (safety question)

LOCATIONS — these are the monitored locations. Match the user's message to the EXACT name from this list, even if they use abbreviations, nicknames, or misspellings:
{locations}

If the user mentions a place not in this list, set location to null.
If the user doesn't mention any location, set location to null.

Respond with ONLY valid JSON, no explanation:
{{"intent": "...", "location": "..." or null}}"""


class ConversationalCoordinator:
    """
    Thin router for conversational interactions.
    Uses a single LLM call to classify intent and extract location,
    then delegates to the appropriate specialist agent.
    """

    def __init__(self, llm, backend_client: BackendClient):
        self.llm = llm
        self.backend = backend_client
        self.name = "AI4SIDS Climate Assistant"

        # Initialize specialist agents
        self.river_agent = RiverMonitoringAgent(llm, backend_client)
        self.social_agent = SocialMediaAgent(llm, backend_client)
        self.flood_risk_agent = FloodRiskAgent(llm, backend_client)
        self.weather_agent = WeatherAgent(llm, backend_client)
        self.knowledge_agent = KnowledgeAgent(llm)

        # Conversation state
        self.last_topic: Optional[str] = None
        self.last_location: Optional[str] = None

    # ------------------------------------------------------------------
    # Combined intent + location classification (single LLM call)
    # ------------------------------------------------------------------

    def _classify(self, query: str) -> Dict[str, Any]:
        """
        Single LLM call to determine intent and extract location.
        Returns {"intent": str, "location": str | None}.
        Falls back to keyword-based classification on failure.
        """
        # Build the location list for the prompt
        location_names = self.backend.get_location_names()
        if location_names:
            locations_str = "\n".join(f"- {name}" for name in location_names)
        else:
            locations_str = "- St. Augustine\n- Cunupia\n- Piarco\n- St. Helena\n- Chaguanas\n- Kelly Village\n- Las Lomas\n- Caroni"

        prompt = ROUTER_PROMPT_TEMPLATE.format(locations=locations_str)

        try:
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=query),
            ]
            response = self.llm.invoke(messages)
            raw = (response.content if hasattr(response, "content") else str(response)).strip()

            # Parse JSON from the response (handle cases where LLM wraps in markdown)
            json_str = raw
            if "```" in json_str:
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                json_str = json_str.strip()

            parsed = json.loads(json_str)

            intent = parsed.get("intent", "knowledge").lower().strip()
            location = parsed.get("location")

            # Validate intent
            valid_intents = {
                "flood_risk", "weather", "river", "social_media",
                "evacuation", "all_locations", "knowledge", "off_topic",
            }
            if intent not in valid_intents:
                print(f"[Coordinator] LLM returned invalid intent '{intent}', falling back")
                return self._keyword_classify(query)

            # Validate location against known names (exact match)
            if location:
                matched = None
                for name in location_names:
                    if name.lower() == location.lower():
                        matched = name
                        break
                location = matched  # None if LLM hallucinated a location not in the list

            print(f"[Coordinator] LLM classified → intent={intent}, location={location}")
            return {"intent": intent, "location": location}

        except (json.JSONDecodeError, KeyError) as e:
            print(f"[Coordinator] LLM JSON parse failed: {e}, falling back to keywords")
        except Exception as e:
            print(f"[Coordinator] LLM classification failed: {e}, falling back to keywords")

        return self._keyword_classify(query)

    def _keyword_classify(self, query: str) -> Dict[str, Any]:
        """Fallback keyword-based intent + location extraction."""
        return {
            "intent": self._keyword_intent(query),
            "location": self._keyword_location(query),
        }

    def _keyword_intent(self, query: str) -> str:
        """Fallback keyword-based intent detection."""
        q = query.lower()

        # Educational / conceptual patterns take priority
        educational_starters = [
            "how does", "how do", "why does", "why do", "what is", "what are",
            "what causes", "explain", "tell me about", "describe",
            "what happens when", "can you explain", "how can",
        ]
        if any(q.startswith(p) or f" {p} " in f" {q} " for p in educational_starters):
            if not self._keyword_location(query):
                return "knowledge"

        if any(w in q for w in ["river", "gauge", "water level"]):
            return "river"
        if any(w in q for w in ["social media", "sentiment", "community", "people saying", "reports", "posts"]):
            return "social_media"
        if any(w in q for w in ["flood", "flooding", "risk", "danger", "safe"]):
            return "flood_risk"
        if any(w in q for w in ["weather", "rain", "rainfall", "storm", "wind", "temperature"]):
            return "weather"
        if any(w in q for w in ["evacuate", "evacuation", "leave", "shelter"]):
            return "evacuation"
        if any(w in q for w in ["all locations", "everywhere", "overall", "summary", "all areas"]):
            return "all_locations"

        # If no climate-related keyword found at all, treat as off_topic
        climate_keywords = [
            "weather", "rain", "flood", "river", "water", "storm", "wind",
            "temperature", "humidity", "safe", "safety", "risk", "danger",
            "evacuate", "shelter", "climate", "disaster", "preparedness",
            "community", "sensor", "gauge", "level", "trinidad", "tobago",
        ]
        if not any(w in q for w in climate_keywords):
            return "off_topic"

        return "knowledge"

    def _keyword_location(self, query: str) -> Optional[str]:
        """Fallback keyword-based location extraction."""
        query_lower = query.lower()

        known_names = self.backend.get_location_names()
        for name in known_names:
            if name.lower() in query_lower:
                return name

        common_locations = [
            "Port of Spain", "Arima", "Piarco", "Cunupia", "Chaguanas",
            "San Fernando", "Caroni", "Sangre Grande", "Tunapuna",
            "Diego Martin", "Point Fortin", "Princes Town",
            "St. Augustine", "St. Helena", "Kelly Village", "Las Lomas",
        ]
        for loc in common_locations:
            if loc.lower() in query_lower:
                return loc

        return None

    # ------------------------------------------------------------------
    # Follow-up detection
    # ------------------------------------------------------------------

    def _is_follow_up_question(self, user_message: str,
                                conversation_history: List[Dict[str, str]]) -> bool:
        """Detect if this is a follow-up question based on conversation history."""
        if not conversation_history or len(conversation_history) < 2:
            return False

        message_lower = user_message.lower()

        follow_up_patterns = [
            'what about', 'how about', 'and', 'also', 'too',
            'what should i do', 'should i', 'is it', 'is the',
            'are they', 'are there', 'can i', 'will it',
            'yes', 'no', 'okay', 'thanks', 'tell me more',
            'can you tell me more', 'tell me about', 'what do you mean',
            'you mentioned', 'you said', 'as you mentioned', 'as you said',
            'earlier you', 'why is', 'how is', 'where is',
            'suggest', 'recommend', 'advice', 'actions',
            'what can i', 'how can i', 'what do i'
        ]

        reference_patterns = ['it', 'that', 'this', 'them', 'they', 'there']

        has_follow_up_pattern = any(p in message_lower for p in follow_up_patterns)

        has_pronoun_reference = any(
            message_lower.startswith(ref) or f" {ref} " in message_lower
            for ref in reference_patterns
        )

        has_explicit_reference = any(
            ref in message_lower
            for ref in ['you mentioned', 'you said', 'as you mentioned',
                        'as you said', 'earlier you', 'tell me more about',
                        'can you tell me more']
        )

        is_reasonable_length = len(user_message.split()) <= 15

        return has_explicit_reference or (
            (has_follow_up_pattern or has_pronoun_reference) and is_reasonable_length
        )

    # ------------------------------------------------------------------
    # Main router
    # ------------------------------------------------------------------

    def process_message(self, user_message: str,
                        conversation_history: List[Dict[str, str]], user_id: str) -> str:
        """
        Process user message: classify intent + location in one LLM call,
        then delegate to the appropriate specialist agent.
        """
        is_follow_up = self._is_follow_up_question(user_message, conversation_history)

        # Single LLM call for both intent and location
        classification = self._classify(user_message)
        intent = classification["intent"]
        location = classification["location"]

        # Use last location for follow-up questions only
        if not location and self.last_location and is_follow_up:
            location = self.last_location

        print(f"[Coordinator] Intent: {intent}, Location: {location}, Follow-up: {is_follow_up}")

        # Track topic and location
        self.last_topic = intent
        if location:
            self.last_location = location

        # Guard: refuse off-topic requests entirely
        if intent == 'off_topic':
            return (
                "I'm a climate resilience assistant for Trinidad & Tobago — I can only help with "
                "weather conditions, flood risk, river levels, community safety reports, and "
                "disaster preparedness. Is there anything along those lines I can help you with?"
            )

        # Route to the appropriate specialist agent
        try:
            if intent == 'river':
                result = self.river_agent.process(user_message, location, conversation_history)

            elif intent == 'social_media':
                result = self.social_agent.process(user_message, location, conversation_history)

            elif intent in ('flood_risk', 'evacuation'):
                result = self.flood_risk_agent.process(user_message, location, conversation_history)

            elif intent == 'weather':
                result = self.weather_agent.process(user_message, location, conversation_history)

            elif intent == 'all_locations':
                result = self.flood_risk_agent.process(user_message, location=None, history=conversation_history)

            else:
                # General / knowledge query
                result = self.knowledge_agent.process(user_message, location, conversation_history)

            # Begin Kwasi Code
            # I need to be able to capture information about the request and response. for analytics (input/output tokens and whether RAG was used or not. For now I'm dumping the data into a file for future analysis. Real-world testing is being done right now by stakeholders)
            try:
                with open("./data/result_logs.json", "a", encoding="utf-8") as f:
                    log_entry = {
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat(),
                        "intent": intent,
                        "location": location,
                        "user_message": user_message,
                        "result": result
                    }
                    # default=str handles any non-serializable objects recursively
                    f.write(json.dumps(log_entry, default=str) + "\n")
            except Exception as e:
                print(f"[Coordinator] Failed to log result: {e}")
            # End Kwasi Code
            return result.get("response", "I'm sorry, I couldn't generate a response.")

        except Exception as e:
            print(f"[Coordinator] Agent error: {e}")
            return (
                "I'm having trouble processing your request right now. "
                "Please try again, or ask about a specific topic like flood risk, "
                "river conditions, weather, or community sentiment."
            )
