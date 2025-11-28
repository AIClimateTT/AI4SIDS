"""
River Monitoring Agent - Autonomous river gauge monitoring and flood prediction
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class RiverMonitoringAgent:
    """
    Agent responsible for:
    - Monitoring river gauge levels across Caroni River
    - Tracking water level trends (rising/falling)
    - Predicting downstream flood risks
    - Correlating river levels with weather conditions
    """

    def __init__(self, llm):
        self.llm = llm
        self.name = "River Monitoring Agent"

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the River Monitoring Agent for AI4SIDS Climate Resilience System.

Your responsibilities:
1. Monitor river gauge levels at multiple points along the Caroni River
2. Analyze water level trends (rising, falling, stable)
3. Identify rapid changes that indicate flash flood risks
4. Predict downstream impacts based on upstream water levels
5. Correlate river levels with rainfall and weather data

When analyzing river data:
- Rising levels > 0.5m/hour = HIGH RISK (flash flood potential)
- Rising levels 0.2-0.5m/hour = MODERATE RISK
- Levels > 3.5m = CRITICAL (regardless of trend)
- Levels > 3.0m = HIGH RISK
- Consider upstream-to-downstream flow (floods move downstream over time)

Provide clear, actionable assessments of:
- Current river status at each gauge point
- Trend analysis (rising/falling/stable)
- Risk levels and predictions
- Recommendations for affected areas

Be concise and focus on critical information."""),
            MessagesPlaceholder(variable_name="messages"),
        ])

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process river gauge data and analyze flood risks

        Args:
            state: Current agent state with river_data

        Returns:
            Updated state with river analysis
        """
        print(f"\n{'='*60}")
        print(f"[RIVER] {self.name} - Analyzing River Conditions")
        print(f"{'='*60}")

        messages = state["messages"]
        river_data = state.get("river_data", {})

        # Add river data summary to messages
        if river_data and river_data.get("status") == "success":
            gauges = river_data.get("gauges", [])

            river_summary = f"""
River Gauge Analysis Summary:
- Total Gauges: {river_data.get('total_gauges', 0)}
- Locations: {', '.join(river_data.get('locations', []))}
- Average River Level: {river_data.get('avg_river_level', 0):.2f}m
- Gauges Rising: {river_data.get('gauges_rising', 0)}
- Gauges Falling: {river_data.get('gauges_falling', 0)}
- Active Flood Events: {river_data.get('flood_events', 0)}

Detailed Gauge Readings:
"""
            for gauge in gauges:
                status = "FLOODING" if gauge['flood_event'] else "Normal"
                trend = "↑" if gauge['change_rate'] > 0 else "↓" if gauge['change_rate'] < 0 else "→"
                river_summary += f"\n{gauge['location']} ({gauge['sensor_id']}): {gauge['current_level']:.2f}m {trend} ({gauge['change_rate']:+.2f}m/hr) [{status}]"

            river_summary += "\n\nPlease analyze this river data and provide your assessment of flood risks."

            messages.append(HumanMessage(content=river_summary))
        else:
            error_msg = river_data.get('error', 'No river data available')
            messages.append(HumanMessage(content=f"River monitoring unavailable: {error_msg}"))
            state["messages"] = messages
            return state

        # Get LLM analysis
        try:
            response = self.llm.invoke(
                self.prompt.format_messages(messages=messages)
            )

            # Handle different response types
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)

            print(f"\n📝 Agent Analysis:")
            print(content)

            state["messages"].append(AIMessage(content=content))

        except Exception as e:
            print(f"❌ Error in {self.name}: {str(e)}")
            error_response = f"River analysis encountered an error: {str(e)}"
            state["messages"].append(AIMessage(content=error_response))

        return state

    def get_gauge_status(self, river_data: Dict[str, Any], location: str = None) -> str:
        """
        Get conversational status for specific gauge or all gauges

        Args:
            river_data: Processed river data
            location: Optional specific location to check

        Returns:
            Formatted status string
        """
        if not river_data or river_data.get("status") != "success":
            return "I don't have current river gauge data available."

        gauges = river_data.get("gauges", [])

        if location:
            # Filter to specific location
            matching_gauges = [g for g in gauges if location.lower() in g['location'].lower()]
            if not matching_gauges:
                return f"I don't have gauge data for {location}."
            gauges = matching_gauges

        response = ""
        for gauge in gauges:
            level = gauge['current_level']
            change = gauge['change_rate']
            loc = gauge['location']

            # Determine trend description
            if abs(change) < 0.1:
                trend_desc = "holding steady"
            elif change > 0.5:
                trend_desc = f"rising rapidly at {change:.2f}m per hour"
            elif change > 0.2:
                trend_desc = f"rising at {change:.2f}m per hour"
            elif change < -0.5:
                trend_desc = f"falling rapidly at {abs(change):.2f}m per hour"
            else:
                trend_desc = f"slowly changing ({change:+.2f}m/hr)"

            # Determine risk level
            if level > 3.5 or change > 0.5:
                risk_emoji = "🔴"
                risk = "CRITICAL"
            elif level > 3.0 or change > 0.3:
                risk_emoji = "🟠"
                risk = "HIGH"
            elif level > 2.5 or change > 0.2:
                risk_emoji = "🟡"
                risk = "MODERATE"
            else:
                risk_emoji = "🟢"
                risk = "LOW"

            response += f"\n{risk_emoji} **{loc}**: River level at {level:.2f}m, {trend_desc}. Risk: {risk}"

            if gauge['flood_event']:
                response += " ⚠️ **FLOODING ACTIVE**"

        return response.strip()
