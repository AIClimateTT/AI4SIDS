# Component Migration Plan: New UI Components Integration

**Date:** October 27, 2025  
**Project:** AI4SIDS Disaster Resilience System  
**Purpose:** Plan for integrating RiskMap, DataAnalytics, and AlertsSection components with existing backend API

---

## Executive Summary

Three new components from another project need integration with your current AI4SIDS backend:

1. **RiskMap** - Interactive flood risk visualization with Leaflet maps
2. **DataAnalytics** - Recharts-based time-series data visualization
3. **AlertsSection** - Real-time alert notifications and preparedness resources

**Current State:** All three components use mock/static data  
**Goal:** Connect them to your existing FastAPI backend with real-time data from SQLite database

---

## 1. RiskMap Component Analysis

### Current Implementation

- **Location:** `/frontend/src/components/RiskMap.tsx`
- **Purpose:** Display flood risk zones and city markers on interactive map
- **Technology:** React, Leaflet, react-leaflet
- **Data Source:** Currently uses **hardcoded static data**

### Static Data Used

```typescript
// Hardcoded city risk levels
const riskLevels = [
  { zone: 'Port of Spain', risk: 'critical', population: '37,000', lat: 10.6549, lng: -61.5019 },
  { zone: 'San Fernando', risk: 'high-risk', population: '48,000', ... },
  // ... 5 total cities
]

// Hardcoded flood risk polygons
const floodRiskZones = [
  { name: 'Port of Spain Coastal', risk: 'critical', coordinates: [...] },
  // ... 5 total zones
]

// Hardcoded environmental factors
<div>127mm Rainfall (24h)</div>
<div>45 km/h Wind Speed</div>
<div>+0.8m Tide Surge</div>
```

### API Integration Requirements

#### ✅ **ALREADY AVAILABLE** - No Backend Changes Needed

Your backend already provides all necessary data through existing endpoints:

1. **GET `/api/locations`** - Returns all locations with coordinates and current risk

   ```json
   {
     "locations": [
       {
         "name": "Caroni",
         "latitude": 10.6167,
         "longitude": -61.4167,
         "sensor_id": "CRN-001",
         "current_risk": "MEDIUM",
         "has_data": true
       }
     ],
     "total": 8
   }
   ```

2. **GET `/api/system-update`** - Provides comprehensive data for all locations

   ```json
   {
     "locations": [
       {
         "name": "Caroni",
         "flood_risk": "MEDIUM",
         "river_level": 3.2,
         "change_rate": 0.045,
         "latitude": 10.6167,
         "longitude": -61.4167
       }
     ],
     "alerts": [...],
     "timestamp": "2025-10-27T..."
   }
   ```

3. **GET `/api/real-time/{location}`** - Detailed conditions including weather
   ```json
   {
     "location": "Caroni",
     "river_conditions": { "level": 3.2, "flood_risk": "MEDIUM" },
     "weather": {
       "rainfall_mm": 12.5,
       "temperature_c": 28.3,
       "humidity_percent": 78,
       "rainfall_rate_hourly": 50.0
     }
   }
   ```

#### 🔧 **Frontend Changes Required**

**File:** `/frontend/src/components/RiskMap.tsx`

**Changes:**

1. **Replace static `riskLevels` array** with data from `useLocations()` hook
2. **Replace static `floodRiskZones` array** with dynamic zones (if available) or keep as static overlay
3. **Replace static environmental factors** with real-time weather from `useRealTimeConditions()`
4. **Add location selection** to show detailed weather for selected marker
5. **Map risk levels** from API format to component format:
   - API: `"CRITICAL"` → Component: `"critical"`
   - API: `"HIGH"` → Component: `"high-risk"`
   - API: `"MEDIUM"` → Component: `"moderate"`
   - API: `"ELEVATED"` → Component: `"low-risk"`
   - API: `"LOW"` → Component: `"safe"`

**Example Integration Code:**

```typescript
import {
  useLocations,
  useSystemUpdate,
  useRealTimeConditions,
} from "@/lib/hooks/useApiData";

const RiskMap = () => {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null);
  const { data: locationsData } = useLocations();
  const { data: systemUpdate } = useSystemUpdate();
  const { data: realTimeData } = useRealTimeConditions(selectedLocation);

  // Transform API locations to risk levels format
  const riskLevels = useMemo(() => {
    if (!systemUpdate?.locations) return [];
    return systemUpdate.locations.map((loc) => ({
      zone: loc.name,
      risk: mapApiRiskToComponentRisk(loc.current_risk),
      population: "N/A", // Population data not in API - keep static or remove
      lat: loc.latitude,
      lng: loc.longitude,
    }));
  }, [systemUpdate]);

  // Use real-time weather data when location selected
  const environmentalFactors = realTimeData
    ? {
        rainfall: realTimeData.weather.rainfall_mm,
        windSpeed: "N/A", // Not in current API
        tideSurge: "N/A", // Not in current API
      }
    : null;
};
```

