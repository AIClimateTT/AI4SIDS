import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService, dataTransformers } from '../api/client';
import type {
    ComprehensiveUpdate,
    RealTimeConditions,
    LocationsResponse,
    LocationTimeline,
    LocationHistory,
    ApiStatus
} from '../api/types';
import type { FloodLocation } from '@/types';
import {env} from '@/lib/env/server';

// Query keys for consistent caching
export const queryKeys = {
    systemUpdate: ['system-update'] as const,
    locations: ['locations'] as const,
    realTime: (location: string) => ['real-time', location] as const,
    timeline: (location: string, minutes: number) => ['timeline', location, minutes] as const,
    locationHistory: (location: string, points: number) => ['location-history', location, points] as const,
    apiStatus: ['api-status'] as const,
    analytics: (location: string, hoursBack: number) => ['analytics', location, hoursBack] as const,
    analyticsById: (locationId: number, hoursBack: number) => ['analytics-by-id', locationId, hoursBack] as const,
    predictionStatus: ['prediction-status'] as const,
} as const;

// Configuration constants
// === VIDEO RECORDING MODE ===
const REAL_TIME_REFETCH_INTERVAL = 1 * 1000; // 1 second to match API cycle (fast for demo)
const STALE_TIME_DEMO = 2 * 1000; // 2 seconds stale time for demo mode
// === PRODUCTION MODE ===
// const REAL_TIME_REFETCH_INTERVAL = 15 * 1000; // 15 seconds to match API cycle
const STALE_TIME_PROD = 15 * 1000; // 15 seconds stale time for production
const SYSTEM_UPDATE_REFETCH_INTERVAL = 1 * 1000; // 1 second
const LOCATIONS_REFETCH_INTERVAL = 1 * 1000; // 1 second for demo
const ANALYTICS_REFETCH_INTERVAL = 1 * 1000; // 1 second for analytics data
const PREDICTION_STATUS_REFETCH_INTERVAL = 1 * 1000; // 1 second for prediction status

// === NORMAL PRODUCTION MODE (COMMENTED OUT) ===
// const REAL_TIME_REFETCH_INTERVAL = 15 * 1000; // 15 seconds to match API cycle
// const SYSTEM_UPDATE_REFETCH_INTERVAL = 15 * 1000; // 15 seconds
// const LOCATIONS_REFETCH_INTERVAL = 60 * 1000; // 1 minute (locations change less frequently)
// const ANALYTICS_REFETCH_INTERVAL = 60 * 1000; // 1 minute for analytics data
// const PREDICTION_STATUS_REFETCH_INTERVAL = 30 * 1000; // 30 seconds for prediction status

/**
 * Hook to get comprehensive system update with auto-refresh
 */
