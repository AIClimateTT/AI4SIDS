import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, TrendingUp, TrendingDown, AlertTriangle, Clock, Target } from 'lucide-react';
import Chart from 'react-apexcharts';

interface AnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
  locationName: string;
}

interface AnalyticsData {
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

const AnalyticsModal: React.FC<AnalyticsModalProps> = ({ isOpen, onClose, locationName }) => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hoursBack, setHoursBack] = useState(24);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/analytics/by-name/${encodeURIComponent(locationName)}?hours_back=${hoursBack}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch analytics data: ${response.statusText}`);
      }
      
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics data');
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateNewPredictions = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/analytics/by-name/${encodeURIComponent(locationName)}/predictions`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to generate predictions: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('Predictions generated:', result);
      
      // Refresh analytics data to show new predictions
      fetchAnalyticsData();
    } catch (err) {
      console.error('Prediction generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate predictions');
    }
  };

  useEffect(() => {
    if (isOpen && locationName) {
      fetchAnalyticsData();
    }
  }, [isOpen, locationName, hoursBack]);

  const getChartOptions = () => {
    if (!analyticsData) return {};

    return {
      chart: {
        height: 400,
        type: 'line' as const,
        zoom: {
          enabled: true
        },
        toolbar: {
          show: true
        }
      },
      colors: ['#2563eb', '#dc2626', '#059669'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'smooth' as const,
        width: [3, 2, 2],
        dashArray: [0, 0, 5]
      },
      title: {
        text: `River Level Analytics - ${locationName}`,
        align: 'left' as const
      },
      grid: {
        borderColor: '#e5e7eb',
        strokeDashArray: 4,
      },
      markers: {
        size: [0, 4, 3],
      },
      xaxis: {
        type: 'datetime' as const,
        title: {
          text: 'Time'
        }
      },
      yaxis: {
        title: {
          text: 'River Level (meters)'
        },
        min: Math.max(0, Math.min(...analyticsData.historical_data.map(d => d.river_level_m)) - 0.5),
        max: Math.max(...analyticsData.historical_data.map(d => d.river_level_m), ...analyticsData.predictions.map(d => d.predicted_level_m)) + 0.5
      },
      tooltip: {
        shared: true,
        intersect: false,
        x: {
          format: 'MMM dd, HH:mm'
        }
      },
      legend: {
        position: 'top' as const,
        horizontalAlign: 'right' as const,
        floating: true,
        offsetY: -25,
        offsetX: -5
      },
      annotations: {
        yaxis: [
          {
            y: 3.0,
            borderColor: '#f59e0b',
            label: {
              borderColor: '#f59e0b',
              style: {
                color: '#fff',
                background: '#f59e0b',
              },
              text: 'Flood Threshold (3.0m)'
            }
          },
          {
            y: 4.2,
            borderColor: '#dc2626',
            label: {
              borderColor: '#dc2626',
              style: {
                color: '#fff',
                background: '#dc2626',
              },
              text: 'Critical Level (4.2m)'
            }
          }
        ]
      }
    };
  };

  const getChartSeries = () => {
    if (!analyticsData) return [];

    return [
      {
        name: 'Historical Data',
        data: analyticsData.historical_data.map(d => [
          new Date(d.timestamp).getTime(),
          d.river_level_m
        ])
      },
      {
        name: 'Predictions',
        data: analyticsData.predictions.map(d => [
          new Date(d.predicted_for_time).getTime(),
          d.predicted_level_m
        ])
      },
      {
        name: 'Confidence Bounds',
        data: analyticsData.predictions.map(d => [
          new Date(d.predicted_for_time).getTime(),
          d.predicted_level_m + (d.confidence_score * 0.1) // Simple confidence visualization
        ])
      }
    ];
  };

  const getRiskColor = (risk: string) => {
    switch (risk?.toUpperCase()) {
      case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'ELEVATED': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'LOW': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend?.toLowerCase()) {
      case 'rising': return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'falling': return <TrendingDown className="h-4 w-4 text-green-500" />;
      default: return <Clock className="h-4 w-4 text-blue-500" />;
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Analytics Dashboard - {locationName}
          </DialogTitle>
        </DialogHeader>

        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading analytics data...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex items-center">
              <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
              <span className="text-red-800">{error}</span>
            </div>
            <Button onClick={fetchAnalyticsData} className="mt-2" variant="outline">
              Retry
            </Button>
          </div>
        )}

        {analyticsData && (
          <div className="space-y-6">
            {/* Controls */}
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <label className="text-sm font-medium">Time Range:</label>
                <select
                  value={hoursBack}
                  onChange={(e) => setHoursBack(Number(e.target.value))}
                  className="px-3 py-1 border rounded-md text-sm"
                >
                  <option value={6}>Last 6 hours</option>
                  <option value={12}>Last 12 hours</option>
                  <option value={24}>Last 24 hours</option>
                  <option value={48}>Last 48 hours</option>
                  <option value={72}>Last 72 hours</option>
                </select>
              </div>
              <Button onClick={generateNewPredictions} size="sm" variant="outline">
                <Target className="h-4 w-4 mr-1" />
                Generate New Predictions
              </Button>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Current Level</span>
                    {getTrendIcon(analyticsData.summary_stats.trend)}
                  </div>
                  <div className="text-2xl font-bold">
                    {analyticsData.summary_stats.current_level.toFixed(2)}m
                  </div>
                  <Badge className={getRiskColor(analyticsData.historical_data[analyticsData.historical_data.length - 1]?.flood_risk || 'UNKNOWN')}>
                    {analyticsData.historical_data[analyticsData.historical_data.length - 1]?.flood_risk || 'UNKNOWN'}
                  </Badge>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <span className="text-sm text-gray-600">24h Range</span>
                  <div className="text-lg font-semibold">
                    {analyticsData.summary_stats.min_level.toFixed(2)} - {analyticsData.summary_stats.max_level.toFixed(2)}m
                  </div>
                  <span className="text-sm text-gray-500">Avg: {analyticsData.summary_stats.avg_level.toFixed(2)}m</span>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <span className="text-sm text-gray-600">Prediction Accuracy</span>
                  <div className="text-2xl font-bold text-green-600">
                    {analyticsData.accuracy_metrics.accuracy_percentage}%
                  </div>
                  <span className="text-sm text-gray-500">
                    {analyticsData.accuracy_metrics.accurate_predictions}/{analyticsData.accuracy_metrics.total_predictions} predictions
                  </span>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <span className="text-sm text-gray-600">Data Points</span>
                  <div className="text-lg font-semibold">
                    {analyticsData.data_counts.historical_points} historical
                  </div>
                  <span className="text-sm text-gray-500">
                    {analyticsData.data_counts.prediction_points} predictions
                  </span>
                </CardContent>
              </Card>
            </div>

            {/* Main Chart */}
            <Card>
              <CardHeader>
                <CardTitle>River Level Trends & Predictions</CardTitle>
              </CardHeader>
              <CardContent>
                <Chart
                  options={getChartOptions()}
                  series={getChartSeries()}
                  type="line"
                  height={400}
                />
              </CardContent>
            </Card>

            {/* Predictions Table */}
            {analyticsData.predictions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Upcoming Predictions (Next 30 minutes)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-2">Time</th>
                          <th className="text-left p-2">Predicted Level</th>
                          <th className="text-left p-2">Confidence</th>
                          <th className="text-left p-2">Weather Factor</th>
                          <th className="text-left p-2">Risk Level</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analyticsData.predictions.map((pred, index) => (
                          <tr key={index} className="border-b hover:bg-gray-50">
                            <td className="p-2">
                              {new Date(pred.predicted_for_time).toLocaleTimeString()}
                            </td>
                            <td className="p-2 font-mono">
                              {pred.predicted_level_m.toFixed(3)}m
                            </td>
                            <td className="p-2">
                              <div className="flex items-center gap-2">
                                <div className="w-12 bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-blue-600 h-2 rounded-full"
                                    style={{ width: `${pred.confidence_score * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-xs">
                                  {(pred.confidence_score * 100).toFixed(0)}%
                                </span>
                              </div>
                            </td>
                            <td className="p-2">
                              <span className={`text-xs px-2 py-1 rounded ${
                                pred.weather_influence > 0 ? 'bg-orange-100 text-orange-800' : 
                                pred.weather_influence < 0 ? 'bg-blue-100 text-blue-800' : 
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {pred.weather_influence > 0 ? '+' : ''}{pred.weather_influence.toFixed(3)}
                              </span>
                            </td>
                            <td className="p-2">
                              <Badge className={getRiskColor(pred.flood_risk)}>
                                {pred.flood_risk}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default AnalyticsModal;