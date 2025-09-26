import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService, dataTransformers } from '../api/client';
import type {
    ComprehensiveUpdate,
    RealTimeConditions,
    LocationsResponse,
    LocationTimeline,
    ApiStatus
} from '../api/types';
import type { FloodLocation } from '@/types';

// Query keys for consistent caching
export const queryKeys = {
    systemUpdate: ['system-update'] as const,
    locations: ['locations'] as const,
    realTime: (location: string) => ['real-time', location] as const,
    timeline: (location: string, minutes: number) => ['timeline', location, minutes] as const,
    apiStatus: ['api-status'] as const,
} as const;

// Configuration constants
const REAL_TIME_REFETCH_INTERVAL = 15 * 1000; // 15 seconds to match API cycle
const SYSTEM_UPDATE_REFETCH_INTERVAL = 15 * 1000; // 15 seconds
const LOCATIONS_REFETCH_INTERVAL = 60 * 1000; // 1 minute (locations change less frequently)

/**
 * Hook to get comprehensive system update with auto-refresh
 */
export function useSystemUpdate(): UseQueryResult<ComprehensiveUpdate, Error> {
    return useQuery({
        queryKey: queryKeys.systemUpdate,
        queryFn: apiService.getSystemUpdate,
        refetchInterval: SYSTEM_UPDATE_REFETCH_INTERVAL,
        refetchIntervalInBackground: true,
        staleTime: 10 * 1000, // Consider data stale after 10 seconds
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
        staleTime: 30 * 1000, // Consider data stale after 30 seconds
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
        staleTime: 30 * 1000,
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
        staleTime: 10 * 1000,
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
        staleTime: 10 * 1000,
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
        refetchInterval: 30 * 1000, // Check API status every 30 seconds
        refetchIntervalInBackground: true,
        staleTime: 20 * 1000,
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