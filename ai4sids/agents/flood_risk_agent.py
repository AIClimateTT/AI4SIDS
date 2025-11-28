"""
Flood Risk Assessment Agent - Real-time risk scoring
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.risk_assessment import assess_flood_risk, generate_recommendations

class FloodRiskAgent:
    """
    Agent responsible for:
    - Synthesizing data from weather sensors, river gauges, and social media
    - Analyzing current weather conditions
    - Assessing flood risk for each location
    - Cross-validating data sources
    - Assigning risk levels (LOW, MODERATE, HIGH, CRITICAL)
    - Providing actionable recommendations
    """

    def __init__(self, llm):
        self.llm = llm
        self.name = "Flood Risk Assessment Agent"

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Flood Risk Assessment Agent for AI4SIDS Climate Resilience System.

Your responsibilities:
1. Synthesize data from multiple sources: weather sensors, river gauges, and social media
2. Cross-validate data sources to ensure accuracy
3. Analyze current weather conditions, river levels, and community sentiment
4. Consider: rainfall accumulation, river gauge levels, storm intensity, terrain vulnerability, and community reports
5. Assign risk levels (LOW, MODERATE, HIGH, CRITICAL) for each location
6. Identify discrepancies between data sources (e.g., sensors say safe but community reports flooding)
7. Provide clear, actionable recommendations for each risk level

Multi-Source Risk Assessment Framework:
- If ALL sources agree = HIGH CONFIDENCE in assessment
- If sources disagree = FLAG DISCREPANCY and recommend investigation
- Social media panic + rising river + heavy rain = CRITICAL (multi-factor confirmation)
- Social media calm + sensors show flooding = INVESTIGATE (possible sensor error or delayed awareness)

Risk assessment has been calculated using weather, river, and social media data.
Provide a comprehensive summary of the overall situation, highlighting:
- Multi-source risk confirmations
- Any data discrepancies that need investigation
- Key concerns for HIGH or CRITICAL risk areas

Be clear, direct, and evidence-based."""),
            MessagesPlaceholder(variable_name="messages"),
        ])
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess flood risk for all locations using multi-source data

        Args:
            state: Current agent state with weather, river, and social media data

        Returns:
            Updated state with comprehensive risk assessments
        """
        print(f"\n{'='*60}")
        print(f"🤖 {self.name} - Synthesizing Multi-Source Risk Assessment")
        print(f"{'='*60}")

        messages = state["messages"]
        current_data = state.get("current_data", {})
        river_data = state.get("river_data", {})
        social_data = state.get("social_media_data", {})
        risk_assessments = {}

        # Assess risk for each location
        if current_data.get("status") == "success" and "locations" in current_data:
            print(f"\n[FLOOD] Assessing {len(current_data['locations'])} locations...")

            for location in current_data["locations"]:
                # Base weather risk
                risk = assess_flood_risk.invoke({
                    "sensor_data": current_data,
                    "location": location
                })

                # Enhance with river gauge data
                if river_data.get("status") == "success":
                    river_risk = self._assess_river_risk(river_data, location)
                    if river_risk:
                        risk = self._merge_risk_assessments(risk, river_risk, "river")

                # Enhance with social media sentiment
                if social_data.get("status") == "success":
                    social_risk = self._assess_social_risk(social_data, location)
                    if social_risk:
                        risk = self._merge_risk_assessments(risk, social_risk, "social_media")

                # Add recommendations
                recommendations = generate_recommendations.invoke({
                    "risk_level": risk["risk_level"]
                })
                risk["recommendations"] = recommendations

                risk_assessments[location] = risk

            state["risk_assessment"] = risk_assessments

            # Create comprehensive summary for LLM
            high_risk_locations = [
                loc for loc, risk in risk_assessments.items()
                if risk["risk_level"] in ["high", "critical"]
            ]

            summary = f"""
Multi-Source Risk Assessment Complete:
- Total Locations: {len(risk_assessments)}
- High Risk Areas: {len(high_risk_locations)}

Data Sources Used:
- Weather Sensors: {'✅ Available' if current_data.get("status") == "success" else '❌ Unavailable'}
- River Gauges: {'✅ Available' if river_data.get("status") == "success" else '❌ Unavailable'}
- Social Media: {'✅ Available' if social_data.get("status") == "success" else '❌ Unavailable'}