#### ⚠️ **Data Gaps Identified**

1. **Population Data** - Not available in API
   - **Solution:** Keep static or add `population` field to Location model
2. **Flood Risk Polygon Coordinates** - Not stored in database
   - **Solution:** Keep static zones OR add `FloodZone` table with polygon geometry
3. **Wind Speed** - Weather table has `windspeed_kmh` but not exposed in real-time endpoint
   - **Solution:** Add to response in `location/contoller.py:get_real_time_conditions()`
4. **Tide/Storm Surge Data** - Not currently tracked
   - **Solution:** Add new field to Weather model or keep as static placeholder

---

## 2. DataAnalytics Component Analysis

### Current Implementation

- **Location:** `/frontend/src/components/DataAnalytics.tsx`
- **Purpose:** Multi-chart dashboard with Recharts (rainfall, river gauge, temperature, humidity)
- **Technology:** React, Recharts (AreaChart, LineChart, ComposedChart)
- **Data Source:** Currently uses **mock 7-day data arrays**

### Static Data Used

```typescript
// Mock 7-day data
const rainfallData = [
  { date: "Mon", value: 12 },
  { date: "Tue", value: 25 },
  // ... hardcoded 7 days
];

const riverGaugeData = [
  { date: "Mon", level: 2.3 },
  // ... hardcoded 7 days
];

// Statistics
const rainfallStats = {
  current: 15,
  avg: 30.7,
  max: 52,
  min: 12,
  trend: -28.8,
};
```

### API Integration Requirements

#### ✅ **ALREADY AVAILABLE** - Existing Backend Support

Your backend **already has comprehensive analytics**:

1. **GET `/api/analytics/{location_id}?hours_back=168`** - Historical data for any timeframe

   ```json
   {
     "location": { "id": 1, "name": "Caroni", ... },
     "time_range": {
       "hours_back": 168,  // 7 days
       "start_time": "...",
       "end_time": "..."
     },
     "historical_data": [
       {
         "timestamp": "2025-10-20T12:00:00Z",
         "river_level_m": 2.8,
         "change_in_level_m": 0.02,
         "flood_risk": "LOW"
       }
       // ... all historical points
     ],
     "predictions": [...],
     "summary_stats": {
       "min_level": 2.3,
       "max_level": 4.1,
       "avg_level": 3.2,
       "current_level": 3.0,
       "trend": "rising"
     },
     "accuracy_metrics": { ... }
   }
   ```

2. **Frontend Hook Already Exists:**
   ```typescript
   // Already in useApiData.ts
   useLocationAnalytics(locationName, hoursBack, enabled);
   useLocationAnalyticsById(locationId, hoursBack, enabled);
   ```

#### 🔧 **Frontend Changes Required**

**File:** `/frontend/src/components/DataAnalytics.tsx`

**Changes:**

1. **Add location selection dropdown** - Connect to `useLocations()` to get available locations
2. **Replace all mock data arrays** with `useLocationAnalytics()` data
3. **Transform API data** to Recharts format:

   ```typescript
   // Transform historical_data array
   const rainfallData = analyticsData.historical_data.map((point) => ({
     date: formatDate(point.timestamp),
     value: getRainfallFromTimestamp(point.timestamp), // Need weather correlation
   }));

   const riverGaugeData = analyticsData.historical_data.map((point) => ({
     date: formatDate(point.timestamp),
     level: point.river_level_m,
   }));
   ```

4. **Calculate statistics** from API data instead of hardcoded values
5. **Add time range selector** - Use `hours_back` parameter (24h, 7d, 30d options already in UI)

**Example Integration:**

```typescript
import { useLocationAnalytics, useLocations } from "@/lib/hooks/useApiData";

const DataAnalytics = () => {
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(
    null
  );
  const [timeRange, setTimeRange] = useState("7d");

  const { data: locationsData } = useLocations();
  const { data: analyticsData, isLoading } = useLocationAnalyticsById(
    selectedLocationId,
    timeRange === "7d" ? 168 : timeRange === "24h" ? 24 : 720,
    !!selectedLocationId
  );

  // Transform to chart format
  const riverGaugeData = useMemo(() => {
    if (!analyticsData?.historical_data) return [];
    return analyticsData.historical_data.map((point) => ({
      date: format(new Date(point.timestamp), "EEE"), // Mon, Tue, etc.
      level: point.river_level_m,
    }));
  }, [analyticsData]);

  const riverStats = useMemo(() => {
    if (!analyticsData?.summary_stats) return defaultStats;
    return {
      current: analyticsData.summary_stats.current_level,
      avg: analyticsData.summary_stats.avg_level,
      max: analyticsData.summary_stats.max_level,
      min: analyticsData.summary_stats.min_level,
      trend: calculateTrendPercentage(analyticsData),
    };
  }, [analyticsData]);
};
```

#### ⚠️ **Data Gaps Identified**

