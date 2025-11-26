"""
Data Ingestion Agent - Autonomous data collection and validation
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class DataIngestionAgent:
    """
    Agent responsible for:
    - Collecting data from multiple sources (sensors, gauges, social media)
    - Validating data quality
    - Detecting anomalies
    - Preparing data for downstream agents
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Data Ingestion Agent"
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Data Ingestion Agent for AI4SIDS Climate Resilience System.

Your responsibilities:
1. Collect and validate data from IoT weather sensors, river gauges, and social media
2. Identify data quality issues, missing values, and anomalies
3. Provide a clear summary of the current data state
4. Flag any sensors that may be malfunctioning

Analyze the provided sensor data and summarize:
- Number of sensors and locations
- Data quality status
- Any anomalies detected
- Overall assessment (GOOD/FAIR/POOR)

Be concise and actionable in your response."""),
            MessagesPlaceholder(variable_name="messages"),
        ])
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming data and validate quality
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validation results
        """
        print(f"\n{'='*60}")
        print(f"🤖 {self.name} - Processing Data")
        print(f"{'='*60}")
        
        messages = state["messages"]
        current_data = state.get("current_data", {})
        
        # Add data summary to messages
        if current_data and current_data.get("status") == "success":
            data_summary = f"""
Data Ingestion Summary:
- Total Sensors: {current_data.get('total_sensors', 0)}
- Locations: {', '.join(current_data.get('locations', []))}
- Total Readings: {current_data.get('total_readings', 0)}
- Average Rainfall: {current_data.get('avg_actual_rainfall', 0):.1f}mm
- Storm Conditions: {current_data.get('storm_conditions', 0)} readings
- Flood Events: {current_data.get('flood_events', 0)} detected

Please analyze this data and provide your assessment.
"""
            messages.append(HumanMessage(content=data_summary))
        else:
            error_msg = current_data.get('error', 'Unknown error occurred')
            messages.append(HumanMessage(content=f"Data ingestion failed: {error_msg}"))
            state["messages"] = messages
            state["next_agent"] = "END"
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
            state["next_agent"] = "prediction_accuracy"
            
        except Exception as e:
            print(f"❌ Error in {self.name}: {str(e)}")
            error_response = f"Data validation encountered an error: {str(e)}"
            state["messages"].append(AIMessage(content=error_response))
            state["next_agent"] = "prediction_accuracy"  # Continue workflow
        
        return state