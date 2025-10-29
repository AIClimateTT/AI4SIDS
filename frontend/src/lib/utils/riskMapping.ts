/**
 * Risk level mapping utilities
 * Maps API flood risk levels to component display formats
 */

export type ApiRiskLevel = 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW' | 'SAFE';
export type ComponentRiskLevel = 'critical' | 'high' | 'moderate' | 'low' | 'safe';

/**
 * Map API risk level (uppercase) to component format (lowercase)
 */
export const mapApiRiskToComponent = (apiRisk: string): ComponentRiskLevel => {
  const mapping: Record<ApiRiskLevel, ComponentRiskLevel> = {
    CRITICAL: 'critical',
    HIGH: 'high',
    MODERATE: 'moderate',
    LOW: 'low',
    SAFE: 'safe'
  };
  return mapping[apiRisk as ApiRiskLevel] || 'safe';
};

/**
 * Get Tailwind CSS classes for risk level badges/cards
 */
export const getRiskColor = (risk: ComponentRiskLevel): string => {
  const colors: Record<ComponentRiskLevel, string> = {
    'critical': 'bg-critical text-critical-foreground',
    'high': 'bg-high-risk text-high-risk-foreground',
    'moderate': 'bg-moderate text-moderate-foreground',
    'low': 'bg-low-risk text-low-risk-foreground',
    'safe': 'bg-safe text-safe-foreground'
  };
  return colors[risk];
};

/**
 * Get hex color codes for maps and charts
 */
export const getRiskHexColor = (risk: ComponentRiskLevel): string => {
  const colors: Record<ComponentRiskLevel, string> = {
    'critical': '#ef4444',   // Red-500
    'high': '#f97316',       // Orange-500
    'moderate': '#eab308',   // Yellow-500
    'low': '#84cc16',        // Lime-500
    'safe': '#22c55e'        // Green-500
  };
  return colors[risk];
};

/**
 * Get alert styling for Alert components
 */
export const getAlertStyle = (level: ComponentRiskLevel): string => {
  const styles: Record<ComponentRiskLevel, string> = {
    'critical': 'border-critical bg-critical/5 shadow-alert',
    'high': 'border-high-risk bg-high-risk/5',
    'moderate': 'border-moderate bg-moderate/5',
    'low': 'border-low-risk bg-low-risk/5',
    'safe': 'border-safe bg-safe/5'
  };
  return styles[level] || '';
};

/**
 * Get badge styling for Alert badges
 */
export const getAlertBadge = (level: ComponentRiskLevel): string => {
  const badges: Record<ComponentRiskLevel, string> = {
    'critical': 'bg-critical text-critical-foreground',
    'high': 'bg-high-risk text-high-risk-foreground',
    'moderate': 'bg-moderate text-moderate-foreground',
    'low': 'bg-low-risk text-low-risk-foreground',
    'safe': 'bg-safe text-safe-foreground'
  };
  return badges[level] || '';
};