1. **Weather Time-Series Missing** - Analytics endpoint only returns river levels, not weather history
   - **API Available:** Weather data exists in database (`Weather` table)
   - **Backend Change Required:** Enhance analytics endpoint to include weather time-series
2. **Temperature & Humidity Charts** - No historical weather data in analytics response
   - **Solution:** Add weather history to `get_analytics_data()` in `location/service.py`
3. **Correlation Data** - Combined rainfall/river chart needs synchronized timestamps
   - **Solution:** Join river and weather queries by timestamp in analytics service

#### 🆕 **BACKEND CHANGES REQUIRED**

**File:** `/api/app/features/location/service.py`

**New Function Needed:**

```python
def get_analytics_data_with_weather(session: Session, location_id: int, hours_back: int = 24) -> Dict[str, Any]:
    """Enhanced analytics including weather time-series"""

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)

    # Get historical river levels (already implemented)
    historical_levels = session.query(RiverLevel).filter(...).all()

    # ⚠️ NEW: Get historical weather data
    historical_weather = session.query(Weather).filter(
        Weather.location_id == location_id,
        Weather.timestamp >= cutoff_time
    ).order_by(Weather.timestamp.asc()).all()

    # Format weather history
    weather_data = [
        {
            "timestamp": weather.timestamp.isoformat(),
            "rainfall_mm": weather.actual_rainfall_mm,
            "temperature_c": weather.actual_temperature_c,
            "humidity_percent": weather.actual_humidity_percent,
            "windspeed_kmh": weather.actual_windspeed_kmh
        }
        for weather in historical_weather
    ]

    return {
        # ... existing fields
        "weather_history": weather_data,  # NEW FIELD
        "correlation_data": create_correlation_series(historical_levels, historical_weather)  # NEW
    }
```

**New Route Needed:**

```python
# In /api/app/features/analytics/routes.py

@router.get("/{location_id}/detailed")
async def get_detailed_analytics(
    location_id: int,
    session: SessionDep,
    hours_back: int = Query(default=24, ge=1, le=168)
) -> Dict[str, Any]:
    """Get analytics with weather and correlation data"""
    return get_analytics_data_with_weather(session, location_id, hours_back)
```

---

## 3. AlertsSection Component Analysis

### Current Implementation

- **Location:** `/frontend/src/components/AlertsSection.tsx`
- **Purpose:** Display active flood alerts with severity levels and action items
- **Technology:** React, shadcn/ui Alert components
- **Data Source:** Currently uses **hardcoded alert array**

### Static Data Used

```typescript
const activeAlerts = [
  {
    id: 1,
    level: "critical",
    title: "Extreme Flood Warning - Port of Spain",
    location: "Port of Spain, Western Trinidad",
    time: "Issued 08:45 UTC",
    description: "Immediate evacuation recommended...",
    actions: ["Evacuate now", "Move to higher ground", ...]
  },
  // ... 3 hardcoded alerts
];

const preparednessInfo = [
  { icon: Navigation, title: "Evacuation Routes", ... },
  // ... static resources
];
```

### API Integration Requirements

#### ✅ **ALREADY AVAILABLE** - Existing Backend Support

Your backend **already generates real-time alerts**:

1. **GET `/api/system-update`** - Includes alerts array

   ```json
   {
     "locations": [...],
     "system_status": {...},
     "alerts": [
       {
         "level": "high",
         "location": "Caroni",
         "message": "HIGH flood risk in Caroni - River level: 3.8m",
         "timestamp": "2025-10-27T14:23:15.123Z"
       }
     ],
     "timestamp": "..."
   }
   ```

2. **Frontend Hook Already Exists:**

   ```typescript
   // Already in useApiData.ts
   const { alerts, criticalAlerts, highAlerts } = useSystemAlerts();
   ```

3. **Alert Generation Logic:**
   - Located in `location/service.py:generate_system_alerts()`
   - Automatically creates alerts for ELEVATED, MEDIUM, HIGH, CRITICAL risk levels
   - Updates every 3 seconds (demo mode)

#### 🔧 **Frontend Changes Required**

**File:** `/frontend/src/components/AlertsSection.tsx`

**Changes:**

1. **Replace `activeAlerts` array** with `useSystemAlerts()` hook data
2. **Transform API alert format** to component format:
   ```typescript
   const transformAlert = (apiAlert, index) => ({
     id: index + 1,
     level: mapApiLevelToComponent(apiAlert.level), // "high" → "high"
     title: generateTitle(apiAlert.level, apiAlert.location),
     location: apiAlert.location,
     time: `Issued ${formatTime(apiAlert.timestamp)}`,
     description: apiAlert.message,
     actions: generateActionItems(apiAlert.level),
   });
   ```
3. **Add auto-refresh** - Already handled by `useSystemAlerts()` (3s interval)
4. **Keep preparedness info static** (or fetch from CMS/database if needed)
5. **Add empty state** when no alerts active

**Example Integration:**

