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
from tools.data_processing import (process_sensor_data, process_river_gauge_data,
                                   process_social_media_data, analyze_river_trends,
                                   analyze_sentiment_trends)
from tools.risk_assessment import assess_flood_risk, generate_recommendations
from tools.document_knowledge import search_knowledge


class ConversationalCoordinator:
    """
    Main coordinator for conversational interactions
    Determines user intent and routes to appropriate specialist agents
    Manages multi-source data integration
    """

    def __init__(self, llm):
        self.llm = llm
        self.name = "AI4SIDS Climate Assistant"
        self.conversation_memory: List[Dict[str, str]] = []
        self.current_data: Optional[Dict[str, Any]] = None
        self.river_data: Optional[Dict[str, Any]] = None
        self.social_data: Optional[Dict[str, Any]] = None
        self.risk_assessments: Dict[str, Any] = {}
        self.last_topic: Optional[str] = None  # Track last discussed topic
        self.last_location: Optional[str] = None  # Track last discussed location

        # Load latest data from all sources
        self._load_latest_data()

    def _load_latest_data(self):
        """Load data from all sources: weather, river gauges, and social media"""
        try:
            sample_dir = DATA_DIR / "sample"

            # Load weather data
            weather_files = [
                f for f in sample_dir.glob("*.csv")
                if 'weather' in f.name.lower() and 'social_media' not in f.name.lower()
            ]

            if weather_files:
                csv_file = str(weather_files[0])
                print(f"[WEATHER] Loading weather data: {weather_files[0].name}")
                self.current_data = process_sensor_data.invoke({"csv_path": csv_file})

                if self.current_data.get("status") == "success":
                    print(f"[OK] Loaded weather data for {len(self.current_data.get('locations', []))} locations")
                else:
                    print(f"[WARNING] Weather data loading issue: {self.current_data.get('error')}")
            else:
                print("[WARNING] No weather data files found")

            # Load river gauge data
            river_files = [
                f for f in sample_dir.glob("*.csv")
                if 'caroni' in f.name.lower() or 'river' in f.name.lower() or 'gauge' in f.name.lower()
            ]

            if river_files:
                csv_file = str(river_files[0])
                print(f"[RIVER] Loading river gauge data: {river_files[0].name}")
                self.river_data = process_river_gauge_data.invoke({"csv_path": csv_file})

                if self.river_data.get("status") == "success":
                    print(f"[OK] Loaded river data for {self.river_data.get('total_gauges', 0)} gauges")
                else:
                    print(f"[WARNING] River data loading issue: {self.river_data.get('error')}")
            else:
                print("[WARNING] No river gauge data files found")

            # Load social media data
            social_files = [
                f for f in sample_dir.glob("*.csv")
                if 'social' in f.name.lower() and 'media' in f.name.lower()
            ]

            if social_files:
                csv_file = str(social_files[0])
                print(f"[SOCIAL] Loading social media data: {social_files[0].name}")
                self.social_data = process_social_media_data.invoke({"csv_path": csv_file})

                if self.social_data.get("status") == "success":
                    print(f"[OK] Loaded social media data ({self.social_data.get('total_posts', 0)} posts)")
                else:
                    print(f"[WARNING] Social media data loading issue: {self.social_data.get('error')}")
            else:
                print("[WARNING] No social media data files found")

            # Pre-compute risk assessments using all data sources
            if self.current_data and self.current_data.get("status") == "success":
                self._compute_all_risks()

        except Exception as e:
            print(f"[ERROR] Error loading data: {str(e)}")

    def _compute_all_risks(self):
        """Pre-compute risk assessments for all locations"""
        if not self.current_data or self.current_data.get("status") != "success":
            return

        locations = self.current_data.get("locations", [])
        print(f" Computing risk assessments for {len(locations)} locations...")

        try:
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
        except Exception as e:
            # Handle encoding errors and other issues gracefully
            error_msg = str(e).encode('ascii', errors='replace').decode('ascii')
            print(f"[WARNING] Risk assessment encountered issue: {error_msg}")
            print(f"[OK] Continuing with {len(self.risk_assessments)} risk assessments computed")

    def _extract_location_from_query(self, query: str) -> Optional[str]:
        """
        Extract location name from user query
        Returns the location if found in our data, None otherwise
        """
        query_lower = query.lower()

        # First check known locations from risk assessments (exact matches)
        for location in self.risk_assessments.keys():
            if location.lower() in query_lower:
                return location

        # Also check common Trinidad locations that might not be in weather data
        # but could be in our raw weather data or mentioned in queries
        common_locations = [
            "Port of Spain", "Arima", "Piarco", "Cunupia", "Chaguanas",
            "San Fernando", "Caroni", "Sangre Grande", "Tunapuna",
            "Diego Martin", "Point Fortin", "Princes Town"
        ]

        for location in common_locations:
            if location.lower() in query_lower:
                # Check if we have weather data for this location in raw data
                if self.current_data and self.current_data.get('raw_data'):
                    for record in self.current_data['raw_data']:
                        if record.get('Location', '').lower() == location.lower():
                            return record.get('Location')
                # Even if not in data, return it so we can give a proper error message
                return location

        return None

    def _determine_intent(self, query: str) -> str:
        """
        Determine user intent from query
        Returns: 'flood_risk', 'weather', 'river', 'social_media', 'evacuation', 'general', 'all_locations'
        """
        query_lower = query.lower()

        # River/gauge queries
        if any(word in query_lower for word in ['river', 'gauge', 'water level', 'caroni', 'rising', 'falling']):
            return 'river'

        # Social media / community sentiment queries
        if any(word in query_lower for word in ['social media', 'sentiment', 'community', 'people saying', 'reports', 'posts']):
            return 'social_media'

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

    def _get_river_info(self, location: str = None) -> str:
        """Get river gauge information in conversational format"""
        if not self.river_data or self.river_data.get("status") != "success":
            return "I don't have current river gauge data available right now, sorry about that."

        gauges = self.river_data.get("gauges", [])

        if location:
            # Filter to gauges near this location
            gauges = [g for g in gauges if location.lower() in g['location'].lower()]

        if not gauges:
            if location:
                return f"I don't have river gauge data near {location}. I'm monitoring other parts of the Caroni River though - would you like to know about those?"
            return "No river gauge data available right now."

        # Count risk levels
        critical_gauges = [g for g in gauges if g['current_level'] > 3.5 or g['change_rate'] > 0.5]
        high_risk_gauges = [g for g in gauges if (g['current_level'] > 3.0 or g['change_rate'] > 0.3) and g not in critical_gauges]
        rising_gauges = [g for g in gauges if g['change_rate'] > 0.1]
        flooding_gauges = [g for g in gauges if g['flood_event']]

        # Start with overall assessment
        if critical_gauges:
            response = f"I need to be straight with you - we have **critical conditions** along the Caroni River right now. "
        elif high_risk_gauges:
            response = f"The Caroni River is showing **elevated risk** at several points. "
        elif rising_gauges:
            response = f"The Caroni River is rising in some areas, so let me give you the details. "
        else:
            response = f"Good news - the Caroni River is relatively stable right now. "

        # Add context about what we're monitoring
        if len(gauges) > 1:
            response += f"I'm tracking {len(gauges)} gauge points from upstream to downstream.\n\n"
        else:
            response += f"Here's what I'm seeing at {gauges[0]['location']}:\n\n"

        # Describe each gauge conversationally
        for i, gauge in enumerate(gauges[:5], 1):
            level = gauge['current_level']
            change = gauge['change_rate']
            loc = gauge['location']

            # Determine urgency
            if level > 3.5 or change > 0.5:
                urgency = "**CRITICAL**"
                intro = "This is urgent -"
            elif level > 3.0 or change > 0.3:
                urgency = "**HIGH RISK**"
                intro = "I'm concerned about"
            elif level > 2.5 or change > 0.2:
                urgency = "**WATCH**"
                intro = "Keep an eye on"
            else:
                urgency = "**NORMAL**"
                intro = "Looking good at"

            response += f"**{loc}** ({urgency}): "

            # Describe the level conversationally
            if level > 3.5:
                response += f"{intro} the water level here is very high at {level:.1f} meters"
            elif level > 3.0:
                response += f"the water is elevated at {level:.1f} meters"
            elif level > 2.5:
                response += f"we're at {level:.1f} meters, which is slightly elevated"
            else:
                response += f"water level is {level:.1f} meters - within normal range"

            # Describe the trend conversationally
            if abs(change) < 0.1:
                response += f", and it's holding steady"
            elif change > 0.5:
                response += f", and it's **rising rapidly** at {abs(change):.1f} meters per hour"
            elif change > 0.2:
                response += f", and it's **rising** at {change:.1f} meters per hour"
            elif change < -0.5:
                response += f", but good news - it's **dropping fast** at {abs(change):.1f} meters per hour"
            elif change < -0.1:
                response += f", and it's **receding** at {abs(change):.1f} meters per hour"

            response += "."

            # Flooding alert
            if gauge['flood_event']:
                response += " ⚠️ **Active flooding reported at this location!**"

            response += "\n\n"

        # Add summary and advice
        if flooding_gauges:
            response += f"\n**Critical Alert:** {len(flooding_gauges)} gauge location(s) are experiencing active flooding. If you're in these areas, move to higher ground immediately."
        elif critical_gauges:
            response += f"\n**Warning:** {len(critical_gauges)} location(s) at critical levels. Flooding is imminent - prepare to evacuate if you're nearby."
        elif rising_gauges:
            response += f"\n**Status:** {len(rising_gauges)} location(s) showing rising water. Keep monitoring the situation closely."
        else:
            response += "\n**Overall:** River conditions are manageable, but stay alert for changing conditions."

        return response.strip()

    def _get_social_media_info(self, community: str = None) -> str:
        """Get social media sentiment information in conversational narrative style"""
        if not self.social_data or self.social_data.get("status") != "success":
            return "I don't have current social media data available right now."

        communities = self.social_data.get("communities", {})
        overall_sentiment = self.social_data.get('latest_sentiment', 0)
        classification = self.social_data.get('sentiment_classification', 'unknown')

        # Count high-activity communities
        active_communities = {name: stats for name, stats in communities.items() if stats['recent_posts'] > 5}
        critical_communities = {name: stats for name, stats in communities.items()
                               if stats['recent_posts'] > 10 and overall_sentiment < -0.3}

        # Start with overall community mood assessment
        response = ""

        if critical_communities:
            response += "**I'm seeing significant concern across our communities right now.** "
            response += f"Social media activity is very high, and the sentiment is strongly negative (around {overall_sentiment:.2f}). "
            response += "This typically means people are actively experiencing or witnessing flooding conditions.\n\n"
        elif overall_sentiment < -0.1 and active_communities:
            response += "**The community mood is shifting towards concern.** "
            response += f"Sentiment has turned negative (around {overall_sentiment:.2f}), and I'm seeing increased social media activity. "
            response += "People are starting to worry about potential flooding.\n\n"
        elif overall_sentiment > 0.1:
            response += "**Good news from the community front.** "
            response += f"Sentiment is positive (around {overall_sentiment:.2f}), and social media activity is calm. "
            response += "People don't seem worried about flooding right now.\n\n"
        else:
            response += "**Community sentiment is neutral at the moment.** "
            response += f"Social media activity is at normal levels, with sentiment around {overall_sentiment:.2f}. "
            response += "No major concerns being expressed.\n\n"

        # Filter to specific community if provided
        target_communities = [community] if community and community in communities else list(communities.keys())

        # Describe each community conversationally
        if len(target_communities) > 1:
            response += "Here's what I'm seeing across the different communities:\n\n"

        for comm in target_communities:
            if comm not in communities:
                continue

            stats = communities[comm]
            posts = stats['recent_posts']

            # Determine urgency and conversational tone
            if posts > 10 and overall_sentiment < -0.3:
                urgency = "**URGENT**"
                intro = "This is concerning -"
            elif posts > 5 and overall_sentiment < -0.1:
                urgency = "**HIGH ACTIVITY**"
                intro = "I'm noticing"
            elif posts > 3:
                urgency = "**ACTIVE**"
                intro = "There's"
            else:
                urgency = "**QUIET**"
                intro = "It's calm here -"

            response += f"**{comm}** ({urgency}): "

            # Describe activity level conversationally
            if posts > 10:
                response += f"{intro} a lot of social media activity here - I've tracked {posts} recent posts. "
                if overall_sentiment < -0.3:
                    response += "The tone is very negative, which suggests people are experiencing or witnessing flooding right now. "
                    response += "This level of panic posting usually means the situation is actively developing."
                elif overall_sentiment < -0.1:
                    response += "People are expressing worry and preparing for potential flooding. "
                    response += "The community is clearly on alert."
                else:
                    response += "Despite high activity, the sentiment isn't particularly negative - could be general weather awareness."
            elif posts > 5:
                response += f"{intro} elevated activity with {posts} recent posts. "
                if overall_sentiment < -0.1:
                    response += "The community is expressing concern about weather conditions and potential flooding risks."
                else:
                    response += "People are discussing the weather, but there's no widespread panic."
            elif posts > 0:
                response += f"{intro} some activity ({posts} recent posts), which is normal baseline chatter about weather conditions."
            else:
                response += f"{intro} no recent social media posts about flooding or weather concerns."

            response += "\n\n"

        # Add contextual summary and actionable insight
        response += "**What this means:** "
        if critical_communities:
            response += f"The high negative sentiment combined with intense posting activity in {len(critical_communities)} "
            response += f"{'community' if len(critical_communities) == 1 else 'communities'} is a strong signal of active flooding conditions. "
            response += "Community reports are often our earliest and most reliable ground truth - when people panic-post, something real is happening."
        elif active_communities:
            response += "Increased community awareness and concern suggests people are seeing warning signs or preparing for potential flooding. "
            response += "This is valuable early warning intelligence."
        elif overall_sentiment > 0.1:
            response += "Calm community sentiment is a good sign - it means people aren't seeing or experiencing flooding conditions. "
            response += "When communities are quiet and positive, it usually aligns with safe conditions on the ground."
        else:
            response += "Normal community activity with neutral sentiment indicates business as usual. "
            response += "No widespread concern or reports of flooding."

        return response.strip()

    def _is_follow_up_question(self, user_message: str, conversation_history: List[Dict[str, str]]) -> bool:
        """
        Detect if this is a follow-up question based on conversation history

        Args:
            user_message: Current user message
            conversation_history: Previous conversation messages

        Returns:
            True if this appears to be a follow-up question
        """
        if not conversation_history or len(conversation_history) < 2:
            return False

        message_lower = user_message.lower()

        # Follow-up indicators
        follow_up_patterns = [
            'what about', 'how about', 'and', 'also', 'too',
            'what should i do', 'should i', 'is it', 'is the',
            'are they', 'are there', 'can i', 'will it',
            'yes', 'no', 'okay', 'thanks', 'tell me more',
            'can you tell me more', 'tell me about', 'what do you mean',
            'you mentioned', 'you said', 'as you mentioned', 'as you said',
            'earlier you', 'why is', 'how is', 'where is',
            'suggest', 'recommend', 'advice', 'evasive', 'actions',
            'what can i', 'how can i', 'what do i'
        ]

        # Pronouns and references that indicate follow-up
        reference_patterns = ['it', 'that', 'this', 'them', 'they', 'there']

        # Check for follow-up patterns
        has_follow_up_pattern = any(pattern in message_lower for pattern in follow_up_patterns)

        # Check for pronouns without explicit topic
        has_pronoun_reference = any(
            message_lower.startswith(ref) or f" {ref} " in message_lower
            for ref in reference_patterns
        )

        # Check for explicit reference phrases that override length requirement
        has_explicit_reference = any(
            ref in message_lower
            for ref in ['you mentioned', 'you said', 'as you mentioned', 'as you said',
                       'earlier you', 'tell me more about', 'can you tell me more']
        )

        # Question length - be more lenient for questions with explicit references
        is_reasonable_length = len(user_message.split()) <= 15  # Increased from 8

        # Follow-up if: (has pattern OR has pronoun) AND reasonable length
        # OR has explicit reference (regardless of length)
        return has_explicit_reference or ((has_follow_up_pattern or has_pronoun_reference) and is_reasonable_length)

    def process_message(self, user_message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Process user message and generate appropriate response with conversational awareness

        Args:
            user_message: The user's question/message
            conversation_history: Previous conversation messages

        Returns:
            Response string
        """
        # Determine if this is a follow-up question
        is_follow_up = self._is_follow_up_question(user_message, conversation_history)

        # Determine intent and extract location
        intent = self._determine_intent(user_message)
        location = self._extract_location_from_query(user_message)

        # Use last location ONLY for follow-up questions, not for new topics
        if not location and self.last_location and is_follow_up:
            location = self.last_location

        print(f" Intent: {intent}, Location: {location}, Follow-up: {is_follow_up}")

        # For follow-up questions, use LLM with full context
        if is_follow_up and len(conversation_history) >= 2:
            return self._handle_conversational_query(user_message, conversation_history, intent, location)

        # Track topic and location for future context
        self.last_topic = intent
        if location:
            self.last_location = location

        # Handle different intents with structured responses
        if intent == 'all_locations':
            return self._format_all_locations_summary()

        elif intent == 'river':
            # River gauge query
            return self._get_river_info(location)

        elif intent == 'social_media':
            # Social media sentiment query
            return self._get_social_media_info(location)

        elif location:
            # Location-specific query
            if intent == 'flood_risk':
                return self._format_location_risk(location)

            elif intent == 'weather':
                weather_info = self._get_weather_info(location)
                # Only add risk info if we have risk assessment for this location
                if location in self.risk_assessments:
                    risk_info = self._format_location_risk(location)
                    return f"{weather_info}\n\n{risk_info}"
                else:
                    return weather_info

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

    def _handle_conversational_query(self, user_message: str, conversation_history: List[Dict[str, str]],
                                     intent: str, location: Optional[str]) -> str:
        """
        Handle follow-up questions using LLM with full conversational context and real-time data

        Args:
            user_message: Current user question
            conversation_history: Previous conversation messages
            intent: Detected intent
            location: Extracted or inferred location

        Returns:
            Conversational response from LLM
        """
        # Build rich context with real-time data
        data_context = ""

        # Add river data if relevant to conversation
        if self.last_topic == 'river' or intent == 'river' or 'river' in user_message.lower():
            if self.river_data and self.river_data.get("status") == "success":
                gauges = self.river_data.get("gauges", [])
                data_context += "\n\n**Current River Gauge Data:**\n"
                for g in gauges[:8]:  # All gauges
                    data_context += f"- {g['location']}: {g['current_level']:.1f}m, "
                    data_context += f"change: {g['change_rate']:+.2f}m/hr"
                    if g['flood_event']:
                        data_context += " (FLOODING!)"
                    data_context += "\n"

        # Add social media data if relevant
        if self.last_topic == 'social_media' or intent == 'social_media' or any(word in user_message.lower() for word in ['community', 'people', 'sentiment']):
            if self.social_data and self.social_data.get("status") == "success":
                data_context += f"\n\n**Community Sentiment Data:**\n"
                data_context += f"Overall sentiment: {self.social_data.get('latest_sentiment', 0):.2f} "
                data_context += f"({self.social_data.get('sentiment_classification', 'unknown')})\n"
                for comm, stats in self.social_data.get('communities', {}).items():
                    data_context += f"- {comm}: {stats['recent_posts']} recent posts\n"

        # Add location-specific risk if relevant
        if location and location in self.risk_assessments:
            risk = self.risk_assessments[location]
            data_context += f"\n\n**{location} Risk Assessment:**\n"
            data_context += f"Risk Level: {risk['risk_level'].upper()}\n"
            data_context += f"Risk Score: {risk['score']}/100\n"
            if risk.get('factors'):
                data_context += f"Factors: {', '.join(risk['factors'])}\n"

        # Build conversational system prompt
        system_prompt = f"""You are the AI4SIDS Climate Resilience Assistant. You're having a conversation with a user about flood risks, weather conditions, river levels, and community sentiment.

**Context:** The user just asked you about something, and now they're following up with another question. Answer their follow-up naturally and conversationally, referencing what you just told them.

**Your personality:**
- Conversational and helpful
- Direct and honest about risks
- Use "I" when referring to data you have ("I'm seeing...", "I'm tracking...")
- Provide actionable advice when asked
- Keep responses concise but complete

**Available Real-Time Data:**{data_context}

**Important:**
- If they ask "is the river rising?" - give a YES/NO answer first, then explain which locations
- If they ask "what should I do?" - provide clear, actionable safety advice based on current risk levels
- If they ask for more details - provide specific data points
- Reference the previous conversation naturally

Answer their question directly and conversationally."""

        # Build messages with conversation history
        messages = [SystemMessage(content=system_prompt)]

        # Add last 3 exchanges for context
        for msg in conversation_history[-6:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))

        # Add current question
        messages.append(HumanMessage(content=user_message))

        # Get LLM response
        try:
            response = self.llm.invoke(messages)

            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)

        except Exception as e:
            print(f" Error in conversational LLM call: {str(e)}")
            # Fallback to structured response
            if intent == 'river':
                return self._get_river_info(location)
            elif intent == 'social_media':
                return self._get_social_media_info(location)
            else:
                return "I'm having trouble processing that follow-up. Could you rephrase your question?"

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
        data_sources = []
        if self.current_data and self.current_data.get("status") == "success":
            data_sources.append("✅ Weather sensors")
        if self.river_data and self.river_data.get("status") == "success":
            data_sources.append(f"✅ River gauges ({self.river_data.get('total_gauges', 0)} locations)")
        if self.social_data and self.social_data.get("status") == "success":
            data_sources.append(f"✅ Social media ({self.social_data.get('total_posts', 0)} posts)")

        context = f"""You are an AI assistant for the AI4SIDS Climate Resilience System.

Available Data Sources:
{chr(10).join(data_sources) if data_sources else '❌ No data currently available'}

Monitored Locations:
- {len(self.risk_assessments)} locations: {', '.join(self.risk_assessments.keys())}
- Multi-source risk assessments (weather + river + community reports)
- Knowledge base of climate and flood research documents

You can help users with:
1. Checking flood risk for specific locations (e.g., "What's the risk in Arima?")
2. Getting weather information
3. River gauge levels and trends (e.g., "What's the Caroni River status?")
4. Community sentiment and social media reports (e.g., "What are people saying in Piarco?")
5. Evacuation guidance
6. General disaster preparedness questions
7. Overview of all locations
8. Climate and flood-related information from research documents

Current high-risk areas: {', '.join([loc for loc, risk in self.risk_assessments.items() if risk['risk_level'] in ['high', 'critical']]) or 'None'}

{knowledge_context}

Please provide helpful, concise responses using real-time data from weather sensors, river gauges, and community reports. If the user asks about a specific location, tell them which locations you have data for."""

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
