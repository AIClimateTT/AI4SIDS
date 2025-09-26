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
    flood_risk: 'LOW' | 'ELEVATED' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
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
    level: 'low' | 'elevated' | 'medium' | 'high' | 'critical';
    location: string;
    message: string;
    timestamp: string;
}

export interface LocationSummary {
    name: string;
    sensor_id: string;
    latitude: number;
    longitude: number;    
    flood_risk: 'LOW' | 'ELEVATED' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
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
    current_risk: 'LOW' | 'ELEVATED' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';
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
    flood_risk: 'LOW' | 'ELEVATED' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
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
export type ApiRiskLevel = 'LOW' | 'ELEVATED' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';
export type FrontendRiskLevel = 'low' | 'medium' | 'high' | 'critical';

export const mapApiRiskToFrontend = (apiRisk: ApiRiskLevel): FrontendRiskLevel => {
    switch (apiRisk) {
        case 'LOW':
            return 'low';
        case 'ELEVATED':
        case 'MEDIUM':
            return 'medium';
        case 'HIGH':
            return 'high';
        case 'CRITICAL':
            return 'critical';
        case 'UNKNOWN':
        default:
            return 'low';
    }
};