export function useSystemUpdate(): UseQueryResult<ComprehensiveUpdate, Error> {
    return useQuery({
        queryKey: queryKeys.systemUpdate,
        queryFn: apiService.getSystemUpdate,
        refetchInterval: SYSTEM_UPDATE_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: 2 * 1000, // Consider data stale after 2 seconds (demo mode)
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get all available locations with auto-refresh
 */
export function useLocations(): UseQueryResult<LocationsResponse, Error> {
    return useQuery({
        queryKey: queryKeys.locations,
        queryFn: apiService.getLocations,
        refetchInterval: LOCATIONS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME_DEMO,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get locations formatted as FloodLocation array for compatibility
 */
export function useFloodLocations(): UseQueryResult<FloodLocation[], Error> {
    return useQuery({
        queryKey: [...queryKeys.locations, 'flood-format'],
        queryFn: async () => {
            const response = await apiService.getLocations();
            return dataTransformers.apiLocationsToFloodLocations(response.locations);
        },
        refetchInterval: LOCATIONS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME_DEMO,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get real-time conditions for a specific location
 */
export function useRealTimeConditions(
    location: string | null,
    enabled: boolean = true
): UseQueryResult<RealTimeConditions, Error> {
    return useQuery({
        queryKey: location ? queryKeys.realTime(location) : [],
        queryFn: () => (location ? apiService.getRealTimeConditions(location) : Promise.reject('No location')),
        enabled: enabled && !!location,
        refetchInterval: REAL_TIME_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME_DEMO,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get timeline data for a specific location
 */
export function useLocationTimeline(
    location: string | null,
    minutes: number = 5,
    enabled: boolean = true
): UseQueryResult<LocationTimeline, Error> {
    return useQuery({
        queryKey: location ? queryKeys.timeline(location, minutes) : [],
        queryFn: () => (location ? apiService.getLocationTimeline(location, minutes) : Promise.reject('No location')),
        enabled: enabled && !!location,
        refetchInterval: REAL_TIME_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME_DEMO,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get location history data for sparklines
 */
export function useLocationHistory(
    location: string | null,
    points: number = 20,
    enabled: boolean = true
): UseQueryResult<LocationHistory, Error> {
    return useQuery({
        queryKey: location ? queryKeys.locationHistory(location, points) : [],
        queryFn: () => (location ? apiService.getLocationHistory(location, points) : Promise.reject('No location')),
        enabled: enabled && !!location,
        refetchInterval: REAL_TIME_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME_DEMO,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get API status
 */
export function useApiStatus(): UseQueryResult<ApiStatus, Error> {
    return useQuery({
        queryKey: queryKeys.apiStatus,
        queryFn: apiService.getApiStatus,
        refetchInterval: 3 * 1000, // Check API status every 3 seconds (demo mode)
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME_DEMO,
        retry: 2,
        retryDelay: 5000,
    });
}

/**
 * Derived hook to get system alerts from system update
 */
export function useSystemAlerts() {
    const { data: systemUpdate, isLoading, error } = useSystemUpdate();

    return {
        alerts: systemUpdate?.alerts || [],
        isLoading,
        error,
        hasAlerts: (systemUpdate?.alerts?.length || 0) > 0,
        criticalAlerts: systemUpdate?.alerts?.filter(alert => alert.level === 'critical') || [],
        highAlerts: systemUpdate?.alerts?.filter(alert => alert.level === 'high') || [],
    };
}

/**
 * Derived hook to get system status information
 */
export function useSystemStatus() {
    const { data: systemUpdate, isLoading, error } = useSystemUpdate();

    return {
        systemStatus: systemUpdate?.system_status,
        isLoading,
        error,
        activeSensors: systemUpdate?.system_status?.active_sensors || 0,
        dataCycleProgress: systemUpdate?.system_status?.data_cycle_progress || '0%',
        nextUpdateSeconds: systemUpdate?.system_status?.next_update_seconds || 0,
        totalAlerts: systemUpdate?.system_status?.total_alerts || 0,
        lastUpdated: systemUpdate?.timestamp,
    };
}

/**
 * Hook for background data prefetching
 */
export function usePrefetchLocationData() {
    const { data: locations } = useLocations();

    // This can be used to prefetch real-time data for visible locations
    // Implementation can be added based on UI needs
    return {
        prefetchRealTime: (_location: string) => {
            // Could implement prefetching logic here if needed
        },
        availableLocations: locations?.locations || [],
    };
}

/**
 * Custom hook for managing data freshness indicators
 */
export function useDataFreshness() {
    const { dataUpdatedAt: systemUpdateTime } = useSystemUpdate();
    const { dataUpdatedAt: locationsUpdateTime } = useLocations();

    const getTimeSinceUpdate = (timestamp: number) => {
        const now = Date.now();
        const diffMs = now - timestamp;
        const diffSeconds = Math.floor(diffMs / 1000);

        if (diffSeconds < 60) {
            return `${diffSeconds}s ago`;
        } else if (diffSeconds < 3600) {
            const minutes = Math.floor(diffSeconds / 60);
            return `${minutes}m ago`;
        } else {
            const hours = Math.floor(diffSeconds / 3600);
            return `${hours}h ago`;
        }
    };

    return {
        systemUpdateFreshness: systemUpdateTime ? getTimeSinceUpdate(systemUpdateTime) : 'Never',
        locationsFreshness: locationsUpdateTime ? getTimeSinceUpdate(locationsUpdateTime) : 'Never',
        isDataFresh: (timestamp: number) => Date.now() - timestamp < 30000, // Fresh if updated within 30 seconds
    };
}

// Analytics data types
export interface AnalyticsData {
    location: {
        id: number;
        name: string;
        latitude: number;
        longitude: number;
    };
    time_range: {
        hours_back: number;
        start_time: string;
        end_time: string;
    };
    historical_data: Array<{
        timestamp: string;
        river_level_m: number;
        change_in_level_m: number;
        flood_risk: string;
    }>;
    predictions: Array<{
        predicted_for_time: string;
        predicted_level_m: number;
        confidence_score: number;
        weather_influence: number;
        flood_risk: string;
    }>;
    summary_stats: {
        min_level: number;
        max_level: number;
        avg_level: number;
        current_level: number;
        trend: string;
    };
    accuracy_metrics: {
        accuracy_percentage: number;
        average_error: number;
        total_predictions: number;
        accurate_predictions: number;
    };
    data_counts: {
        historical_points: number;
        prediction_points: number;
    };
}

export interface PredictionStatusData {
    running: boolean;
    prediction_interval_seconds: number;
    cleanup_interval_seconds: number;
    last_cleanup: string | null;
    task_active: boolean;
}

export interface PredictionGenerationResult {
    success: boolean;
    message: string;
    predictions_count?: number;
    location_id?: number;
}

/**
 * Hook to get analytics data for a specific location by name
 */
export function useLocationAnalytics(
    locationName: string | null,
    hoursBack: number = 24,
    enabled: boolean = true
): UseQueryResult<AnalyticsData, Error> {
    return useQuery({
        queryKey: locationName ? queryKeys.analytics(locationName, hoursBack) : [],
        queryFn: async () => {
            if (!locationName) throw new Error('No location name provided');
            const response = await fetch(
                `${env.VITE_API_URL}/api/analytics/by-name/${encodeURIComponent(locationName)}?hours_back=${hoursBack}`
            );
            if (!response.ok) {
                throw new Error(`Failed to fetch analytics: ${response.statusText}`);
            }
            return response.json();
        },
        enabled: enabled && !!locationName,
        refetchInterval: ANALYTICS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: 2 * 1000, // Consider data stale after 2 seconds (demo mode)
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get analytics data for a specific location by ID
 */
export function useLocationAnalyticsById(
    locationId: number | null,
    hoursBack: number = 24,
    enabled: boolean = true
): UseQueryResult<AnalyticsData, Error> {
    return useQuery({
        queryKey: locationId ? queryKeys.analyticsById(locationId, hoursBack) : [],
        queryFn: async () => {
            if (!locationId) throw new Error('No location ID provided');
            const response = await fetch(
                `${env.VITE_API_URL}/api/analytics/${locationId}?hours_back=${hoursBack}`
            );
            if (!response.ok) {
                throw new Error(`Failed to fetch analytics: ${response.statusText}`);
            }
            return response.json();
        },
        enabled: enabled && !!locationId,
        refetchInterval: ANALYTICS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: 2 * 1000, // Demo mode
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to get prediction task status
 */
export function usePredictionStatus(): UseQueryResult<PredictionStatusData, Error> {
    return useQuery({
        queryKey: queryKeys.predictionStatus,
        queryFn: async () => {
            const response = await fetch('${env.VITE_API_URL}/api/predictions/status');
            if (!response.ok) {
                throw new Error(`Failed to fetch prediction status: ${response.statusText}`);
            }
            return response.json();
        },
        refetchInterval: PREDICTION_STATUS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: 2 * 1000, // Demo mode
        retry: 2,
        retryDelay: 5000,
    });
}

/**
 * Hook to generate new predictions for a location (mutation)
 */
export function useGeneratePredictions() {
    return {
        generateByName: async (locationName: string): Promise<PredictionGenerationResult> => {
            const response = await fetch(
                `${env.VITE_API_URL}/api/analytics/by-name/${encodeURIComponent(locationName)}/predictions`,
                { method: 'POST' }
            );
            if (!response.ok) {
                throw new Error(`Failed to generate predictions: ${response.statusText}`);
            }
            return response.json();
        },
        generateById: async (locationId: number): Promise<PredictionGenerationResult> => {
            const response = await fetch(
                `${env.VITE_API_URL}/api/analytics/${locationId}/predictions`,
                { method: 'POST' }
            );
            if (!response.ok) {
                throw new Error(`Failed to generate predictions: ${response.statusText}`);
            }
            return response.json();
        },
        triggerGlobal: async (): Promise<{ success: boolean; message: string }> => {
            const response = await fetch(
                '${env.VITE_API_URL}/api/predictions/generate',
                { method: 'POST' }
            );
            if (!response.ok) {
                throw new Error(`Failed to trigger global predictions: ${response.statusText}`);
            }
            return response.json();
        }
    };
}