Risk Breakdown:
"""
            for location, risk in risk_assessments.items():
                summary += f"\n{location}:"
                summary += f"\n  - Risk Level: {risk['risk_level'].upper()}"
                summary += f"\n  - Risk Score: {risk['score']}/100"
                summary += f"\n  - Confidence: {risk.get('confidence', 'medium')}"
                if risk['factors']:
                    summary += f"\n  - Factors: {', '.join(risk['factors'])}"
                if risk.get('data_sources'):
                    summary += f"\n  - Data Sources: {', '.join(risk['data_sources'])}"
                if risk.get('discrepancies'):
                    summary += f"\n  - ⚠️ Discrepancies: {', '.join(risk['discrepancies'])}"

            messages.append(HumanMessage(content=summary))

        else:
            messages.append(HumanMessage(content="Unable to assess risk: No valid data available"))
            state["messages"] = messages
            state["next_agent"] = "END"
            return state
        
        # Get LLM analysis
        try:
            response = self.llm.invoke(
                self.prompt.format_messages(messages=messages)
            )
            
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            print(f"\n📝 Agent Analysis:")
            print(content)
            
            state["messages"].append(AIMessage(content=content))
            state["next_agent"] = "alert_generation"
            
        except Exception as e:
            print(f"❌ Error in {self.name}: {str(e)}")
            error_response = f"Risk assessment encountered an error: {str(e)}"
            state["messages"].append(AIMessage(content=error_response))
            state["next_agent"] = "alert_generation"  # Continue workflow

        return state

    def _assess_river_risk(self, river_data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """
        Assess risk based on river gauge data for a specific location

        Args:
            river_data: Processed river gauge data
            location: Location name

        Returns:
            Risk assessment dict or None if no matching data
        """
        gauges = river_data.get("gauges", [])

        # Find nearby gauges (simple matching by location name)
        nearby_gauges = [g for g in gauges if location.lower() in g['location'].lower() or
                        any(word in g['location'].lower() for word in location.lower().split())]

        if not nearby_gauges:
            return None

        # Analyze river risk
        max_level = max(g['current_level'] for g in nearby_gauges)
        max_change = max(g['change_rate'] for g in nearby_gauges)
        any_flooding = any(g['flood_event'] for g in nearby_gauges)

        # Determine risk level
        if max_level > 3.5 or max_change > 0.5 or any_flooding:
            risk_level = "critical"
            score = 90
        elif max_level > 3.0 or max_change > 0.3:
            risk_level = "high"
            score = 75
        elif max_level > 2.5 or max_change > 0.2:
            risk_level = "moderate"
            score = 55
        else:
            risk_level = "low"
            score = 25

        factors = []
        if max_level > 3.0:
            factors.append(f"High river level ({max_level:.2f}m)")
        if max_change > 0.2:
            factors.append(f"Rising water ({max_change:+.2f}m/hr)")
        if any_flooding:
            factors.append("Active flooding at river gauge")

        return {
            "risk_level": risk_level,
            "score": score,
            "factors": factors,
            "source": "river_gauge"
        }

    def _assess_social_risk(self, social_data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """
        Assess risk based on social media sentiment for a specific location

        Args:
            social_data: Processed social media data
            location: Location name

        Returns:
            Risk assessment dict or None if no matching data
        """
        communities = social_data.get("communities", {})
        sentiment = social_data.get("latest_sentiment", 0)

        # Try to match location to community
        matching_community = None
        for comm_name in communities.keys():
            if comm_name.lower() in location.lower() or location.lower() in comm_name.lower():
                matching_community = comm_name
                break

        if not matching_community:
            # Use overall sentiment
            posts = sum(c['recent_posts'] for c in communities.values())
        else:
            posts = communities[matching_community]['recent_posts']

        # Determine risk based on sentiment and post volume
        if posts > 10 and sentiment < -0.3:
            risk_level = "critical"
            score = 85
            factors = [f"High community panic ({posts} posts, sentiment {sentiment:.2f})"]
        elif posts > 5 and sentiment < -0.1:
            risk_level = "high"
            score = 70
            factors = [f"Growing community concern ({posts} posts, sentiment {sentiment:.2f})"]
        elif posts > 3:
            risk_level = "moderate"
            score = 50
            factors = [f"Elevated community awareness ({posts} posts)"]
        else:
            risk_level = "low"
            score = 20
            factors = ["Community sentiment calm"]

        return {
            "risk_level": risk_level,
            "score": score,
            "factors": factors,
            "source": "social_media"
        }

    def _merge_risk_assessments(self, base_risk: Dict[str, Any],
                                additional_risk: Dict[str, Any],
                                source_name: str) -> Dict[str, Any]:
        """
        Merge multiple risk assessments into a comprehensive assessment

        Args:
            base_risk: Base risk assessment (usually from weather)
            additional_risk: Additional risk assessment (river or social media)
            source_name: Name of the additional source

        Returns:
            Merged risk assessment
        """
        # Initialize tracking fields
        if 'data_sources' not in base_risk:
            base_risk['data_sources'] = ['weather']
        if 'discrepancies' not in base_risk:
            base_risk['discrepancies'] = []

        base_risk['data_sources'].append(source_name)

        # Risk level hierarchy
        risk_hierarchy = {"low": 1, "moderate": 2, "high": 3, "critical": 4}

        base_level = risk_hierarchy.get(base_risk['risk_level'], 1)
        additional_level = risk_hierarchy.get(additional_risk['risk_level'], 1)

        # If levels differ significantly, flag discrepancy
        if abs(base_level - additional_level) >= 2:
            base_risk['discrepancies'].append(
                f"{source_name} shows {additional_risk['risk_level']} vs weather shows {base_risk['risk_level']}"
            )
            base_risk['confidence'] = 'low'
        elif abs(base_level - additional_level) == 1:
            base_risk['confidence'] = 'medium'
        else:
            base_risk['confidence'] = 'high'

        # Use higher risk level (conservative approach)
        if additional_level > base_level:
            base_risk['risk_level'] = additional_risk['risk_level']

        # Merge scores (weighted average, favoring higher risk)
        base_risk['score'] = int((base_risk['score'] * 0.4 + additional_risk['score'] * 0.6))

        # Merge factors
        base_risk['factors'].extend(additional_risk['factors'])

        return base_risk