```typescript
import { useSystemAlerts } from "@/lib/hooks/useApiData";

const AlertsSection = () => {
  const { alerts, isLoading, criticalAlerts, highAlerts } = useSystemAlerts();

  const transformedAlerts = useMemo(() => {
    return alerts.map((alert, idx) => ({
      id: idx + 1,
      level: alert.level, // Already matches: "critical", "high", "medium"
      title: `Flood ${alert.level.toUpperCase()} - ${alert.location}`,
      location: alert.location,
      time: `Issued ${format(new Date(alert.timestamp), "HH:mm")} UTC`,
      description: alert.message,
      actions: generateActionsForLevel(alert.level),
    }));
  }, [alerts]);

  const generateActionsForLevel = (level: string) => {
    switch (level) {
      case "critical":
        return [
          "Evacuate immediately",
          "Move to higher ground",
          "Call emergency services",
        ];
      case "high":
        return ["Prepare to evacuate", "Secure property", "Monitor updates"];
      case "medium":
      case "elevated":
        return ["Stay alert", "Avoid low areas", "Check drainage"];
      default:
        return ["Monitor conditions"];
    }
  };

  if (isLoading) return <LoadingState />;
  if (alerts.length === 0) return <NoAlertsState />;

  return (
    <section className="py-16 px-6">
      {/* ... render transformedAlerts */}
    </section>
  );
};
```

#### ⚠️ **Data Gaps Identified**

1. **Alert Titles** - API only provides generic message, not descriptive title
   - **Solution:** Generate titles on frontend based on level + location
2. **Action Items** - Not included in API alert structure
   - **Solution:** Generate on frontend based on alert level (as shown above)
3. **Alert Descriptions** - Current API message is brief technical format
   - **Solution:** Enhance backend to include user-friendly description OR format on frontend
4. **Preparedness Resources** - Static information (evacuation routes, shelters, contacts)
   - **Solution:** Keep as static data OR create database table for dynamic updates

#### 🆕 **BACKEND ENHANCEMENTS (OPTIONAL)**

**File:** `/api/app/features/location/service.py`

**Enhanced Alert Generation:**

```python
def generate_system_alerts(session: Session) -> List[Dict[str, str]]:
    """Generate detailed system alerts with action items"""
    alerts = []
    locations = get_all_locations(session)

    for location in locations:
        river_data = get_latest_river_data(session, location.name)
        if river_data:
            risk = calculate_flood_risk(river_data.river_level_m)
            if risk in ["ELEVATED", "MEDIUM", "HIGH", "CRITICAL"]:
                alerts.append({
                    "level": risk.lower(),
                    "location": location.name,
                    "message": f"{risk} flood risk in {location.name}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    # ⚠️ NEW FIELDS
                    "title": generate_alert_title(risk, location.name),
                    "description": generate_alert_description(risk, river_data),
                    "action_items": generate_action_items(risk),
                    "severity_score": get_severity_score(risk, river_data)
                })

    return alerts

def generate_alert_title(risk: str, location: str) -> str:
    titles = {
        "CRITICAL": f"⚠️ EXTREME FLOOD WARNING - {location}",
        "HIGH": f"🚨 FLOOD WARNING - {location}",
        "MEDIUM": f"⚡ FLOOD WATCH - {location}",
        "ELEVATED": f"📍 FLOOD ADVISORY - {location}"
    }
    return titles.get(risk, f"Alert - {location}")

def generate_alert_description(risk: str, river_data: RiverLevel) -> str:
    descriptions = {
        "CRITICAL": f"Immediate evacuation recommended. River level at {river_data.river_level_m}m - approaching maximum capacity. Flooding expected within 2-4 hours.",
        "HIGH": f"Prepare to evacuate. River level at {river_data.river_level_m}m and rising {river_data.change_in_level_m:+.3f}m per cycle. Monitor conditions closely.",
        "MEDIUM": f"Flooding likely in low-lying areas. River level at {river_data.river_level_m}m. Avoid unnecessary travel near waterways.",
        "ELEVATED": f"Conditions deteriorating. River level at {river_data.river_level_m}m approaching flood threshold. Stay alert."
    }
    return descriptions.get(risk, "Monitor flood conditions")

def generate_action_items(risk: str) -> List[str]:
    actions = {
        "CRITICAL": ["Evacuate immediately", "Move to higher ground", "Call emergency: 110"],
        "HIGH": ["Prepare emergency kit", "Secure property", "Monitor weather updates"],
        "MEDIUM": ["Avoid low areas", "Check drainage", "Prepare to evacuate"],
        "ELEVATED": ["Stay informed", "Avoid travel near rivers", "Monitor conditions"]
    }
    return actions.get(risk, ["Monitor conditions"])
```

---

## 4. Summary of Required Changes

### Frontend Changes (Required)

