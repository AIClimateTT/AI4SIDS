"""
Knowledge Agent — Self-contained specialist for research document RAG queries.
Uses the local FAISS vector store over PDF research documents.
No backend API dependency — this is the actual RAG component.
"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from tools.document_knowledge import search_knowledge


SYSTEM_PROMPT = """You are the Knowledge Agent for AI4SIDS, a climate resilience system for Trinidad & Tobago and Small Island Developing States.

You answer educational, conceptual, and research questions about flooding, climate, disaster preparedness, and environmental science. You may receive relevant excerpts from research documents below — use them to ground your answers.

HOW TO RESPOND:
1. Answer the question directly and thoroughly — don't just quote documents
2. Explain concepts in accessible, plain language (avoid jargon unless you explain it)
3. Connect abstract concepts to Trinidad & Tobago's real context where relevant (e.g., the Caroni River basin, tropical weather patterns, SIDS vulnerability)
4. Reference source documents when available ("According to research on SIDS flood management...")
5. If the knowledge base doesn't have directly relevant material, use your general knowledge and say so
6. Provide practical takeaways when appropriate — help the user understand why this matters

You are the agent that handles questions like:
- "What is flood risk?" (explain the concept)
- "How does weather affect the environment?"
- "What causes flooding in Trinidad?"
- "Tell me about climate resilience for small islands"
- "How do early warning systems work?"

Be conversational, informative, and helpful. Make complex topics understandable.
Use "I" naturally ("Based on what I know...", "The research suggests...", "In Trinidad's case...")."""


class KnowledgeAgent:
    """Self-contained agent for research document RAG queries."""

    def __init__(self, llm):
        self.llm = llm
        self.name = "Knowledge Agent"

    def process(self, query: str, location: str = None,
                history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a general / knowledge query using FAISS vector search.

        Returns:
            {"response": str, "data": dict}
        """
        # Search the PDF knowledge base
        results = search_knowledge(query, top_k=3)
        data: Dict[str, Any] = {"sources": results or []}

        context = self._build_context(results)
        response = self._analyze(query, context, history)
        return {"response": response, "data": data}

    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build a knowledge context string from FAISS search results."""
        if not results:
            return ""

        parts = ["**Relevant Research Documents:**"]
        for i, result in enumerate(results, 1):
            source = result.get("source", "Unknown")
            content = result.get("content", "")[:400]
            parts.append(f"\n{i}. From '{source}':\n{content}...")

        return "\n".join(parts)

    def _analyze(self, query: str, context: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Invoke the LLM with knowledge-specialist prompt and document context."""
        system_content = SYSTEM_PROMPT
        if context:
            system_content += f"\n\n{context}"
        else:
            system_content += "\n\nNo directly relevant documents were found in the knowledge base. Answer based on your general knowledge about flood risk and climate resilience, and let the user know the knowledge base didn't have a specific match."

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
            print(f"[KnowledgeAgent] LLM error: {e}")
            if context:
                return f"I found some relevant research, but I'm having trouble summarizing it. Here's what I found:\n\n{context}"
            return "I'm having trouble accessing the knowledge base right now. Please try again."
