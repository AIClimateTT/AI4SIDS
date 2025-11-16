import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService, dataTransformers } from '../api/client';
import type { AnalyticsData, PredictionStatusData } from '@/lib/types';
import type {
    ComprehensiveUpdate,
    RealTimeConditions,
    LocationsResponse,
    LocationTimeline,
    LocationHistory,
    ApiStatus,
    FloodLocation,
} from '../types';
import { env } from '@/lib/env/server';

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

// Convert environment variables from seconds to milliseconds
const REFETCH_INTERVAL = env.VITE_REFETCH_INTERVAL * 1000;
const LOCATIONS_REFETCH_INTERVAL = env.VITE_LOCATIONS_REFETCH_INTERVAL * 1000;
const ANALYTICS_REFETCH_INTERVAL = env.VITE_ANALYTICS_REFETCH_INTERVAL * 1000;
const PREDICTION_STATUS_REFETCH_INTERVAL = env.VITE_PREDICTION_STATUS_REFETCH_INTERVAL * 1000;
const STALE_TIME = env.VITE_STALE_TIME * 1000;
const RETRY_COUNT = env.VITE_RETRY_COUNT;
const RETRY_DELAY_BASE = env.VITE_RETRY_DELAY_BASE * 1000;

// Retry delay function with exponential backoff
const retryDelay = (attemptIndex: number) => Math.min(RETRY_DELAY_BASE * 2 ** attemptIndex, 30000);

/**
 * Hook to get comprehensive system update with auto-refresh
 */
export function useSystemUpdate(): UseQueryResult<ComprehensiveUpdate, Error> {
    return useQuery({
        queryKey: queryKeys.systemUpdate,
        queryFn: apiService.getSystemUpdate,
        refetchInterval: REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
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
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
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
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
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
        refetchInterval: REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
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
        refetchInterval: REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
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
        refetchInterval: REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
    });
}

/**
 * Hook to get API status
 */
export function useApiStatus(): UseQueryResult<ApiStatus, Error> {
    return useQuery({
        queryKey: queryKeys.apiStatus,
        queryFn: apiService.getApiStatus,
        refetchInterval: REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(RETRY_DELAY_BASE * 2 ** attemptIndex, 30000),
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
        isDataFresh: (timestamp: number) => Date.now() - timestamp < (env.VITE_DATA_FRESH_THRESHOLD * 1000),
    };
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
        queryFn: () => locationName ? apiService.getAnalyticsByName(locationName, hoursBack) : Promise.reject('No location name'),
        enabled: enabled && !!locationName,
        refetchInterval: ANALYTICS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
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
        queryFn: () => locationId ? apiService.getAnalyticsById(locationId, hoursBack) : Promise.reject('No location ID'),
        enabled: enabled && !!locationId,
        refetchInterval: ANALYTICS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: RETRY_COUNT,
        retryDelay,
    });
}

/**
 * Hook to get prediction task status
 */
export function usePredictionStatus(): UseQueryResult<PredictionStatusData, Error> {
    return useQuery({
        queryKey: queryKeys.predictionStatus,
        queryFn: apiService.getPredictionStatus,
        refetchInterval: PREDICTION_STATUS_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: STALE_TIME,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(RETRY_DELAY_BASE * 2 ** attemptIndex, 30000),
    });
}

/**
 * Hook to generate new predictions for a location (mutation)
 */
export function useGeneratePredictions() {
    return {
        generateByName: apiService.generatePredictionsByName,
        generateById: apiService.generatePredictionsById,
        triggerGlobal: apiService.triggerGlobalPredictions,
    };
}