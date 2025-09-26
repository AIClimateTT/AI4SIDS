// src/components/app/map.tsx
import { useRef, useEffect, useImperativeHandle, forwardRef, useCallback } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import { useSystemUpdate } from '@/lib/hooks/useApiData';
import { getRiskColor } from '@/lib/utils/mapUtils';
import type { LocationSummary } from '@/lib/api/types';


export interface MapComponentRef {
  flyToLocation: (location: LocationSummary) => void;
  highlightLocation: (location: LocationSummary) => void;
}

interface MapComponentProps {
  selectedLocation: LocationSummary | null;
}

// Helper component to handle map control using useMap hook
function MapController({ selectedLocation, onMapReady }: {
  selectedLocation: LocationSummary | null;
  onMapReady: (map: L.Map) => void;
}) {
  const map = useMap();

  useEffect(() => {
    onMapReady(map);
  }, [map, onMapReady]);

  useEffect(() => {
    if (selectedLocation && map) {
      map.flyTo([selectedLocation.latitude, selectedLocation.longitude], 12, {
        duration: 1.0
      });
    }
  }, [selectedLocation, map]);

  return null;
}

// Individual marker component for better React patterns
function FloodMarker({
  location,
  isSelected,
  onMarkerReady
}: {
  location: LocationSummary;
  isSelected: boolean;
  onMarkerReady: (location: LocationSummary, marker: L.CircleMarker) => void;
}) {
  const markerRef = useRef<L.CircleMarker>(null);

  useEffect(() => {
    if (markerRef.current) {
      onMarkerReady(location, markerRef.current);
    }
  }, [location, onMarkerReady]);

  useEffect(() => {
    if (markerRef.current) {
      if (isSelected) {
        markerRef.current.setRadius(15);
        markerRef.current.setStyle({ weight: 4 });
        setTimeout(() => {
          markerRef.current?.openPopup();
        }, 1500);
      } else {
        markerRef.current.setRadius(10);
        markerRef.current.setStyle({ weight: 2 });
      }
    }
  }, [isSelected]);

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
    <CircleMarker
      ref={markerRef}
      center={[location.latitude, location.longitude]}
      radius={isSelected ? 15 : 10}
      pathOptions={{
        color: getRiskColor(mapApiRiskToFrontend(location.flood_risk)),
        fillColor: getRiskColor(mapApiRiskToFrontend(location.flood_risk)),
        fillOpacity: 0.7,
        weight: isSelected ? 4 : 2
      }}
    >
      <Popup>
        <div className="min-w-[200px]">
          <div className="font-bold text-lg mb-2">{location.name}</div>

          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>Flood Risk:</span>
              <span style={{
                color: getRiskColor(mapApiRiskToFrontend(location.flood_risk)),
                fontWeight: 'bold'
              }}>
                {location.flood_risk}
              </span>
            </div>

            <div className="flex justify-between">
              <span>Coordinates:</span>
              <span className="text-gray-600">{location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}</span>
            </div>

            <div className="flex justify-between">
              <span>Sensor ID:</span>
              <span className="text-gray-600">{location.sensor_id}</span>
            </div>

            <div className="flex justify-between">
              <span>River Level:</span>
              <span className="text-blue-600 font-medium">{location.river_level.toFixed(2)}m</span>
            </div>

            <div className="flex justify-between">
              <span>Change Rate:</span>
              <span className={location.change_rate > 0 ? 'text-red-600' : location.change_rate < 0 ? 'text-green-600' : 'text-gray-600'}>
                {location.change_rate > 0 ? '+' : ''}{location.change_rate.toFixed(3)}m/15min
              </span>
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              Click location in sidebar for detailed conditions
            </div>
          </div>
        </div>
      </Popup>
    </CircleMarker>
  );
}

const MapComponent = forwardRef<MapComponentRef, MapComponentProps>(({ selectedLocation }, ref) => {
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<{ [key: string]: L.CircleMarker }>({});

  // Get live locations from system update
  const { data: systemUpdate, isLoading: locationsLoading, error: locationsError } = useSystemUpdate();
  const locations = systemUpdate?.locations || [];

  // Ensure we're in the browser environment
  if (typeof window === 'undefined') {
    return null;
  }

  const handleMapReady = useCallback((map: L.Map) => {
    mapRef.current = map;

    // Force lower z-index after map creation
    const container = map.getContainer();
    if (container) {
      container.style.zIndex = '1';
    }
  }, []);

  const handleMarkerReady = useCallback((location: LocationSummary, marker: L.CircleMarker) => {
    markersRef.current[location.name] = marker;
  }, []);

  useImperativeHandle(ref, () => ({
    flyToLocation: (location: LocationSummary) => {
      if (mapRef.current) {
        mapRef.current.flyTo([location.latitude, location.longitude], 12, {
          duration: 1.0
        });
      }
    },
    highlightLocation: (location: LocationSummary) => {
      // Reset all markers to normal state
      Object.values(markersRef.current).forEach(marker => {
        marker.setRadius(10);
        marker.setStyle({ weight: 2 });
      });

      // Highlight selected marker
      const selectedMarker = markersRef.current[location.name];
      if (selectedMarker) {
        selectedMarker.setRadius(15);
        selectedMarker.setStyle({ weight: 4 });
        selectedMarker.openPopup();
      }
    }
  }));  // Loading state
  if (locationsLoading) {
    return (
      <div className="w-full h-full bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading map data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (locationsError) {
    return (
      <div className="w-full h-full bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-2xl mb-2">⚠️</div>
          <p className="text-red-600 font-medium">Failed to load map data</p>
          <p className="text-gray-600 text-sm mt-1">Please check API connection</p>
        </div>
      </div>
    );
  }

  // Use API data or fallback to empty array
  const displayLocations = locations;

  return (
    <MapContainer
      center={[10.6918, -61.2225]}
      zoom={9}
      zoomControl={true}
      style={{ width: '100%', height: '100%', zIndex: 1 }}
    >
      <TileLayer
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        maxZoom={19}
        attribution='© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />

      <MapController
        selectedLocation={selectedLocation}
        onMapReady={handleMapReady}
      />

      {displayLocations.map((location: LocationSummary) => (
        <FloodMarker
          key={location.name}
          location={location}
          isSelected={selectedLocation?.name === location.name}
          onMarkerReady={handleMarkerReady}
        />
      ))}
    </MapContainer>
  );
});

MapComponent.displayName = 'MapComponent';

export default MapComponent;