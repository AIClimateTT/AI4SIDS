// src/utils/mapUtils.tsx
export function getRiskColor(risk: string) {
  switch (risk) {
    case 'low': return '#22c55e'; // green
    case 'medium': return '#eab308'; // yellow
    case 'high': return '#f97316'; // orange
    case 'critical': return '#ef4444'; // red
    default: return '#6b7280';
  }
};