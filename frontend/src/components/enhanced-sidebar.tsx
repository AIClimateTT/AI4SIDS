// src/components/app/enhanced-sidebar.tsx
import React, { useState } from 'react';
import type { SidebarProps } from '@/types';
import {
    useSystemUpdate,
    useSystemStatus,
    useSystemAlerts,
    useDataFreshness
} from '@/lib/hooks/useApiData';
import { dataTransformers } from '@/lib/api/client';
import { getRiskColor } from '@/lib/utils/mapUtils';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { LocationSummary } from '@/lib/api/types';

// Risk level icons
const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
        case 'low':
            return '🟢'; // Green circle
        case 'medium':
            return '🟡'; // Yellow circle
        case 'high':
            return '🟠'; // Orange circle
        case 'critical':
            return '🔴'; // Red circle
        default:
            return '⚫'; // Black circle
    }
};

// Enhanced sidebar component with API integration
const EnhancedSidebar: React.FC<SidebarProps> = ({ onLocationSelect, selectedLocation }) => {
    const [showSystemStatus, setShowSystemStatus] = useState(true);
    const [showAlerts, setShowAlerts] = useState(true);

    // API data hooks - using system update for locations
    const { data: systemUpdate, isLoading: systemLoading, error: systemError } = useSystemUpdate();
    const {
        isLoading: statusLoading,
        activeSensors,
        dataCycleProgress,
        nextUpdateSeconds,
        totalAlerts
    } = useSystemStatus();
    const { alerts, hasAlerts, criticalAlerts, highAlerts } = useSystemAlerts();
    const { systemUpdateFreshness } = useDataFreshness();

    // Extract locations from system update
    const locations = systemUpdate?.locations || [];
    const isLoading = systemLoading;
    const error = systemError;

    // Loading state
    if (systemLoading) {
        return (
            <div className="w-80 bg-white border-r border-gray-300 shadow-lg h-full flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                    <p className="text-gray-600">Loading system data...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (systemError) {
        return (
            <div className="w-80 bg-white border-r border-gray-300 shadow-lg h-full flex items-center justify-center">
                <div className="text-center p-4">
                    <div className="text-red-500 text-2xl mb-2">⚠️</div>
                    <p className="text-red-600 font-medium">Failed to load system data</p>
                    <p className="text-gray-600 text-sm mt-1">Please check API connection</p>
                </div>
            </div>
        );
    }

    // Helper function to get risk level priority for sorting
    const getRiskPriority = (riskLevel: string): number => {
        switch (riskLevel.toUpperCase()) {
            case 'CRITICAL': return 5;
            case 'HIGH': return 4;
            case 'ELEVATED': return 3;
            case 'MEDIUM': return 2;
            case 'LOW': return 1;
            default: return 0;
        }
    };

    // Sort locations by risk level (highest risk first)
    const displayLocations = (locations || []).sort((a, b) => {
        const priorityA = getRiskPriority(a.flood_risk);
        const priorityB = getRiskPriority(b.flood_risk);

        // Sort by risk priority first (descending), then by name (ascending) for consistent ordering
        if (priorityA !== priorityB) {
            return priorityB - priorityA;
        }
        return a.name.localeCompare(b.name);
    });

    const urgentAlerts = [...criticalAlerts, ...highAlerts];

    // Helper function to convert API risk level to frontend format
    const mapApiRiskToFrontend = (apiRisk: string) => {
        switch (apiRisk) {
            case 'LOW': return 'low';
            case 'ELEVATED':
            case 'MEDIUM': return 'medium';
            case 'HIGH': return 'high';
            case 'CRITICAL': return 'critical';
            default: return 'low';
        }
    };

    return (
        <div className="w-80 bg-white border-r border-gray-300 shadow-lg h-full overflow-y-auto flex flex-col">
            {/* Header */}
            <div className="bg-blue-600 text-white px-4 py-3 flex-shrink-0">
                <h2 className="text-lg font-semibold">AI4SIDS Monitor</h2>
                <p className="text-sm text-blue-100">Real-time flood risk monitoring</p>
                <div className="text-xs text-blue-200 mt-1">
                    Last update: {systemUpdateFreshness}
                </div>
            </div>

            {/* System Status Section */}
            {showSystemStatus && (
                <div className="p-4 border-b border-gray-200 flex-shrink-0">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-semibold text-gray-700">System Status</h3>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowSystemStatus(false)}
                            className="h-6 w-6 p-0"
                        >
                            ×
                        </Button>
                    </div>

                    <Card className="border border-gray-200">
                        <CardContent className="p-3">
                            <div className="grid grid-cols-2 gap-2 text-xs">
                                <div className="text-center">
                                    <div className="font-medium text-blue-600">{activeSensors}</div>
                                    <div className="text-gray-600">Active Sensors</div>
                                </div>
                                <div className="text-center">
                                    <div className="font-medium text-green-600">{dataCycleProgress}</div>
                                    <div className="text-gray-600">Data Cycle</div>
                                </div>
                                <div className="text-center">
                                    <div className="font-medium text-orange-600">{totalAlerts}</div>
                                    <div className="text-gray-600">Total Alerts</div>
                                </div>
                                <div className="text-center">
                                    <div className="font-medium text-purple-600">{nextUpdateSeconds}s</div>
                                    <div className="text-gray-600">Next Update</div>
                                </div>
                            </div>

                            {statusLoading && (
                                <div className="mt-2 flex items-center justify-center">
                                    <div className="animate-pulse text-xs text-gray-500">Updating...</div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Alerts Section */}
            {showAlerts && hasAlerts && (
                <div className="p-4 border-b border-gray-200 flex-shrink-0">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-semibold text-gray-700">
                            System Alerts {urgentAlerts.length > 0 && (
                                <span className="inline-flex items-center justify-center w-5 h-5 text-xs bg-red-500 text-white rounded-full ml-1">
                                    {urgentAlerts.length}
                                </span>
                            )}
                        </h3>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowAlerts(false)}
                            className="h-6 w-6 p-0"
                        >
                            ×
                        </Button>
                    </div>

                    <div className="space-y-2 max-h-32 overflow-y-auto">
                        {alerts.slice(0, 3).map((alert, index) => {
                            const styling = dataTransformers.getAlertStyling(alert.level);
                            return (
                                <div
                                    key={index}
                                    className={`p-2 rounded-md border text-xs ${styling.bgColor} ${styling.textColor} ${styling.borderColor}`}
                                >
                                    <div className="flex items-start space-x-2">
                                        <span className="text-sm">{styling.icon}</span>
                                        <div className="flex-1">
                                            <div className="font-medium">{alert.location}</div>
                                            <div className="text-xs opacity-75">{alert.message}</div>
                                            <div className="text-xs opacity-60 mt-1">
                                                {dataTransformers.formatRelativeTime(alert.timestamp)}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                        {alerts.length > 3 && (
                            <div className="text-xs text-gray-500 text-center">
                                +{alerts.length - 3} more alerts
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Location List */}
            <div className="flex-1 p-4 space-y-2 overflow-y-auto">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-gray-700">Monitored Locations</h3>
                    <div className="text-xs text-gray-500">
                        {displayLocations.length} location{displayLocations.length !== 1 ? 's' : ''}
                    </div>
                </div>

                {displayLocations.map((location: LocationSummary) => (
                    <div
                        key={location.name}
                        onClick={() => onLocationSelect(location)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md ${selectedLocation?.name === location.name
                            ? 'border-blue-500 bg-blue-50 shadow-md'
                            : 'border-gray-200 hover:border-gray-300'
                            }`}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                {/* Risk Icon */}
                                <span className="text-xl">{getRiskIcon(mapApiRiskToFrontend(location.flood_risk))}</span>

                                {/* Location Info */}
                                <div>
                                    <h3 className="font-medium text-gray-900">{location.name}</h3>
                                    <p className="text-sm text-gray-600">
                                        {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
                                    </p>
                                    <p className="text-xs text-gray-500">ID: {location.sensor_id}</p>
                                </div>
                            </div>

                            {/* Risk Level Badge */}
                            <div className="text-right">
                                <span
                                    className="inline-block px-2 py-1 text-xs font-semibold rounded-full text-white"
                                    style={{ backgroundColor: getRiskColor(mapApiRiskToFrontend(location.flood_risk)) }}
                                >
                                    {location.flood_risk}
                                </span>
                            </div>
                        </div>

                        {/* Enhanced Location Details */}
                        <div className="mt-2 space-y-1">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">River Level:</span>
                                <span className="font-medium">{location.river_level.toFixed(2)}m</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Change Rate:</span>
                                <span className={location.change_rate > 0 ? 'text-red-600' : location.change_rate < 0 ? 'text-green-600' : 'text-gray-600'}>
                                    {location.change_rate > 0 ? '+' : ''}{location.change_rate.toFixed(3)}m/15min
                                </span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-gray-500">Last Updated:</span>
                                <span className="text-gray-500">
                                    {dataTransformers.formatRelativeTime(location.last_updated)}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}                {displayLocations.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                        <div className="text-2xl mb-2">📍</div>
                        <p>No locations available</p>
                        <p className="text-xs mt-1">Check API connection</p>
                    </div>
                )}
            </div>

            {/* Footer with data freshness */}
            <div className="border-t border-gray-200 p-4 flex-shrink-0">
                {/* <h3 className="text-sm font-semibold text-gray-700 mb-2">Risk Levels</h3> */}
                {/* <div className="space-y-1 text-sm mb-3">
                    <div className="flex items-center space-x-2">
                        <span>🟢</span>
                        <span className="text-gray-600">Low - Minimal flood risk</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span>🟡</span>
                        <span className="text-gray-600">Medium - Moderate flood risk</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span>🟠</span>
                        <span className="text-gray-600">High - Significant flood risk</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span>🔴</span>
                        <span className="text-gray-600">Critical - Severe flood risk</span>
                    </div>
                </div> */}

                <div className="text-xs text-gray-500 border-t pt-2">
                    <div>System: {systemUpdateFreshness}</div>
                    <div>Data Cycle: {dataCycleProgress}</div>
                </div>
            </div>
        </div>
    );
};

export default EnhancedSidebar;