# AI4SIDS - Flood Monitoring System

Real-time flood monitoring dashboard with advanced playback controls for time-series data visualization.

## Quick Setup

### API Setup

**Option 1: Using Python venv**

```bash
cd api
python -m venv .venv
source venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Option 2: Using uv (faster)**

```bash
cd api
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
pnpm install
```

## Running the Application

### Start API Server

```bash
# Original API (port 8000)
cd api
fastapi dev main.py

# Enhanced API with playback controls (port 8001)
cd api
fastapi dev api.py
```

### Start Frontend

```bash
cd frontend
pnpm dev
```

The frontend will be available at `http://localhost:5173`

## Features

- **Real-time Dashboard**: Live flood risk monitoring
- **Interactive Map**: Location-based flood data visualization
- **Playback Controls**: Time-lapse and replay functionality
- **Event Detection**: Auto-identification of flood events
- **Timeline Scrubbing**: Navigate through historical data
- **Speed Controls**: 0.1x to 10x playback speeds

## API Endpoints

### Standard Endpoints

- `GET /api/system-update` - System status and locations
- `GET /api/real-time/{location}` - Location conditions
- `GET /api/timeline/{location}` - Historical data

