// src/components/app/side-bar-2.tsx
import React from 'react';
import type { SidebarProps } from '@/types';
import { floodLocations } from '@/data/floodLocations';
import { getRiskColor } from '@/lib/utils/mapUtils';

// Risk level icons
const getRiskIcon = (riskLevel: string) => {
  switch (riskLevel) {
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

const Sidebar: React.FC<SidebarProps> = ({ onLocationSelect, selectedLocation }) => {
  return (
    <div className="w-80 bg-white border-r border-gray-300 shadow-lg h-full overflow-y-auto flex flex-col">
      {/* Header */}
      <div className="bg-blue-600 text-white px-4 py-3 flex-shrink-0">
        <h2 className="text-lg font-semibold">Flood Risk Locations</h2>
        <p className="text-sm text-blue-100">Click a location to view on map</p>
      </div>

      {/* Location List */}
      <div className="flex-1 p-4 space-y-2 overflow-y-auto">
        {floodLocations.map((location) => (
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
                <span className="text-xl">{getRiskIcon(location.riskLevel)}</span>

                {/* Location Info */}
                <div>
                  <h3 className="font-medium text-gray-900">{location.name}</h3>
                  <p className="text-sm text-gray-600">
                    {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                  </p>
                </div>
              </div>

              {/* Risk Level Badge */}
              <div className="text-right">
                <span
                  className="inline-block px-2 py-1 text-xs font-semibold rounded-full text-white"
                  style={{ backgroundColor: getRiskColor(location.riskLevel) }}
                >
                  {location.riskLevel.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Risk Description */}
            <div className="mt-2 text-sm text-gray-600">
              {getRiskDescription(location.riskLevel)}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="border-t border-gray-200 p-4 flex-shrink-0">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Risk Levels</h3>
        <div className="space-y-1 text-sm">
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
        </div>
      </div>
    </div>
  );
};

// Helper function for risk descriptions
const getRiskDescription = (riskLevel: string): string => {
  switch (riskLevel) {
    case 'low':
      return 'Generally safe from flooding with good drainage systems.';
    case 'medium':
      return 'Some flood risk during heavy rainfall periods.';
    case 'high':
      return 'Frequent flooding issues, especially during rainy season.';
    case 'critical':
      return 'Severe flood risk with regular water accumulation.';
    default:
      return 'Risk level assessment pending.';
  }
};

export default Sidebar;