# AI4SIDS Deployment Guide
## OpenWebUI + Conversational Climate Assistant

This guide will help you deploy the AI4SIDS system with OpenWebUI chat interface.

---

## Overview

**Architecture:**
```
User (Browser)
    → OpenWebUI (Chat Interface - Port 3000)
        → AI4SIDS Backend (FastAPI - Port 8000)
            → Ollama LLM (Local - Port 11434)
                → llama3.2 model
```

---

## Prerequisites

### Required:
- **Docker & Docker Compose** installed
- **Git** (to clone/navigate the project)
- **At least 8GB RAM** (for llama3.2 model)
- **10GB free disk space** (for Docker images and models)

### For Local Development (Without Docker):
- **Python 3.11+**
- **Ollama** installed locally
- **Virtual environment** (recommended)

---

## Deployment Options

### Option A: Full Docker Deployment (Recommended)

This deploys everything in Docker containers - easiest method!

#### Step 1: Navigate to project directory
```bash
cd c:\Users\abdul\Desktop\ai4sids\ai4sids
```

#### Step 2: Pull llama3.2 model in Ollama container
First, start just the Ollama service:
```bash
docker-compose up ollama -d
```

Wait 30 seconds, then pull the model:
```bash
docker exec -it ai4sids-ollama ollama pull llama3.2
```

#### Step 3: Start all services
```bash
docker-compose up -d
```

#### Step 4: Verify services are running
```bash
docker-compose ps
```

You should see 3 services running:
- `ai4sids-ollama` (Ollama LLM)
- `ai4sids-backend` (FastAPI server)
- `ai4sids-webui` (OpenWebUI)

#### Step 5: Access OpenWebUI
Open your browser and go to:
```
http://localhost:3000
```

#### Step 6: Configure OpenWebUI (First Time Only)
1. Create an account (first user becomes admin)
2. Go to **Settings** → **Connections**
3. Verify the connection shows:
   - **API URL:** `http://ai4sids-backend:8000/v1`
   - **API Key:** `sk-aea2d955be6a4c6ba5623e92f736be94`
4. Go to **Settings** → **Models**
5. Select model: **ai4sids-climate-assistant**

#### Step 7: Start Chatting!
Try these example queries:
- "What's the flood risk in Arima?"
- "Is it safe in Port of Spain?"
- "Should I evacuate from San Fernando?"
- "Give me an overview of all locations"

---

### Option B: Hybrid (Local Ollama + Docker for Backend/UI)

If you already have Ollama running locally.

#### Step 1: Ensure Ollama is running
```bash
ollama list  # Should show llama3.2
```

If llama3.2 is not installed:
```bash
ollama pull llama3.2
```

#### Step 2: Update docker-compose.yml
Comment out the Ollama service and update the backend environment:

```yaml
services:
  # ollama:
  #   ... (comment this out)

  ai4sids-backend:
    ...
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434  # Points to host machine
      ...
```

#### Step 3: Start services
```bash
docker-compose up ai4sids-backend open-webui -d
```

#### Step 4: Access at http://localhost:3000

---

### Option C: Full Local Development (No Docker)

For development and testing.

#### Step 1: Activate virtual environment
```bash
cd c:\Users\abdul\Desktop\ai4sids
ai4sids_env\Scripts\activate
```

#### Step 2: Ensure dependencies are installed
```bash
cd ai4sids
pip install -r requirements.txt
```

#### Step 3: Verify Ollama is running
```bash
ollama list
```

Ensure llama3.2 is available:
```bash
ollama pull llama3.2
```

#### Step 4: Start the AI4SIDS API server
```bash
python api_server.py
```

You should see:
```
============================================================
      AI4SIDS API SERVER
      OpenAI-Compatible Conversational Interface
============================================================
INFO: Uvicorn running on http://0.0.0.0:8000
```

#### Step 5: Install OpenWebUI separately
```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=sk-aea2d955be6a4c6ba5623e92f736be94 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

#### Step 6: Access at http://localhost:3000

---

## Testing the Deployment

### 1. Test API Endpoints Directly

**Health Check:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","timestamp":"2025-11-26T..."}
```

