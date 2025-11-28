"""
Social Media Intelligence Agent - Analyzes community sentiment and crowd-sourced reports
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class SocialMediaIntelligenceAgent:
    """
    Agent responsible for:
    - Analyzing social media sentiment about flooding/weather
    - Detecting emerging hotspots (areas with sudden post spikes)
    - Identifying affected communities
    - Cross-validating sensor data with community reports
    - Providing human context to technical data
    """

    def __init__(self, llm):
        self.llm = llm
        self.name = "Social Media Intelligence Agent"

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Social Media Intelligence Agent for AI4SIDS Climate Resilience System.

Your responsibilities:
1. Analyze social media sentiment from affected communities
2. Detect sudden spikes in posts (indicates emerging crisis)
3. Identify which communities are most concerned/affected
4. Cross-validate technical sensor data with community reports
5. Provide human context and ground truth

Sentiment Analysis Scale:
- Highly Negative (< -0.3): Panic, fear, active flooding reports
- Negative (-0.3 to -0.1): Concern, worry, preparation
- Neutral (-0.1 to 0.1): Normal conditions, general awareness
- Positive (> 0.1): Calm, confidence, recovery

Alert Thresholds:
- 10+ posts with highly negative sentiment = CRITICAL (widespread concern)
- 5-10 posts with negative sentiment = HIGH (growing concern)
- 3-5 posts = MODERATE (community awareness increasing)
- < 3 posts = NORMAL

Communities Monitored:
- Cunupia
- Piarco
- St. Augustine
- St. Helena

Key Insights to Provide:
- Which communities are most active/concerned
- Sentiment trends (improving/worsening)
- Potential sensor blind spots (community reports ≠ sensor data)
- Early warning signals (sudden sentiment shift)

Be concise and focus on actionable intelligence."""),
            MessagesPlaceholder(variable_name="messages"),
        ])

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process social media data and analyze community sentiment

        Args:
            state: Current agent state with social_media_data

        Returns:
            Updated state with sentiment analysis
        """
        print(f"\n{'='*60}")
        print(f"📱 {self.name} - Analyzing Community Sentiment")
        print(f"{'='*60}")

        messages = state["messages"]
        social_data = state.get("social_media_data", {})

        # Add social media summary to messages
        if social_data and social_data.get("status") == "success":
            communities = social_data.get("communities", {})

            social_summary = f"""
Social Media Intelligence Summary:
- Total Posts Analyzed: {social_data.get('total_posts', 0)}
- Overall Sentiment: {social_data.get('avg_sentiment', 0):.3f} ({social_data.get('sentiment_classification', 'unknown')})
- Latest Sentiment: {social_data.get('latest_sentiment', 0):.3f}

Community Breakdown:
"""
            for community, stats in communities.items():
                social_summary += f"\n- {community}: {stats['total_posts']} total posts, {stats['recent_posts']} recent posts"

            # Add context about what sentiment means
            latest_sent = social_data.get('latest_sentiment', 0)
            if latest_sent < -0.3:
                context = "⚠️ ALERT: Highly negative sentiment suggests panic or active crisis"
            elif latest_sent < -0.1:
                context = "⚠️ WARNING: Negative sentiment indicates growing concern"
            elif latest_sent < 0.1:
                context = "ℹ️ NORMAL: Neutral sentiment, no major concerns"
            else:
                context = "✅ POSITIVE: Community sentiment is calm/positive"

            social_summary += f"\n\n{context}\n\nPlease analyze this social media data and provide insights on community concerns and potential risks."

            messages.append(HumanMessage(content=social_summary))
        else:
            error_msg = social_data.get('error', 'No social media data available')
            messages.append(HumanMessage(content=f"Social media monitoring unavailable: {error_msg}"))
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
            error_response = f"Social media analysis encountered an error: {str(e)}"
            state["messages"].append(AIMessage(content=error_response))

        return state

    def get_community_sentiment(self, social_data: Dict[str, Any], community: str = None) -> str:
        """
        Get conversational sentiment report for specific community or all communities

        Args:
            social_data: Processed social media data
            community: Optional specific community to check

        Returns:
            Formatted sentiment report string
        """
        if not social_data or social_data.get("status") != "success":
            return "I don't have current social media data available."

        communities = social_data.get("communities", {})

        if community and community not in communities:
            return f"I don't have social media data for {community}. I'm tracking: {', '.join(communities.keys())}"

        overall_sentiment = social_data.get('latest_sentiment', 0)
        classification = social_data.get('sentiment_classification', 'unknown')

        response = f"**Overall Sentiment:** {overall_sentiment:.3f} ({classification})\n\n"

        # Analyze each community
        target_communities = [community] if community else communities.keys()

        for comm in target_communities:
            if comm not in communities:
                continue

            stats = communities[comm]
            posts = stats['recent_posts']

            # Determine alert emoji based on posts and sentiment
            if posts > 10 and overall_sentiment < -0.3:
                alert = "🔴 CRITICAL"
            elif posts > 5 and overall_sentiment < -0.1:
                alert = "🟠 HIGH"
            elif posts > 3:
                alert = "🟡 MODERATE"
            else:
                alert = "🟢 NORMAL"

            response += f"{alert} **{comm}**: {posts} recent posts"

            # Add context
            if posts > 10:
                response += " (high activity - significant concern)"
            elif posts > 5:
                response += " (elevated activity - growing concern)"
            elif posts > 0:
                response += " (normal activity)"
            else:
                response += " (quiet - no reports)"

            response += f"\n"

        # Add interpretation
        if overall_sentiment < -0.3:
            response += "\n⚠️ **Community is reporting panic or active crisis conditions**"
        elif overall_sentiment < -0.1:
            response += "\n⚠️ **Community is expressing concern and worry**"
        elif overall_sentiment > 0.1:
            response += "\n✅ **Community sentiment is positive/calm**"
        else:
            response += "\nℹ️ **Community sentiment is neutral - normal conditions**"

        return response.strip()

    def detect_anomalies(self, social_data: Dict[str, Any], sensor_data: Dict[str, Any] = None) -> str:
        """
        Detect discrepancies between social media reports and sensor data

        Args:
            social_data: Processed social media data
            sensor_data: Optional sensor data for cross-validation

        Returns:
            Anomaly report string
        """
        if not social_data or social_data.get("status") != "success":
            return "Cannot detect anomalies - no social media data available."

        sentiment = social_data.get('latest_sentiment', 0)
        total_posts = sum(comm['recent_posts'] for comm in social_data.get('communities', {}).values())

        anomalies = []

        # Check for high activity with negative sentiment but low sensor warnings
        if total_posts > 10 and sentiment < -0.3:
            if sensor_data and sensor_data.get('flood_events', 0) == 0:
                anomalies.append("⚠️ DISCREPANCY: High negative sentiment and many posts, but sensors show no flooding. Possible sensor blind spot or malfunction.")

        # Check for low activity but sensors show flooding
        if total_posts < 3 and sensor_data and sensor_data.get('flood_events', 0) > 0:
            anomalies.append("⚠️ DISCREPANCY: Sensors detect flooding but low social media activity. Community may be unaware or evacuated.")

        # Check for sudden spike in posts
        if total_posts > 15:
            anomalies.append("🔔 ALERT: Sudden spike in social media posts - indicates rapidly developing situation.")

        if not anomalies:
            return "✅ No anomalies detected - social media reports align with sensor data."

        return "\n".join(anomalies)
