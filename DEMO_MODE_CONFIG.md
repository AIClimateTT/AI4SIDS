# Demo Mode Configuration

## Frontend Query Speed-up for Demo

### Changes Made

Updated all React Query refetch intervals from the normal production values (15s-60s) to **3 seconds** to match the backend's accelerated data generation cycle.

### File Modified

`/frontend/src/lib/hooks/useApiData.ts`

### Configuration Changes

#### Before (Production Mode):

```typescript
const REAL_TIME_REFETCH_INTERVAL = 15 * 1000; // 15 seconds
const SYSTEM_UPDATE_REFETCH_INTERVAL = 15 * 1000; // 15 seconds
const LOCATIONS_REFETCH_INTERVAL = 60 * 1000; // 1 minute
const ANALYTICS_REFETCH_INTERVAL = 60 * 1000; // 1 minute
const PREDICTION_STATUS_REFETCH_INTERVAL = 30 * 1000; // 30 seconds
```

#### After (Demo Mode):

```typescript
const REAL_TIME_REFETCH_INTERVAL = 3 * 1000; // 3 seconds
const SYSTEM_UPDATE_REFETCH_INTERVAL = 3 * 1000; // 3 seconds
const LOCATIONS_REFETCH_INTERVAL = 3 * 1000; // 3 seconds
const ANALYTICS_REFETCH_INTERVAL = 3 * 1000; // 3 seconds
const PREDICTION_STATUS_REFETCH_INTERVAL = 3 * 1000; // 3 seconds
```

#### StaleTime Updates:

All `staleTime` values updated from 10-30 seconds to **2 seconds** to ensure data is considered fresh immediately.

### Affected Hooks

1. ✅ `useSystemUpdate()` - 3s refresh
2. ✅ `useLocations()` - 3s refresh
3. ✅ `useFloodLocations()` - 3s refresh
4. ✅ `useRealTimeConditions()` - 3s refresh
5. ✅ `useLocationTimeline()` - 3s refresh
6. ✅ `useLocationHistory()` - 3s refresh
7. ✅ `useApiStatus()` - 3s refresh
8. ✅ `useLocationAnalytics()` - 3s refresh
9. ✅ `useLocationAnalyticsById()` - 3s refresh
10. ✅ `usePredictionStatus()` - 3s refresh

### Synchronized Timing

**Backend (data_simulator.py):**

- Data generation: Every **3 seconds**
- Prediction generation: Every **30 seconds**

**Frontend (useApiData.ts):**

- All queries: Every **3 seconds** ✅
- Matches backend cycle perfectly

### Benefits for Demo

1. **Immediate Updates**: Changes appear almost instantly on the frontend
2. **Smooth Animations**: River levels, charts, and predictions update smoothly
3. **Dramatic Effect**: Rapid flood scenario progression visible in real-time
4. **Better Engagement**: Audience sees live data flowing continuously

### Reverting to Production Mode

When switching back to production:

1. Open `/frontend/src/lib/hooks/useApiData.ts`
2. Comment out the "VIDEO RECORDING MODE" section
3. Uncomment the "NORMAL PRODUCTION MODE" section:
   ```typescript
   // === NORMAL PRODUCTION MODE ===
   const REAL_TIME_REFETCH_INTERVAL = 15 * 1000;
   const SYSTEM_UPDATE_REFETCH_INTERVAL = 15 * 1000;
   const LOCATIONS_REFETCH_INTERVAL = 60 * 1000;
   const ANALYTICS_REFETCH_INTERVAL = 60 * 1000;
   const PREDICTION_STATUS_REFETCH_INTERVAL = 30 * 1000;
   ```
4. Update staleTime values back to original (10-30 seconds)

### Performance Notes

- 3-second polling is more intensive than normal
- Acceptable for demo/testing scenarios
- For production, use the standard 15-60 second intervals
- React Query's intelligent caching minimizes unnecessary network requests
