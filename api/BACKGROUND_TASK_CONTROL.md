# Background Task Control API

Control the real-time data generation background task via API calls.

## Endpoints

### Get Status

```bash
GET /api/data-generation/status
```

**Response:**

```json
{
  "running": false,
  "enabled_in_env": false,
  "cycle_interval_seconds": 3600,
  "task_exists": false,
  "locations_count": 8
}
```

### Start Background Generation

```bash
POST /api/data-generation/start
```

**Response:**

```json
{
  "success": true,
  "message": "Background data generation started"
}
```

### Stop Background Generation

```bash
POST /api/data-generation/stop
```

**Response:**

```json
{
  "success": true,
  "message": "Background data generation stopped"
}
```

## Usage Examples

### Using curl

**Check status:**

```bash
curl http://localhost:8000/api/data-generation/status
```

**Start generation:**

```bash
curl -X POST http://localhost:8000/api/data-generation/start
```

**Stop generation:**

```bash
curl -X POST http://localhost:8000/api/data-generation/stop
```

### Using Python

```python
import requests

API_URL = "http://localhost:8000"  # or your deployed URL

# Check status
response = requests.get(f"{API_URL}/api/data-generation/status")
print(response.json())

# Start generation
response = requests.post(f"{API_URL}/api/data-generation/start")
print(response.json())

# Stop generation
response = requests.post(f"{API_URL}/api/data-generation/stop")
print(response.json())
```

## Use Cases

### For Demos/Presentations

1. Start generation 5 minutes before your demo
2. Show live data updating in real-time
3. Stop generation after demo to save resources

```bash
# Before demo
curl -X POST https://your-api.railway.app/api/data-generation/start

# After demo
curl -X POST https://your-api.railway.app/api/data-generation/stop
```

### For Development

Keep it running locally:

```bash
# Set in .env
ENABLE_BACKGROUND_TASK=true
DATA_CYCLE_INTERVAL=15
```

### For Production (Free Tier)

Keep it off by default, enable on-demand:

```bash
# Set in deployment environment
ENABLE_BACKGROUND_TASK=false

# Turn on when needed via API
curl -X POST https://your-api.railway.app/api/data-generation/start

# Turn off to save resources
curl -X POST https://your-api.railway.app/api/data-generation/stop
```

## Cost Optimization Strategy

**Scenario: Demo for stakeholders at 2pm**

```bash
# 1:55pm - Start generation (5 min before demo)
curl -X POST https://your-api.railway.app/api/data-generation/start

# 2:00pm - 2:30pm - Run your demo with live data

# 2:30pm - Stop generation (immediately after demo)
curl -X POST https://your-api.railway.app/api/data-generation/stop
```

**Result:** App runs for ~35 minutes instead of 24/7 = massive cost savings!

## Automation with GitHub Actions

Create `.github/workflows/scheduled-demo.yml`:

```yaml
name: Scheduled Demo Data Generation

on:
  schedule:
    # Run Monday-Friday at 1:55pm UTC (before typical demo time)
    - cron: "55 13 * * 1-5"
  workflow_dispatch: # Allow manual triggering

jobs:
  start-generation:
    runs-on: ubuntu-latest
    steps:
      - name: Start data generation
        run: |
          curl -X POST ${{ secrets.API_URL }}/api/data-generation/start

      - name: Wait 4 hours
        run: sleep 14400

      - name: Stop data generation
        run: |
          curl -X POST ${{ secrets.API_URL }}/api/data-generation/stop
```

This way the system automatically wakes up for business hours!