**List Models:**
```bash
curl http://localhost:8000/v1/models
```

Expected response:
```json
{
  "object":"list",
  "data":[{
    "id":"ai4sids-climate-assistant",
    "object":"model",
    "created":...,
    "owned_by":"ai4sids"
  }]
}
```

**Test Chat Completion:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai4sids-climate-assistant",
    "messages": [{"role": "user", "content": "What is the flood risk in Arima?"}]
  }'
```

### 2. Test via OpenWebUI
1. Open http://localhost:3000
2. Start a new chat
3. Ask: "What locations do you have data for?"
4. Ask: "What's the risk in [location]?"

---

## Troubleshooting

### Issue: Ollama model not found
```bash
# In Docker:
docker exec -it ai4sids-ollama ollama pull llama3.2

# Locally:
ollama pull llama3.2
```

### Issue: Backend can't connect to Ollama
- **Docker:** Ensure Ollama container is healthy: `docker-compose ps`
- **Local:** Ensure Ollama is running: `ollama list`

### Issue: OpenWebUI shows "Connection Error"
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify API URL in OpenWebUI settings
3. Check logs: `docker-compose logs ai4sids-backend`

### Issue: No data available
- Ensure CSV files are in `ai4sids/data/sample/`
- Check logs: `docker-compose logs ai4sids-backend`
- Look for "OK Loaded data for X locations"

### Issue: Unicode/Emoji errors on Windows
- This should be fixed, but if you see encoding errors:
- Set environment variable: `set PYTHONIOENCODING=utf-8`

---

## Understanding the Conversational System

### How It Works:

1. **User asks a question** → OpenWebUI sends to `/v1/chat/completions`
2. **ConversationalCoordinator analyzes the query:**
   - Extracts location (if mentioned)
   - Determines intent (flood_risk, weather, evacuation, general)
3. **Routes to appropriate handler:**
   - Specific location → Returns risk data for that location only
   - "All locations" → Returns summary of all areas
   - General question → Uses LLM with context about available data
4. **Returns formatted response**

### Example Conversation Flow:

**User:** "Will there be a flood in Arima?"
- **System detects:** Location = "Arima", Intent = "flood_risk"
- **Response:** Risk assessment for Arima only (not all locations)

**User:** "Show me all locations"
- **System detects:** Intent = "all_locations"
- **Response:** Summary table of all monitored areas

**User:** "What should I do?"
- **System detects:** Intent = "general", uses conversation context
- **Response:** LLM provides guidance based on previous messages

---

## Stopping the Services

### Docker:
```bash
docker-compose down
```

### Local development:
Press `CTRL+C` in the terminal running `api_server.py`

---

## Data Updates

To update weather data:
1. Place new CSV files in `ai4sids/data/sample/`
2. Restart the backend:
   ```bash
   docker-compose restart ai4sids-backend
   ```

The system automatically loads the latest weather data on startup.

---

## Environment Variables

Key variables in `.env`:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434  # Local
# or
OLLAMA_BASE_URL=http://ollama:11434     # Docker

# Model Selection
LLM_MODEL=llama3.2

# OpenWebUI API Key (for authentication)
OPENWEBUI_API_KEY=sk-aea2d955be6a4c6ba5623e92f736be94
```

---

## Production Considerations

### Security:
- Change the default API key
- Enable HTTPS (use reverse proxy like Nginx)
- Implement user authentication
- Restrict CORS origins

### Performance:
- Use larger/better LLM models for production
- Increase Ollama memory limits
- Consider GPU acceleration for Ollama

### Monitoring:
- Enable LangSmith tracing (set `LANGCHAIN_TRACING_V2=true`)
- Monitor Docker logs
- Set up health check alerts

---

## Next Steps

1. **Customize** the risk thresholds in `config/settings.py`
2. **Add more data sources** (social media, river gauges)
3. **Enhance** the conversational prompts in `ConversationalCoordinator`
4. **Deploy** to cloud (AWS, Azure, GCP)
5. **Integrate** with real-time weather APIs

---

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review the codebase documentation
- Ensure all prerequisites are met

---

**Congratulations!** You now have a fully functional conversational climate resilience assistant.

Start chatting and stay safe!
