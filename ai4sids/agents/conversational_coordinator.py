"""
Conversational Coordinator Agent
=================================
Orchestrates conversational interactions and routes queries to appropriate specialists
"""
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config.settings import DATA_DIR
from tools.data_processing import process_sensor_data
from tools.risk_assessment import assess_flood_risk, generate_recommendations
from tools.document_knowledge import search_knowledge


class ConversationalCoordinator:
    """
    Main coordinator for conversational interactions
    Determines user intent and routes to appropriate specialist agents
    """

    def __init__(self, llm):
        self.llm = llm
        self.name = "AI4SIDS Climate Assistant"
        self.conversation_memory: List[Dict[str, str]] = []
        self.current_data: Optional[Dict[str, Any]] = None
        self.risk_assessments: Dict[str, Any] = {}

        # Load latest weather data on initialization
        self._load_latest_data()

    def _load_latest_data(self):
        """Load the most recent weather data"""
        try:
            sample_dir = DATA_DIR / "sample"
            weather_files = [
                f for f in sample_dir.glob("*.csv")
                if 'weather' in f.name.lower() or 'Weather' in f.name
            ]

            if weather_files:
                csv_file = str(weather_files[0])
                print(f" Loading weather data: {weather_files[0].name}")
                self.current_data = process_sensor_data.invoke({"csv_path": csv_file})

                if self.current_data.get("status") == "success":
                    print(f"OK Loaded data for {len(self.current_data.get('locations', []))} locations")
                    # Pre-compute risk assessments for all locations
                    self._compute_all_risks()
                else:
                    print(f"WARNING  Data loading issue: {self.current_data.get('error')}")
            else:
                print("WARNING  No weather data files found")
        except Exception as e:
            print(f" Error loading data: {str(e)}")

    def _compute_all_risks(self):
        """Pre-compute risk assessments for all locations"""
        if not self.current_data or self.current_data.get("status") != "success":
            return

        locations = self.current_data.get("locations", [])
        print(f" Computing risk assessments for {len(locations)} locations...")

        for location in locations:
            risk = assess_flood_risk.invoke({
                "sensor_data": self.current_data,
                "location": location
            })

            # Add recommendations
            recommendations = generate_recommendations.invoke({
                "risk_level": risk["risk_level"]
            })
            risk["recommendations"] = recommendations
            self.risk_assessments[location] = risk

        print("OK Risk assessments ready")

    def _extract_location_from_query(self, query: str) -> Optional[str]:
        """
        Extract location name from user query
        Returns the location if found in our data, None otherwise
        """
        query_lower = query.lower()

        # Check each known location
        for location in self.risk_assessments.keys():
            if location.lower() in query_lower:
                return location

        return None

    def _determine_intent(self, query: str) -> str:
        """
        Determine user intent from query
        Returns: 'flood_risk', 'weather', 'evacuation', 'general', 'all_locations'
        """
        query_lower = query.lower()

        # Flood risk queries
        if any(word in query_lower for word in ['flood', 'flooding', 'risk', 'danger', 'safe']):
            return 'flood_risk'

        # Weather queries
        if any(word in query_lower for word in ['weather', 'rain', 'rainfall', 'storm', 'wind']):
            return 'weather'

        # Evacuation queries
        if any(word in query_lower for word in ['evacuate', 'evacuation', 'leave', 'shelter']):
            return 'evacuation'

        # All locations overview
        if any(phrase in query_lower for phrase in ['all locations', 'everywhere', 'overall', 'summary', 'all areas']):
            return 'all_locations'

        return 'general'

    def _format_location_risk(self, location: str) -> str:
        """Format risk information for a specific location in conversational tone"""
        risk = self.risk_assessments.get(location)

        if not risk:
            return f"I don't have current data for {location}, sorry about that."

        # Start with a natural opening based on risk level
        if risk['risk_level'] == 'critical':
            opening = f"I need to be honest with you - the situation in {location} is **critical** right now. "
        elif risk['risk_level'] == 'high':
            opening = f"Yes, there's a **high risk** of flooding in {location} at the moment. "
        elif risk['risk_level'] == 'moderate':
            opening = f"There's a **moderate risk** of flooding in {location} right now. "
        else:
            opening = f"Good news - the flood risk in {location} is currently **low**. "

        response = opening + f"The risk score is {risk['score']} out of 100.\n\n"

        # Explain what's causing concern
        if risk.get('factors') and risk['factors'] != ["Normal conditions"]:
            if risk['risk_level'] in ['critical', 'high']:
                response += "Here's what's concerning me:\n"
            else:
                response += "Here's what I'm seeing:\n"
            for factor in risk['factors']:
                response += f"- {factor}\n"
            response += "\n"

        # Give personalized recommendations
        if risk.get('recommendations'):
            if risk['risk_level'] == 'critical':
                response += "**Please take these actions immediately:**\n"
            elif risk['risk_level'] == 'high':
                response += "**Here's what you should do:**\n"
            elif risk['risk_level'] == 'moderate':
                response += "**I'd recommend:**\n"
            else:
                response += "**Just to be safe:**\n"

            for i, rec in enumerate(risk['recommendations'][:5], 1):
                response += f"{i}. {rec}\n"

        # Add a closing based on severity
        if risk['risk_level'] == 'critical':
            response += "\nPlease stay safe and follow emergency services instructions."
        elif risk['risk_level'] == 'high':
            response += "\nStay alert and keep monitoring the situation."
        elif risk['risk_level'] == 'moderate':
            response += "\nKeep an eye on updates, but no need to panic."
        else:
            response += "\nYou should be fine, but it's always good to stay prepared!"

        return response

    def _format_all_locations_summary(self) -> str:
        """Format summary of all locations"""
        if not self.risk_assessments:
            return "I don't have current risk assessment data available."

        # Group by risk level
        critical = []
        high = []
        moderate = []
        low = []

        for location, risk in self.risk_assessments.items():
            level = risk['risk_level']
            if level == 'critical':
                critical.append(location)
            elif level == 'high':
                high.append(location)
            elif level == 'moderate':
                moderate.append(location)
            else:
                low.append(location)

        response = f"**Climate Risk Assessment - All Locations**\n\n"
        response += f" **Total Locations Monitored:** {len(self.risk_assessments)}\n\n"

        if critical:
            response += f" **CRITICAL RISK** ({len(critical)}):\n"
            for loc in critical:
                response += f"   {loc} (Score: {self.risk_assessments[loc]['score']}/100)\n"
            response += "\n"

        if high:
            response += f" **HIGH RISK** ({len(high)}):\n"
            for loc in high:
                response += f"   {loc} (Score: {self.risk_assessments[loc]['score']}/100)\n"
            response += "\n"

        if moderate:
            response += f" **MODERATE RISK** ({len(moderate)}):\n"
            for loc in moderate:
                response += f"   {loc} (Score: {self.risk_assessments[loc]['score']}/100)\n"
            response += "\n"

        if low:
            response += f" **LOW RISK** ({len(low)}):\n"
            for loc in low:
                response += f"   {loc} (Score: {self.risk_assessments[loc]['score']}/100)\n"
            response += "\n"

        # Add priority alerts
        if critical or high:
            response += "\n **Priority Alerts:**\n"
            if critical:
                response += f"  WARNING  {len(critical)} location(s) at CRITICAL risk - immediate action recommended\n"
            if high:
                response += f"  WARNING  {len(high)} location(s) at HIGH risk - prepare for possible evacuation\n"

        return response

    def _get_weather_info(self, location: str) -> str:
        """Get current weather information for a location in conversational tone"""
        if not self.current_data or not self.current_data.get('raw_data'):
            return f"I don't have current weather data for {location}, sorry."

        location_data = [
            d for d in self.current_data['raw_data']
            if d.get('Location') == location
        ]

        if not location_data:
            return f"I don't have weather data for {location}."

        latest = location_data[0]

        rainfall = latest.get('Actual Rainfall (mm)', 0)
        windspeed = latest.get('Actual Windspeed (km/h)', 0)
        humidity = latest.get('Actual Humidity (%)', 0)
        conditions = latest.get('Actual Storm', 'Unknown')

        # Make it conversational
        response = f"Right now in {location}, "

        if conditions == 'Storm':
            response += f"we're experiencing storm conditions. "
        elif conditions == 'Rainy':
            response += f"it's rainy. "
        else:
            response += f"the weather is relatively calm. "

        response += f"We've had {rainfall:.1f}mm of rainfall, "

        if windspeed > 30:
            response += f"with strong winds at {windspeed:.1f} km/h, "
        elif windspeed > 20:
            response += f"with moderate winds at {windspeed:.1f} km/h, "
        else:
            response += f"with light winds at {windspeed:.1f} km/h, "

        response += f"and humidity is at {humidity:.1f}%.\n\n"

        return response

    def process_message(self, user_message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Process user message and generate appropriate response

        Args:
            user_message: The user's question/message
            conversation_history: Previous conversation messages

        Returns:
            Response string
        """
        # Determine intent and extract location
        intent = self._determine_intent(user_message)
        location = self._extract_location_from_query(user_message)

        print(f" Intent: {intent}, Location: {location}")

        # Handle different intents
        if intent == 'all_locations':
            return self._format_all_locations_summary()

        elif location:
            # Location-specific query
            if intent == 'flood_risk':
                return self._format_location_risk(location)

            elif intent == 'weather':
                weather_info = self._get_weather_info(location)
                risk_info = self._format_location_risk(location)
                return f"{weather_info}\n\n{risk_info}"

            elif intent == 'evacuation':
                risk = self.risk_assessments.get(location)
                if not risk:
                    return f"I don't have current risk data for {location}, so I can't give you evacuation advice right now."

                if risk['risk_level'] == 'critical':
                    response = f"Listen, the situation in {location} is **critical**. If authorities have issued an evacuation order, you need to leave **immediately**. Don't wait.\n\n"
                    response += "Here's what to do right now:\n"
                    for i, rec in enumerate(risk['recommendations'][:3], 1):
                        response += f"{i}. {rec}\n"
                    response += "\nPlease take this seriously and stay safe."

                elif risk['risk_level'] == 'high':
                    response = f"Given the **high risk** in {location}, I'd strongly recommend preparing to evacuate. You might not need to leave right this second, but be ready to go at a moment's notice.\n\n"
                    response += "Here's what you should do:\n"
                    for i, rec in enumerate(risk['recommendations'][:3], 1):
                        response += f"{i}. {rec}\n"
                    response += "\nStay alert and follow official guidance."

                elif risk['risk_level'] == 'moderate':
                    response = f"You don't need to evacuate {location} right now - the risk is moderate. But it's smart to be prepared just in case things change.\n\n"
                    response += "I'd suggest:\n"
                    for i, rec in enumerate(risk['recommendations'][:3], 1):
                        response += f"{i}. {rec}\n"
                    response += "\nKeep monitoring the situation, but no need to panic."

                else:
                    response = f"Good news - you don't need to evacuate {location}. The flood risk is currently low, so you're safe to stay put.\n\n"
                    response += "That said, it's always good to be prepared:\n"
                    for i, rec in enumerate(risk['recommendations'][:2], 1):
                        response += f"{i}. {rec}\n"
                    response += "\nYou should be fine!"

                return response

            else:
                # General query about a location
                return self._format_location_risk(location)

        else:
            # No specific location - use LLM for general response
            return self._handle_general_query(user_message, conversation_history)

    def _handle_general_query(self, user_message: str, conversation_history: List[Dict[str, str]]) -> str:
        """Handle general queries using LLM with context and RAG"""

        # Search knowledge base for relevant information
        knowledge_results = search_knowledge(user_message, top_k=3)

        knowledge_context = ""
        if knowledge_results:
            knowledge_context = "\n\nRelevant Knowledge from Documents:\n"
            for i, result in enumerate(knowledge_results, 1):
                knowledge_context += f"\n{i}. From '{result['source']}':\n{result['content'][:300]}...\n"

        # Build context about available data
        context = f"""You are an AI assistant for the AI4SIDS Climate Resilience System.

Available Data:
- {len(self.risk_assessments)} locations being monitored: {', '.join(self.risk_assessments.keys())}
- Real-time weather data and flood risk assessments
- Knowledge base of climate and flood research documents

You can help users with:
1. Checking flood risk for specific locations (e.g., "What's the risk in Arima?")
2. Getting weather information
3. Evacuation guidance
4. General disaster preparedness questions
5. Overview of all locations
6. Climate and flood-related information from research documents

Current high-risk areas: {', '.join([loc for loc, risk in self.risk_assessments.items() if risk['risk_level'] in ['high', 'critical']])}

{knowledge_context}

Please provide helpful, concise responses using both real-time data and knowledge base information when relevant. If the user asks about a specific location, tell them which locations you have data for."""

        # Build prompt with conversation history
        messages = [SystemMessage(content=context)]

        # Add conversation history
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))

        # Add current message
        messages.append(HumanMessage(content=user_message))

        try:
            response = self.llm.invoke(messages)

            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)

        except Exception as e:
            print(f" Error in LLM call: {str(e)}")
            return f"I'm here to help with flood risk assessment and disaster preparedness. I currently have data for these locations: {', '.join(self.risk_assessments.keys())}. What would you like to know?"
