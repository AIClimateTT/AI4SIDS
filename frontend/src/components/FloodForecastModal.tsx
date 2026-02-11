import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Badge } from './ui/badge';

import { Download, X } from 'lucide-react';




// --- INTERFACE DEFINITIONS (Aligned with weekforecast.py Pydantic) ---
interface ForecastDay {
  date: string; // ISO string from datetime
  label: string;
  rainfall_mm: number;
  risk: "SAFE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | string;
  confidence: number;
}

interface ForecastResponse {
  location: string;
  generated_at: string; // ISO string from datetime
  baseline: { [key: string]: any };
  forecast: ForecastDay[];
}

interface ForecastSummary {
    average_rainfall_mm: number;
    highest_risk: "SAFE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | string;
}

// --- HELPER FUNCTION TO CALCULATE SUMMARY (since the API no longer provides it) ---
const calculateSummary = (forecast: ForecastDay[]): ForecastSummary => {
  if (!forecast || forecast.length === 0) {
    return { average_rainfall_mm: 0, highest_risk: "SAFE" };
  }

  // Define risk hierarchy for finding the highest risk
  const riskOrder = { "SAFE": 0, "LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4 };

  const totalRainfall = forecast.reduce((sum, day) => sum + day.rainfall_mm, 0);
  const average_rainfall_mm = totalRainfall / forecast.length;

  let highest_risk = "SAFE";
  for (const day of forecast) {
    if (riskOrder[day.risk] > riskOrder[highest_risk]) {
      highest_risk = day.risk;
    }
  }

  return {
    average_rainfall_mm: parseFloat(average_rainfall_mm.toFixed(2)),
    highest_risk: highest_risk,
  };
};


// --- MOCK API RESPONSE DATA (Aligned with new Pydantic structure) ---
const generatedAt = new Date().toISOString();
const today = new Date();
const oneDayInMs = 86400000;

const mockForecastData: ForecastResponse = {
  location: "Caroni Station",
  generated_at: generatedAt,
  baseline: { base_daily_mm: 40.0, base_conf: 0.9, sentiment: 0.1 },
  forecast: [
    { date: new Date(today.getTime() + 0 * oneDayInMs).toISOString(), label: "Today", rainfall_mm: 15, risk: "LOW", confidence: 0.95 },
    { date: new Date(today.getTime() + 1 * oneDayInMs).toISOString(), label: "Tomorrow", rainfall_mm: 46, risk: "HIGH", confidence: 0.88 },
    { date: new Date(today.getTime() + 2 * oneDayInMs).toISOString(), label: today.toLocaleString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).split(' ').join(' '), rainfall_mm: 65, risk: "CRITICAL", confidence: 0.92 },
    { date: new Date(today.getTime() + 3 * oneDayInMs).toISOString(), label: new Date(today.getTime() + 3 * oneDayInMs).toLocaleString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).split(' ').join(' '), rainfall_mm: 30, risk: "MODERATE", confidence: 0.80 },
    { date: new Date(today.getTime() + 4 * oneDayInMs).toISOString(), label: new Date(today.getTime() + 4 * oneDayInMs).toLocaleString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).split(' ').join(' '), rainfall_mm: 10, risk: "SAFE", confidence: 0.98 },
    { date: new Date(today.getTime() + 5 * oneDayInMs).toISOString(), label: new Date(today.getTime() + 5 * oneDayInMs).toLocaleString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).split(' ').join(' '), rainfall_mm: 21, risk: "LOW", confidence: 0.90 },
    { date: new Date(today.getTime() + 6 * oneDayInMs).toISOString(), label: new Date(today.getTime() + 6 * oneDayInMs).toLocaleString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).split(' ').join(' '), rainfall_mm: 5, risk: "SAFE", confidence: 0.85 },
  ],
};


// --- HELPER FUNCTION FOR STYLING ---
const getRiskClass = (risk: ForecastDay['risk']) => {
  switch (risk) {
    case "SAFE":
      return "bg-green-500 hover:bg-green-500/80";
    case "LOW":
      return "bg-blue-500 hover:bg-blue-500/80";
    case "MODERATE":
      return "bg-yellow-500 hover:bg-yellow-500/80";
    case "HIGH":
      return "bg-red-500 hover:bg-red-500/80";
    case "CRITICAL":
      return "bg-rose-900 hover:bg-rose-900/80";
    default:
      return "bg-gray-500";
  }
};

// --- FloodForecastModal Component Definition ---

interface FloodForecastModalProps {
  location: string;
  open: boolean;
  onClose: () => void;
}

