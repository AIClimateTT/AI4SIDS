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
    - Analyzing current weather conditions
    - Assessing flood risk for each location
    - Assigning risk levels (LOW, MODERATE, HIGH, CRITICAL)
    - Providing actionable recommendations
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Flood Risk Assessment Agent"
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Flood Risk Assessment Agent for AI4SIDS Climate Resilience System.

Your responsibilities:
1. Analyze current weather conditions to assess flood risk
2. Consider: rainfall accumulation, river gauge levels, storm intensity, terrain vulnerability
3. Assign risk levels (LOW, MODERATE, HIGH, CRITICAL) for each location
4. Provide clear, actionable recommendations for each risk level

Risk assessment has been calculated. Provide a brief summary of the overall situation and key concerns.
Focus on areas with HIGH or CRITICAL risk. Be clear and direct."""),
            MessagesPlaceholder(variable_name="messages"),
        ])
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess flood risk for all locations
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with risk assessments
        """
        print(f"\n{'='*60}")
        print(f"🤖 {self.name} - Analyzing Risk")
        print(f"{'='*60}")
        
        messages = state["messages"]
        current_data = state.get("current_data", {})
        risk_assessments = {}
        
        # Assess risk for each location
        if current_data.get("status") == "success" and "locations" in current_data:
            print(f"\n🌊 Assessing {len(current_data['locations'])} locations...")
            
            for location in current_data["locations"]:
                risk = assess_flood_risk.invoke({
                    "sensor_data": current_data,
                    "location": location
                })
                
                # Add recommendations
                recommendations = generate_recommendations.invoke({
                    "risk_level": risk["risk_level"]
                })
                risk["recommendations"] = recommendations
                
                risk_assessments[location] = risk
            
            state["risk_assessment"] = risk_assessments
            
            # Create summary for LLM
            high_risk_locations = [
                loc for loc, risk in risk_assessments.items() 
                if risk["risk_level"] in ["high", "critical"]
            ]
            
            summary = f"""
Risk Assessment Complete:
- Total Locations: {len(risk_assessments)}
- High Risk Areas: {len(high_risk_locations)}

Risk Breakdown:
"""
            for location, risk in risk_assessments.items():
                summary += f"\n{location}:"
                summary += f"\n  - Risk Level: {risk['risk_level'].upper()}"
                summary += f"\n  - Risk Score: {risk['score']}/100"
                if risk['factors']:
                    summary += f"\n  - Factors: {', '.join(risk['factors'])}"
            
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