| Component         | File                | Changes Needed                                                                | Effort | Data Available          |
| ----------------- | ------------------- | ----------------------------------------------------------------------------- | ------ | ----------------------- |
| **RiskMap**       | `RiskMap.tsx`       | Replace static locations with `useLocations()`, add real-time weather display | Medium | ✅ Yes (partial)        |
| **DataAnalytics** | `DataAnalytics.tsx` | Connect to `useLocationAnalytics()`, transform data for Recharts              | High   | ⚠️ Partial (river only) |
| **AlertsSection** | `AlertsSection.tsx` | Replace alerts with `useSystemAlerts()`, add action generation                | Low    | ✅ Yes                  |

### Backend Changes

| Priority   | Component     | File                    | Change Description                                | Effort |
| ---------- | ------------- | ----------------------- | ------------------------------------------------- | ------ |
| **HIGH**   | DataAnalytics | `location/service.py`   | Add weather time-series to analytics              | Medium |
| **HIGH**   | DataAnalytics | `analytics/routes.py`   | New endpoint for detailed analytics with weather  | Low    |
| **MEDIUM** | RiskMap       | `location/contoller.py` | Add wind speed to real-time conditions            | Low    |
| **LOW**    | AlertsSection | `location/service.py`   | Enhance alerts with titles, descriptions, actions | Medium |
| **LOW**    | RiskMap       | New table/model         | Add population data to Location model             | Low    |

### Data Gaps Summary

#### ✅ **No Backend Changes Needed**

- Location coordinates and risk levels (RiskMap)
- River level time-series (DataAnalytics - river chart only)
- Real-time conditions and alerts (AlertsSection)

#### ⚠️ **Backend Enhancement Required**

- **Weather time-series** for DataAnalytics charts (rainfall, temperature, humidity)
  - **Data exists** in Weather table but not exposed in analytics endpoint
  - **Action:** Modify `get_analytics_data()` to include weather history

#### 📋 **Optional Enhancements**

- Population data for locations (RiskMap markers)
- Flood zone polygons (RiskMap overlays)
- Tide/surge data (RiskMap environmental factors)
- Enhanced alert messages with action items (AlertsSection)
- Wind speed in real-time endpoint (RiskMap)

---

## 5. Recommended Migration Path

### Phase 1: AlertsSection (Easiest - Start Here)

**Estimated Time:** 2-3 hours

1. ✅ **No backend changes required** - All data already available
2. Replace `activeAlerts` array with `useSystemAlerts()` hook
3. Transform alert data to component format
4. Add action item generation logic on frontend
5. Test with live data
6. Add empty state for no alerts

**Why Start Here:**

- Minimal changes required
- Immediate value to users
- Builds confidence with API integration
- No backend work needed

### Phase 2: RiskMap (Medium Complexity)

**Estimated Time:** 4-6 hours

1. Replace static `riskLevels` with `useLocations()` and `useSystemUpdate()`
2. Add risk level mapping function (API → Component format)
3. Keep flood zones static for now (or make optional backend table)
4. Add location selection to show real-time weather
5. **Optional backend:** Add wind speed to real-time endpoint (30 min)
6. Keep population static or add to database
7. Test with all 8 locations rendering correctly

**Why Second:**

- Most data already available
- Visual impact for users
- Few backend changes needed
- Can iterate on enhancements later

### Phase 3: DataAnalytics (Most Complex)

**Estimated Time:** 8-12 hours (includes backend work)

#### Backend Work (4-6 hours)

1. Enhance `get_analytics_data()` to include weather time-series
2. Add correlation data generation
3. Create new detailed analytics endpoint
4. Test with various time ranges (24h, 7d, 30d)

#### Frontend Work (4-6 hours)

1. Add location selector dropdown
2. Connect to analytics API hooks
3. Transform data for all 4 chart types:
   - Rainfall chart (from weather_history)
   - River gauge chart (from historical_data)
   - Temperature chart (from weather_history)
   - Humidity chart (from weather_history)
4. Implement statistics calculations
5. Add loading states and error handling
6. Test with different time ranges and locations

**Why Last:**

- Requires backend modifications
- Most complex data transformation
- Multiple chart types to implement
- Depends on Phase 1 & 2 patterns

---

## 6. Testing Checklist

### Per Component Testing

#### RiskMap

- [ ] All 8 locations render on map with correct coordinates
- [ ] Risk levels update every 3 seconds (demo mode)
- [ ] Markers show correct colors based on flood risk
- [ ] Popups display location name, risk, and data
- [ ] Forecast slider works (if kept)
- [ ] Environmental factors show real data when location selected
- [ ] Map centers on Trinidad & Tobago
- [ ] Legend displays correctly

#### DataAnalytics

- [ ] Location selector shows all available locations
- [ ] Charts load historical data for selected location
- [ ] Time range selector (24h, 7d, 30d) works correctly
- [ ] All 4 charts display correct data:
  - [ ] Rainfall chart shows mm values
  - [ ] River gauge chart shows meter values with alert lines
  - [ ] Temperature chart shows °C values
  - [ ] Humidity chart shows % values
