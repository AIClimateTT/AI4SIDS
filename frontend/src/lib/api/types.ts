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