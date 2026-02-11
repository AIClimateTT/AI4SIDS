// API Response Types based on FastAPI models
export interface LocationInfo {
    name: string;
    latitude: number;
    longitude: number;
    sensor_id: string;
    last_updated: string;
}

export interface RiverConditions {
    level: number;
    change_rate: number;
    trend: 'rising' | 'falling' | 'stable';
    flood_risk: 'SAFE' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
    sensor_id: string;
}

export interface WeatherConditions {
    rainfall_mm: number;
    temperature_c: number;
    humidity_percent: number;
    rainfall_rate_hourly: number;
}

export interface SocialActivity {
    post_count: number;
    sentiment_score: number;
    sentiment_level: 'Highly Negative' | 'Negative' | 'Neutral';
    recent_posts: string[];
    activity_level: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface LocationInsights {
    summary: string;
    recommendation: string;
    correlation: string;
}

export interface RealTimeConditions {
    location: string;
    timestamp: string;
    river_conditions: RiverConditions;
    weather: WeatherConditions;
    social_activity: SocialActivity;
    insights: LocationInsights;
}

export interface SystemStatus {
    active_sensors: number;
    data_cycle_progress: string;
    next_update_seconds: number;
    total_alerts: number;
}

export interface Alert {
    level: 'safe' | 'low' | 'moderate' | 'high' | 'critical';
    location: string;
    message: string;
    timestamp: string;
    river_level?: number;
    change_rate?: number;
}

export interface LocationSummary {
    name: string;
    sensor_id: string;
    latitude: number;
    longitude: number;    
    flood_risk: 'SAFE' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
    river_level: number;
    change_rate: number;
    last_updated: string;
}

export interface ComprehensiveUpdate {
    locations: LocationSummary[];
    system_status: SystemStatus;
    alerts: Alert[];
    timestamp: string;
}

export interface ApiLocation {
    name: string;
    latitude: number;
    longitude: number;
    sensor_id: string;
    current_risk: 'SAFE' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';
    has_data: boolean;
}

export interface LocationsResponse {
    locations: ApiLocation[];
    total: number;
}

export interface TimelinePoint {
    timestamp: string;
    river_level: number;
    change_rate: number;
    flood_risk: 'SAFE' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
    minutes_ago: number;
}

export interface TimelineSummary {
    trend: 'Rising' | 'Falling';
    max_level: number;
    min_level: number;
    avg_change: number;
}

export interface LocationTimeline {
    location: string;
    timeline: TimelinePoint[];
    summary: TimelineSummary;
}

export interface HistoryPoint {
    timestamp: string;
    value: number;
    change: number;
}

export interface LocationHistory {
    location: string;
    current: {
        value: number;
        risk: 'LOW' | 'ELEVATED' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
        change: number;
        timestamp: string;
    };
    history: HistoryPoint[];
    trend: {
        direction: 'rising' | 'falling' | 'stable';
        percentage: number;
        color: 'red' | 'orange' | 'green' | 'blue';
    };
    stats: {
        max: number;
        min: number;
        avg: number;
        points: number;
    };
}

export interface ApiStatus {
    message: string;
    version: string;
    current_index: number;
    data_points: {
        river: number;
        weather: number;
        social: number;
    };
}

// Utility type for converting API risk levels to frontend risk levels
export type ApiRiskLevel = 'SAFE' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';
export type FrontendRiskLevel = 'safe' | 'low' | 'moderate' | 'high' | 'critical';

export const mapApiRiskToFrontend = (apiRisk: ApiRiskLevel): FrontendRiskLevel => {
    switch (apiRisk) {
        case 'SAFE':
            return 'safe';
        case 'LOW':
            return 'low';
        case 'MODERATE':
            return 'moderate';
        case 'HIGH':
            return 'high';
        case 'CRITICAL':
            return 'critical';
        default:
            return 'safe';
    }
};


// Analytics and Prediction types
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

// src/types/index.tsx

export type FloodLocation = {
  name: string
  lat: number
  lng: number
  riskLevel: 'low' | 'moderate' | 'high' | 'critical' | 'safe'
  // Enhanced fields from API integration
  sensor_id?: string
  has_data?: boolean
  api_risk_level?: string
}

// Add these to your existing types
export type SidebarProps = {
  onLocationSelect: (location: LocationSummary) => void
  selectedLocation: LocationSummary | null
}

export type Message = {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

export type ChatInterfaceProps = {
  isExpanded?: boolean
  onToggleExpand?: () => void
  selectedLocation?: LocationSummary | null
}