- [ ] Statistics calculate correctly (current, avg, max, min, trend)
- [ ] Combined rainfall/river correlation chart works
- [ ] Live badge updates timestamp
- [ ] Export button (if implemented)

#### AlertsSection

- [ ] Active alerts display when flood risk exists
- [ ] Empty state shows when no alerts
- [ ] Alert cards color-code by severity (critical=red, high=orange, etc.)
- [ ] Timestamps format correctly (UTC)
- [ ] Action items generate based on alert level
- [ ] Alerts update every 3 seconds (demo mode)
- [ ] Preparedness resources display correctly
- [ ] Critical alerts appear first (if sorting implemented)

### Integration Testing

- [ ] All components work simultaneously without conflicts
- [ ] Data refreshes consistently across all components
- [ ] No memory leaks from React Query subscriptions
- [ ] Browser console shows no errors
- [ ] Network tab shows efficient API calls (not redundant)
- [ ] Components handle loading states gracefully
- [ ] Components handle error states gracefully
- [ ] Mobile responsiveness maintained

---

## 7. Code Templates

### Risk Level Mapping Utility

Create: `/frontend/src/lib/utils/riskMapping.ts`

```typescript
/**
 * Map API flood risk levels to component display formats
 */
export type ApiRiskLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "ELEVATED" | "LOW";
export type ComponentRiskLevel =
  | "critical"
  | "high-risk"
  | "moderate"
  | "low-risk"
  | "safe";

export const mapApiRiskToComponent = (apiRisk: string): ComponentRiskLevel => {
  const mapping: Record<ApiRiskLevel, ComponentRiskLevel> = {
    CRITICAL: "critical",
    HIGH: "high-risk",
    MEDIUM: "moderate",
    ELEVATED: "low-risk",
    LOW: "safe",
  };
  return mapping[apiRisk as ApiRiskLevel] || "safe";
};

export const getRiskColor = (risk: ComponentRiskLevel): string => {
  const colors: Record<ComponentRiskLevel, string> = {
    critical: "bg-critical text-critical-foreground",
    "high-risk": "bg-high-risk text-high-risk-foreground",
    moderate: "bg-moderate text-moderate-foreground",
    "low-risk": "bg-low-risk text-low-risk-foreground",
    safe: "bg-safe text-safe-foreground",
  };
  return colors[risk];
};

export const getRiskHexColor = (risk: ComponentRiskLevel): string => {
  const colors: Record<ComponentRiskLevel, string> = {
    critical: "#ef4444",
    "high-risk": "#f97316",
    moderate: "#eab308",
    "low-risk": "#84cc16",
    safe: "#22c55e",
  };
  return colors[risk];
};
```

### Analytics Data Transformer

Create: `/frontend/src/lib/utils/analyticsTransformers.ts`

```typescript
import { format, parseISO } from "date-fns";
import type { AnalyticsData } from "@/lib/hooks/useApiData";

export interface ChartDataPoint {
  date: string;
  value: number;
}

export const transformRiverData = (
  analyticsData: AnalyticsData | undefined
): ChartDataPoint[] => {
  if (!analyticsData?.historical_data) return [];

  return analyticsData.historical_data.map((point) => ({
    date: format(parseISO(point.timestamp), "EEE"), // Mon, Tue, Wed
    value: point.river_level_m,
  }));
};

export const transformWeatherData = (
  analyticsData: AnalyticsData | undefined,
  field: "rainfall_mm" | "temperature_c" | "humidity_percent"
): ChartDataPoint[] => {
  if (!analyticsData?.weather_history) return [];

  return analyticsData.weather_history.map((point) => ({
    date: format(parseISO(point.timestamp), "EEE"),
    value: point[field],
  }));
};

export const calculateTrendPercentage = (
  analyticsData: AnalyticsData | undefined
): number => {
  if (
    !analyticsData?.historical_data ||
    analyticsData.historical_data.length < 2
  )
    return 0;

  const data = analyticsData.historical_data;
  const recentCount = Math.min(5, data.length);
  const recentAvg =
    data.slice(-recentCount).reduce((sum, p) => sum + p.river_level_m, 0) /
    recentCount;
  const olderAvg =
    data.slice(0, recentCount).reduce((sum, p) => sum + p.river_level_m, 0) /
    recentCount;

  return olderAvg > 0 ? ((recentAvg - olderAvg) / olderAvg) * 100 : 0;
};
```

### Alert Action Generator

Create: `/frontend/src/lib/utils/alertActions.ts`