export const FloodForecastModal: React.FC<FloodForecastModalProps> = ({ location, open, onClose }) => {
  // Now uses ForecastResponse type
  const [data, setData] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use the location from props or fall back to mock data's location
  const displayLocation = data?.location || location;
  
  // Custom hook to handle escape key press for closing modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (open) {
      document.addEventListener('keydown', handleEscape);
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open, onClose]);


  useEffect(() => {
    if (open) {
      setLoading(true);
      setError(null);
      setData(null); // Clear previous data

      // Simulate API call delay
      setTimeout(() => {
        // Adjust the mock data location to match the requested location for better UX
        const adjustedData = { ...mockForecastData, location: displayLocation };
        // The mock data now conforms to ForecastResponse without summary
        setData(adjustedData);
        setLoading(false);
      }, 800);
    }
  }, [open, displayLocation]);

  if (!open) return null;

  // Simple backdrop click handler
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };
  
  // Dynamically calculate summary here for display
  const summary = data ? calculateSummary(data.forecast) : null;

  return (
    // Modal Overlay
    <div 
      className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick} // Close on backdrop click
    >
      <Card className="w-full max-w-xl relative">
        
        {/* Card Header (for Title, Location, and Controls) */}
        <CardHeader className="flex flex-row items-start justify-between">
          <div>
            <CardTitle>Flood Forecast</CardTitle>
            <CardDescription className="text-lg font-semibold text-blue-600 mt-1">
              {displayLocation}
            </CardDescription>
          </div>
          <div className="flex gap-2 items-center">
             <Button variant="outline" size="sm">
               <Download className="h-4 w-4 mr-2" />
               Export
             </Button>
             <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close modal">
               <X className="h-4 w-4" />
             </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          {loading && <p className="text-center py-8 text-gray-500">Loading forecast data...</p>}
          {error && <p className="text-center py-8 text-red-600">Error: {error}</p>}

          {data && summary && (
            <>
              <p className="text-sm text-gray-500 mb-4">
                Generated: {new Date(data.generated_at).toLocaleString()}
              </p>

              {/* Forecast Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {data.forecast.map((day, i) => (
                  <div key={i} className="p-4 bg-gray-50 border rounded-lg text-center shadow-sm transition-all hover:shadow-md">
                    <h3 className="font-semibold text-lg text-gray-900 mb-1">{day.label}</h3>
                    <p className="text-sm text-gray-600 font-mono">
                      {day.rainfall_mm.toFixed(0)} mm {/* Rainfall is int in python, so no need for fixed(1) */}
                    </p>
                    {/* Risk Badge */}
                    <Badge 
                      className={`mt-2 font-bold px-3 py-1 text-white text-sm justify-center ${getRiskClass(day.risk)}`}
                    >
                      {day.risk}
                    </Badge>
                    <p className="text-xs text-gray-500 mt-1">
                      {Math.round(day.confidence * 100)}% confidence
                    </p>
                  </div>
                ))}
              </div>

              {/* Summary Section (calculated client-side) */}
              <div className="mt-6 p-4 border rounded-lg bg-blue-50/50 text-sm text-gray-900 border-blue-200">
                <p>
                  <strong className="font-semibold">Average Forecast Rainfall:</strong> {summary.average_rainfall_mm.toFixed(1)} mm
                </p>
                <p className="mt-1">
                  <strong className="font-semibold">Highest Predicted Risk:</strong>{" "}
                  <Badge 
                    className={`font-bold text-white ${getRiskClass(summary.highest_risk)}`}
                  >
                    {summary.highest_risk}
                  </Badge>
                </p>
                {/* Display baseline information */}
                {data.baseline && (
                   <p className="mt-3 text-xs text-gray-600 italic">
                       (Baseline: {data.baseline.base_daily_mm}mm base rainfall, {data.baseline.base_conf} base confidence)
                   </p>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default FloodForecastModal;
// --- Demo App for Component Testing ---
// This is an export default so the file is runnable on its own.
// const App = () => {
//     const [isOpen, setIsOpen] = useState(false);
//     const [currentLocation, setCurrentLocation] = useState('Central River');

//     return (
//         <div className="p-8 min-h-screen bg-gray-100 flex flex-col items-center">
//             <h1 className="text-3xl font-bold mb-8 text-gray-800">Modal Demo</h1>
//             <p className="text-gray-600 mb-4">Current Location: <span className="font-semibold text-blue-600">{currentLocation}</span></p>
            
//             <Button onClick={() => setIsOpen(true)}>
//                 Open Forecast Modal
//             </Button>
            
//             {/* The FloodForecastModal Component */}
//             <FloodForecastModal
//                 open={isOpen}
//                 location={currentLocation}
//                 onClose={() => setIsOpen(false)}
//             />

//             {/* Mock Station Cards (Optional, for context) */}
//             <div className="mt-8 space-y-4 max-w-md w-full">
//                 <Card>
//                     <CardContent className="p-4 flex justify-between items-center">
//                         <span className="font-medium">Caroni Station</span>
//                         <Button size="sm" onClick={() => { setCurrentLocation('Caroni Station'); setIsOpen(true); }}>View</Button>
//                     </CardContent>
//                 </Card>
//                 <Card>
//                     <CardContent className="p-4 flex justify-between items-center">
//                         <span className="font-medium">Ortoire River Delta</span>
//                         <Button size="sm" onClick={() => { setCurrentLocation('Ortoire River Delta'); setIsOpen(true); }}>View</Button>
//                     </CardContent>
//                 </Card>
//             </div>
//         </div>
//     );
// }

// export default App;
