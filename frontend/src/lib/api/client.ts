import {
    RealTimeConditions,
    ComprehensiveUpdate,
    LocationsResponse,
    LocationTimeline,
    LocationHistory,
    ApiStatus,
    ApiLocation,
    mapApiRiskToFrontend
} from './types';
import type { FloodLocation } from '@/types';

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Generic API request helper with error handling
async function apiRequest<T>(endpoint: string): Promise<T> {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`API request error for ${endpoint}:`, error);
        throw error;
    }
}

// API Service Functions
export const apiService = {
    /**
     * Get API status and basic info
     */
    getApiStatus: (): Promise<ApiStatus> => {
        return apiRequest<ApiStatus>('/');
    },

    /**
     * Get comprehensive system update with all locations and alerts
     */
    getSystemUpdate: (): Promise<ComprehensiveUpdate> => {
        return apiRequest<ComprehensiveUpdate>('/api/system-update');
    },

    /**
     * Get real-time conditions for a specific location
     */
    getRealTimeConditions: (location: string): Promise<RealTimeConditions> => {
        const encodedLocation = encodeURIComponent(location);
        return apiRequest<RealTimeConditions>(`/api/real-time/${encodedLocation}`);
    },

    /**
     * Get all available locations with current status
     */
    getLocations: (): Promise<LocationsResponse> => {
        return apiRequest<LocationsResponse>('/api/locations');
    },

    /**
     * Get timeline data for a specific location
     */
    getLocationTimeline: (location: string, minutes: number = 5): Promise<LocationTimeline> => {
        const encodedLocation = encodeURIComponent(location);
        return apiRequest<LocationTimeline>(`/api/timeline/${encodedLocation}?minutes=${minutes}`);
    },

    /**
     * Get historical data for sparkline visualization
     * @param location - Location name
     * @param points - Number of historical points to fetch (default: 20, max: 100)
     */
    getLocationHistory: (location: string, points: number = 20): Promise<LocationHistory> => {
        const encodedLocation = encodeURIComponent(location);
        return apiRequest<LocationHistory>(`/api/history/${encodedLocation}?points=${points}`);
    },
};

// Helper functions for data transformation
export const dataTransformers = {
    /**
     * Convert API locations to FloodLocation format for compatibility
     */
    apiLocationsToFloodLocations: (apiLocations: ApiLocation[]): FloodLocation[] => {
        return apiLocations.map(location => ({
            name: location.name,
            lat: location.latitude,
            lng: location.longitude,
            riskLevel: mapApiRiskToFrontend(location.current_risk),
            // Additional fields for enhanced functionality
            sensor_id: location.sensor_id,
            has_data: location.has_data,
            api_risk_level: location.current_risk,
        }));
    },

    /**
     * Get risk level color for UI display
     */
    getRiskLevelColor: (riskLevel: string): string => {
        switch (riskLevel.toLowerCase()) {
            case 'safe':
                return '#22c55e'; // Green (safe)
            case 'low':
                return '#84cc16'; // Lime (low-risk)
            case 'elevated':
            case 'medium':
            case 'moderate':
                return '#eab308'; // Yellow (moderate)
            case 'high':
                return '#f97316'; // Orange (high-risk)
            case 'critical':
                return '#ef4444'; // Red (critical)
            default:
                return '#6B7280'; // Gray
        }
    },

    /**
     * Get alert urgency styling
     */
    getAlertStyling: (level: string) => {
        switch (level.toLowerCase()) {
            case 'critical':
                return {
                    bgColor: 'bg-critical/10',
                    textColor: 'text-critical',
                    borderColor: 'border-critical/30',
                    icon: '🔴'
                };
            case 'high':
                return {
                    bgColor: 'bg-high-risk/10',
                    textColor: 'text-high-risk',
                    borderColor: 'border-high-risk/30',
                    icon: '🟠'
                };
            case 'medium':
            case 'moderate':
                return {
                    bgColor: 'bg-moderate/10',
                    textColor: 'text-moderate',
                    borderColor: 'border-moderate/30',
                    icon: '🟡'
                };
            case 'low':
                return {
                    bgColor: 'bg-low-risk/10',
                    textColor: 'text-low-risk',
                    borderColor: 'border-low-risk/30',
                    icon: '�'
                };
            case 'safe':
                return {
                    bgColor: 'bg-safe/10',
                    textColor: 'text-safe',
                    borderColor: 'border-safe/30',
                    icon: '�'
                };
            default:
                return {
                    bgColor: 'bg-gray-100',
                    textColor: 'text-gray-800',
                    borderColor: 'border-gray-300',
                    icon: '⚫'
                };
        }
    },

    /**
     * Format timestamp for display
     */
    formatTimestamp: (timestamp: string): string => {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
            });
        } catch {
            return 'Invalid time';
        }
    },

    /**
     * Format relative time (e.g., "2 minutes ago")
     */
    formatRelativeTime: (timestamp: string): string => {
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            const diffMinutes = Math.floor(diffMs / (1000 * 60));

            if (diffMinutes < 1) {
                return 'Just now';
            } else if (diffMinutes < 60) {
                return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
            } else {
                const diffHours = Math.floor(diffMinutes / 60);
                return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
            }
        } catch {
            return 'Unknown time';
        }
    },
};

// Error handling utilities
export class ApiError extends Error {
    constructor(
        message: string,
        public status?: number,
        public endpoint?: string
    ) {
        super(message);
        this.name = 'ApiError';
    }
}