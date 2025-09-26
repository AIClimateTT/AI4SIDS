// src/data/floodLocations.tsx
import type { FloodLocation } from "@/types";

export const floodLocations: FloodLocation[] = [
    { name: "Port of Spain", lat: 10.6540, lng: -61.5097, riskLevel: "high" },
    { name: "Arima", lat: 10.6372, lng: -61.2828, riskLevel: "medium" },
    { name: "San Fernando", lat: 10.2799, lng: -61.4583, riskLevel: "critical" },
    { name: "Chaguanas", lat: 10.5158, lng: -61.4119, riskLevel: "medium" },
    { name: "Point Fortin", lat: 10.1786, lng: -61.6842, riskLevel: "low" },
    { name: "Scarborough", lat: 11.1817, lng: -60.7393, riskLevel: "high" },
];