```typescript
export const generateActionItemsForLevel = (level: string): string[] => {
  const actions: Record<string, string[]> = {
    critical: [
      "Evacuate immediately to higher ground",
      "Call emergency services: 110",
      "Avoid all flooded areas",
    ],
    high: [
      "Prepare emergency kit and evacuation plan",
      "Secure property and valuables",
      "Monitor weather updates continuously",
    ],
    medium: [
      "Avoid low-lying areas and flood-prone roads",
      "Check drainage systems",
      "Stay informed about conditions",
    ],
    elevated: [
      "Stay alert and monitor conditions",
      "Avoid travel near rivers and streams",
      "Prepare for potential evacuation",
    ],
  };

  return actions[level] || ["Monitor flood conditions"];
};

export const generateAlertTitle = (level: string, location: string): string => {
  const titles: Record<string, string> = {
    critical: `⚠️ EXTREME FLOOD WARNING - ${location}`,
    high: `🚨 Flood Warning - ${location}`,
    medium: `⚡ Flood Watch - ${location}`,
    elevated: `📍 Flood Advisory - ${location}`,
  };

  return titles[level] || `Alert - ${location}`;
};

export const generateAlertDescription = (
  apiMessage: string,
  level: string
): string => {
  // Can enhance API message or return as-is
  return apiMessage;
};
```

---

## 8. API Documentation Reference

### Available Endpoints (Current Backend)

```typescript
// Base URL: http://localhost:8000

// ===== LOCATION ENDPOINTS =====
GET /api/locations
// Returns: LocationsResponse { locations: Location[], total: number }
// Refresh: 3s (demo mode)

GET /api/system-update
// Returns: ComprehensiveUpdate { locations, system_status, alerts, timestamp }
// Refresh: 3s (demo mode)

GET /api/real-time/{location}
// Returns: RealTimeConditions { location, timestamp, river_conditions, weather, social_activity, insights }
// Refresh: 3s (demo mode)

GET /api/timeline/{location}?minutes=5
// Returns: LocationTimeline { location, timeline[], summary }
// Refresh: 3s (demo mode)

GET /api/history/{location}?points=20
// Returns: LocationHistory { location, current, history[], trend, stats }
// Refresh: 3s (demo mode)

// ===== ANALYTICS ENDPOINTS =====
GET /api/analytics/{location_id}?hours_back=24
// Returns: AnalyticsData { location, time_range, historical_data[], predictions[], summary_stats, accuracy_metrics }
// Refresh: 3s (demo mode)

GET /api/analytics/
// Returns: Summary for all locations

POST /api/analytics/{location_id}/predictions
// Triggers: New prediction generation

GET /api/predictions/status
// Returns: PredictionStatusData { running, intervals, last_cleanup, task_active }

// ===== DATA STATISTICS =====
GET /api/data-statistics
// Returns: Database statistics { total_locations, total_data_points, counts, latest_update }
```

### React Query Hooks (Already Available)

```typescript
// From @/lib/hooks/useApiData

// System-wide data
useSystemUpdate(); // Comprehensive update every 3s
useLocations(); // All locations with current risk
useFloodLocations(); // Transformed for compatibility
useSystemAlerts(); // Derived alerts from system update
useSystemStatus(); // Derived status from system update

// Location-specific data
useRealTimeConditions(location, enabled);
useLocationTimeline(location, minutes, enabled);
useLocationHistory(location, points, enabled);

// Analytics data
useLocationAnalytics(locationName, hoursBack, enabled);
useLocationAnalyticsById(locationId, hoursBack, enabled);

// Prediction management
usePredictionStatus();
useGeneratePredictions(); // Mutation hooks

// Utilities
useDataFreshness(); // Data age indicators
usePrefetchLocationData(); // Background prefetching
```

---

## 9. Known Limitations & Trade-offs

### Current System Constraints

1. **SQLite Database**

   - Returns naive datetimes (timezone-aware checks added)
   - Limited concurrent write performance (not an issue for read-heavy analytics)

2. **Demo Mode (3-second refresh)**

   - High API call frequency (intentional for demo)
   - May need adjustment for production (change constants in `useApiData.ts`)

3. **8 Locations Only**

   - Current system has 8 river monitoring stations
   - RiskMap component designed for 5 hardcoded cities (will need mapping)

4. **No Historical Weather in Analytics**
   - Current analytics endpoint only returns river levels
   - Phase 3 requires backend enhancement to add weather time-series

### Design Decisions to Make

1. **Population Data**

   - **Option A:** Keep hardcoded in RiskMap component (simplest)
   - **Option B:** Add population field to Location database model (scalable)
   - **Recommendation:** Option A for MVP, Option B for production

2. **Flood Zone Polygons**

   - **Option A:** Keep static polygons in RiskMap (no DB changes)
   - **Option B:** Create FloodZone table with geometry columns (complex)
   - **Recommendation:** Option A - Static zones are acceptable for fixed geography

3. **Alert Enhancements**

   - **Option A:** Generate titles/actions on frontend (faster, no backend changes)
   - **Option B:** Enhance backend alert generation (more consistent, centralized logic)
   - **Recommendation:** Option A for MVP, Option B if alerts become more complex

4. **Weather Charts Time Range**
   - **Option A:** Match available data (up to 7 days if data exists)
   - **Option B:** Sample/aggregate for longer ranges (30 days)
   - **Recommendation:** Start with Option A, implement aggregation if performance issues

---

## 10. Next Steps

### Immediate Actions (Before Coding)

