"""
AI4SIDS FastAPI Server
======================
OpenAI-compatible API server for conversational disaster preparedness
"""
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
from contextlib import asynccontextmanager

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from config.settings import get_llm, DATA_DIR
from agents.conversational_coordinator import ConversationalCoordinator

# Global conversation coordinator
coordinator: Optional[ConversationalCoordinator] = None

def get_coordinator():
    """Get or initialize the conversation coordinator"""
    global coordinator
    if coordinator is None:
        try:
            llm = get_llm()
            coordinator = ConversationalCoordinator(llm)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize LLM: {str(e)}")
    return coordinator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    print("="*60)
    print("AI4SIDS API Server Starting...")
    print("="*60)
    get_coordinator()
    print("Server ready!")
    print("="*60)
    yield
    # Shutdown
    print("Shutting down...")

# FastAPI app with lifespan
app = FastAPI(
    title="AI4SIDS Climate Resilience API",
    description="Conversational AI system for disaster preparedness in Small Island Developing States",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (required for OpenWebUI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI-compatible models
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 2000
    stream: Optional[bool] = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "ai4sids"

class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI4SIDS Climate Resilience API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "models": "/v1/models"
        }
    }

@app.get("/v1/models")
async def list_models() -> ModelList:
    """List available models (OpenAI-compatible)"""
    return ModelList(
        data=[
            ModelInfo(
                id="ai4sids-climate-assistant",
                created=int(datetime.now().timestamp()),
                owned_by="ai4sids"
            )
        ]
    )

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """
    Chat completions endpoint (OpenAI-compatible)

    This is where OpenWebUI will send user messages
    """
    try:
        # Get coordinator
        coord = get_coordinator()

        # Extract user message (last message in the conversation)
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        user_message = request.messages[-1].content
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages[:-1]
        ]

        print(f"\n{'='*60}")
        print(f"New Chat Request")
        print(f"{'='*60}")
        print(f"User: {user_message}")

        # Process message through coordinator
        response_content = coord.process_message(
            user_message=user_message,
            conversation_history=conversation_history
        )

        print(f"\nResponse: {response_content[:100]}...")
        print(f"{'='*60}\n")

        # Create OpenAI-compatible response
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(datetime.now().timestamp()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(role="assistant", content=response_content),
                    finish_reason="stop"
                )
            ]
        )

    except Exception as e:
        print(f"Error processing chat: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

def main():
    """Run the API server"""
    print("=" * 60)
    print("      AI4SIDS API SERVER")
    print("      OpenAI-Compatible Conversational Interface")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()
