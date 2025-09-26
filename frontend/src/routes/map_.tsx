import { createFileRoute, ClientOnly } from '@tanstack/react-router'
import { useRef, useState, lazy, Suspense } from "react";

import type { MapComponentRef } from "@/components/map";
import type { LocationSummary } from "@/lib/api/types";

import ChatInterface from "@/components/chat-interface";
import EnhancedSidebar from "@/components/enhanced-sidebar";
import { LocationDetailSheet } from "@/components/location-detail-sheet";
// import { ClientOnly } from "@/components/ClientOnly";

// Dynamically import the map component to avoid SSR issues with Leaflet
const MapComponent = lazy(() => import("@/components/map"));

export const Route = createFileRoute('/map_')({
  component: RouteComponent,
})

function RouteComponent() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<LocationSummary | null>(null);
  const [isDetailSheetOpen, setIsDetailSheetOpen] = useState(false);
  const mapRef = useRef<MapComponentRef>(null);

  const handleLocationSelect = (location: LocationSummary) => {
    setSelectedLocation(location);
    setIsDetailSheetOpen(true);
  };

  const handleCloseDetailSheet = () => {
    setIsDetailSheetOpen(false);
  };

  return (
    <div className="h-screen flex flex-col">

      <div className="flex-1 flex min-h-0">
        {/* Enhanced Sidebar */}
        <EnhancedSidebar
          onLocationSelect={handleLocationSelect}
          selectedLocation={selectedLocation}
        />

        {/* Map and Chat Container */}
        <div className="flex-1 relative">
          {/* Map with explicit lower z-index */}
          <div
            className="absolute inset-0"
            style={{ zIndex: 1 }}
          >
            <ClientOnly fallback={
              <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                <div className="text-gray-600">Loading map...</div>
              </div>
            }>
              <Suspense fallback={
                <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                  <div className="text-gray-600">Loading map...</div>
                </div>
              }>
                <MapComponent
                  ref={mapRef}
                  selectedLocation={selectedLocation}
                />
              </Suspense>
            </ClientOnly>
          </div>

          {/* Chat with much higher z-index */}
          <div
            className="absolute top-4 right-4"
            style={{ zIndex: 1000 }}
          >
            <ChatInterface
              isExpanded={isExpanded}
              onToggleExpand={() => setIsExpanded(!isExpanded)}
              selectedLocation={selectedLocation}
            />
          </div>
        </div>
      </div>

      {/* Location Detail Sheet */}
      <LocationDetailSheet
        location={selectedLocation}
        isOpen={isDetailSheetOpen}
        onClose={handleCloseDetailSheet}
      />
    </div>
  );
}