1. **Review this document** with team/stakeholders
2. **Prioritize phases** - Confirm Phase 1 → 2 → 3 order
3. **Assign resources** - Backend dev for Phase 3 weather endpoint
4. **Set timeline** - Estimate 2-3 days for all phases
5. **Create feature branch** - `feature/new-component-integration`

### Development Workflow

```bash
# 1. Create branch
git checkout -b feature/new-component-integration

# 2. Phase 1: AlertsSection
git checkout -b feature/alerts-integration
# ... implement AlertsSection changes
git commit -m "feat: integrate AlertsSection with live alerts API"

# 3. Phase 2: RiskMap
git checkout -b feature/riskmap-integration
# ... implement RiskMap changes
git commit -m "feat: integrate RiskMap with locations API"

# 4. Phase 3: Backend Weather Endpoint
git checkout -b feature/analytics-weather-endpoint
# ... implement backend changes
git commit -m "feat: add weather time-series to analytics endpoint"

# 5. Phase 3: DataAnalytics Frontend
git checkout -b feature/analytics-integration
# ... implement DataAnalytics changes
git commit -m "feat: integrate DataAnalytics with enhanced analytics API"

# 6. Merge to main
git checkout demo-1
git merge feature/new-component-integration
```

### Documentation Updates

After completing integration:

- [ ] Update API documentation with new endpoints (if added)
- [ ] Add component usage examples to README
- [ ] Document data refresh intervals for production
- [ ] Create troubleshooting guide for common issues

---

## Appendix A: Database Schema Reference

### Current Tables

```python
# Location Model
class Location(Base):
    id: int
    name: str  # "Caroni", "Arima", etc.
    sensor_id: str  # "CRN-001"
    latitude: float  # 10.6167
    longitude: float  # -61.4167
    # Relationships: river_levels, weather_data, social_data, predictions

# RiverLevel Model
class RiverLevel(Base):
    id: int
    location_id: int (FK)
    timestamp: DateTime(timezone=True)
    river_level_m: float
    change_in_level_m: float

# Weather Model
class Weather(Base):
    id: int
    location_id: int (FK)
    timestamp: DateTime(timezone=True)
    # Predicted values
    predicted_rainfall_mm: float
    predicted_temperature_c: float
    predicted_humidity_percent: float
    predicted_windspeed_kmh: float
    predicted_storm: bool
    # Actual values
    actual_rainfall_mm: float
    actual_temperature_c: float
    actual_humidity_percent: float
    actual_windspeed_kmh: float
    actual_storm: bool

# RiverPrediction Model
class RiverPrediction(Base):
    id: int
    location_id: int (FK)
    prediction_timestamp: DateTime(timezone=True)
    predicted_for_time: DateTime(timezone=True)
    predicted_level_m: float
    confidence_score: float
    weather_factor_influence: float
    trend_factor_influence: float

# Social Model
class Social(Base):
    id: int
    location_id: int (FK)
    timestamp: DateTime(timezone=True)
    post_count: int
    sentiment_score: float
```

### Potential New Tables (Optional)

```python
# For enhanced RiskMap
class FloodZone(Base):
    id: int
    name: str  # "Port of Spain Coastal"
    risk_level: str  # "critical", "high", etc.
    coordinates: JSON  # GeoJSON polygon
    location_id: int (FK) - optional association

# For enhanced Location data
# Add to Location model:
class Location(Base):
    # ... existing fields
    population: int  # NEW
    elevation_m: float  # NEW - useful for flood risk
    zone_type: str  # NEW - "coastal", "river", "urban"
```

---

## Appendix B: Color Scheme Mapping

Ensure consistent color usage across all components:

```typescript
// Tailwind CSS classes (already in your system)
const colorClasses = {
  critical: "bg-critical text-critical-foreground", // Red
  "high-risk": "bg-high-risk text-high-risk-foreground", // Orange
  moderate: "bg-moderate text-moderate-foreground", // Yellow
  "low-risk": "bg-low-risk text-low-risk-foreground", // Light green
  safe: "bg-safe text-safe-foreground", // Green
};

// Hex colors for Leaflet/Recharts
const hexColors = {
  critical: "#ef4444", // Red-500
  "high-risk": "#f97316", // Orange-500
  moderate: "#eab308", // Yellow-500
  "low-risk": "#84cc16", // Lime-500
  safe: "#22c55e", // Green-500
};

// Recharts CSS variables
const rechartsColors = {
  primary: "var(--primary)", // Default blue
  critical: "var(--color-critical)",
  highRisk: "var(--color-high-risk)",
  moderate: "var(--color-moderate)",
  lowRisk: "var(--color-low-risk)",
  safe: "var(--color-safe)",
};
```

---

**End of Migration Plan**

This document should be updated as implementation progresses. Mark sections complete and add notes about deviations from the plan.

**Last Updated:** October 27, 2025  
**Status:** ✅ Ready for Implementation  
**Approved By:** [Pending Review]
