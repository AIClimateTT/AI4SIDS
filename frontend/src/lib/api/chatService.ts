// Chat service for handling agent responses
// Switch between static and API responses by changing USE_STATIC_RESPONSES

import type { FloodLocation , LocationSummary} from '@/lib/types';


import { env } from '../env/server';

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

// Union type to accept both location formats
type ChatLocation = FloodLocation | LocationSummary;

export interface ChatRequest {
    message: string;
    context?: {
        selectedLocation?: ChatLocation | null;
        conversationHistory?: ChatMessage[];
    };
}

export interface ChatResponse {
    message: string;
    confidence?: number;
    sources?: string[];
}

/**
 * Main chat service - handles both static and API responses
 */
class ChatService {
    private conversationHistory: ChatMessage[] = [];

    /**
     * Send a message and get a response
     */
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        // Add user message to history
        this.conversationHistory.push({
            role: 'user',
            content: request.message,
        });

        let response: ChatResponse;

        if (env.VITE_USE_STATIC_RESPONSES) {
            // Use static responses (current implementation)
            response = await this.getStaticResponse(request);
        } else {
            // Use real API
            response = await this.getApiResponse(request);
        }

        // Add bot response to history
        this.conversationHistory.push({
            role: 'assistant',
            content: response.message,
        });

        return response;
    }

    /**
     * Static response generator (current implementation)
     */
    private async getStaticResponse(request: ChatRequest): Promise<ChatResponse> {
        // Simulate API delay for realistic UX
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 500));

        const inputText = request.message.toLowerCase();
        const selectedLocation = request.context?.selectedLocation;
        let responseText = 'I can provide information about flood risks in Trinidad and Tobago.';

        // Helper to get risk level from either location type
        const getRiskLevel = (location: ChatLocation): string => {
            if ('riskLevel' in location) {
                return location.riskLevel.toUpperCase();
            } else if ('flood_risk' in location) {
                return location.flood_risk;
            }
            return 'UNKNOWN';
        };

        // Location-specific responses
        if (inputText.includes('port of spain')) {
            responseText = 'Port of Spain has HIGH flood risk due to its coastal location and urban drainage issues. Heavy rainfall often causes flooding in downtown areas, particularly around Independence Square and South Quay.';
        } else if (inputText.includes('san fernando')) {
            responseText = 'San Fernando has CRITICAL flood risk, especially during the rainy season. The Guaracara River and coastal proximity contribute to frequent flooding. Main affected areas include High Street and Coffee Street.';
        } else if (inputText.includes('arima')) {
            responseText = 'Arima has MEDIUM flood risk. While inland, the area can experience flash floods during heavy rainfall due to topography. The Arima River can overflow during intense storms.';
        } else if (inputText.includes('chaguanas')) {
            responseText = 'Chaguanas has MEDIUM flood risk, particularly in low-lying areas like Longdenville and Edinburgh. Urban development has impacted natural drainage, leading to occasional flooding.';
        } else if (inputText.includes('point fortin')) {
            responseText = 'Point Fortin has LOW flood risk, but localized flooding can occur during intense rain events. The area is generally well-drained due to its elevation.';
        } else if (inputText.includes('st. augustine') || inputText.includes('st augustine')) {
            responseText = 'St. Augustine has MEDIUM to HIGH flood risk due to the Caroni River proximity. The area experiences seasonal flooding, particularly during heavy rainfall. Monitor river levels closely during wet season.';
        }
        // Context-aware responses for selected location
        else if (selectedLocation && inputText.includes(`flood risk in ${selectedLocation.name.toLowerCase()}`)) {
            const riskLevel = getRiskLevel(selectedLocation);
            responseText = `${selectedLocation.name} currently has ${riskLevel} flood risk. `;
            
            if (riskLevel === 'CRITICAL') {
                responseText += 'Immediate precautions recommended. Avoid unnecessary travel and stay informed about evacuation orders.';
            } else if (riskLevel === 'HIGH') {
                responseText += 'Monitor conditions closely. Prepare emergency supplies and know your evacuation routes.';
            } else if (riskLevel === 'MEDIUM') {
                responseText += 'Stay alert to changing conditions. Review your flood preparedness plan.';
            } else {
                responseText += 'Current conditions are stable, but always stay prepared during rainy season.';
            }
        }
        // Evacuation routes
        else if (inputText.includes('evacuation routes') || inputText.includes('evacuation route')) {
            if (selectedLocation) {
                responseText = `Evacuation routes from ${selectedLocation.name}: Primary route via Highway, Secondary route via local roads to higher ground. Nearest shelter: Community Center (2.3km away). Current route status: PASSABLE.`;
            } else {
                responseText = 'Main evacuation routes: Use major highways to move to higher ground. Avoid low-lying areas and bridges during heavy rain. Emergency shelters are located at community centers and schools.';
            }
        }
        // Current conditions
        else if (inputText.includes('current conditions')) {
            if (selectedLocation) {
                const riskLevel = getRiskLevel(selectedLocation);
                responseText = `Current conditions in ${selectedLocation.name}: Weather - Light rain, River levels - Normal, Road access - Clear, Emergency services - Standby. Risk level: ${riskLevel}.`;
            } else {
                responseText = 'Current conditions across Trinidad: Mixed weather patterns, some areas experiencing light rain. River levels are within normal ranges. All major roads are passable.';
            }
        }
        // Generic responses for preset questions
        else if (inputText.includes('highest flood risk')) {
            responseText = 'Areas with highest flood risk: San Fernando (CRITICAL), Port of Spain (HIGH), followed by low-lying coastal areas. These areas are most vulnerable due to sea level, river proximity, and drainage issues.';
        } else if (inputText.includes('prepare for flood season')) {
            responseText = 'Flood season preparation: 1) Create emergency kit with water, food, flashlight, radio 2) Know evacuation routes 3) Waterproof important documents 4) Have emergency contacts ready 5) Monitor weather alerts regularly.';
        } else if (inputText.includes('emergency shelters') || inputText.includes('emergency shelter')) {
            responseText = 'Emergency shelters are located at: Schools, Community centers, Religious buildings, Government buildings. Major shelters: Arima Community Center, San Fernando Town Hall, Chaguanas Secondary School. Check with local authorities for current availability.';
        } else if (inputText.includes('during a flood warning') || inputText.includes('flood warning')) {
            responseText = 'During flood warning: 1) Stay indoors if possible 2) Move to higher ground immediately 3) Avoid walking/driving through floodwater 4) Listen to emergency broadcasts 5) Have emergency supplies ready 6) Contact authorities if in immediate danger.';
        } else if (inputText.includes('weather conditions') || inputText.includes('weather')) {
            responseText = 'Current weather: Partly cloudy with scattered showers expected. Temperature: 28°C. Rainfall in last 24hrs: Moderate in central areas. Next 48hrs: Increased rainfall expected, monitor for flood advisories.';
        } else if (inputText.includes('safety tips')) {
            const floodRisk = selectedLocation ? getRiskLevel(selectedLocation) : 'general';
            
            if (floodRisk === 'CRITICAL') {
                responseText = 'CRITICAL risk safety tips: Evacuate immediately if ordered, avoid all unnecessary travel, move valuables to high areas, stay tuned to emergency broadcasts, never attempt to cross flooded roads.';
            } else if (floodRisk === 'HIGH') {
                responseText = 'HIGH risk safety tips: Prepare to evacuate, avoid low-lying areas, secure outdoor items, charge devices, keep emergency supplies accessible, monitor water levels closely.';
            } else if (floodRisk === 'MEDIUM') {
                responseText = 'MEDIUM risk safety tips: Stay alert, avoid unnecessary travel to flood-prone areas, keep emergency kit updated, monitor weather updates, know nearest evacuation routes.';
            } else {
                responseText = 'General safety tips: Never drive through flooded roads, stay informed during heavy rain, keep emergency supplies ready, know your evacuation routes, report flooding to authorities.';
            }
        }

        return {
            message: responseText,
            confidence: 0.95,
            sources: ['Trinidad & Tobago Flood Risk Database', 'Local Weather Service'],
        };
    }

    /**
     * Real API response (to be implemented)
     */
    private async getApiResponse(request: ChatRequest): Promise<ChatResponse> {
        try {
            const response = await fetch(`${env.VITE_CHAT_API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: request.message,
                    context: {
                        selectedLocation: request.context?.selectedLocation,
                        conversationHistory: this.conversationHistory.slice(-10), // Last 10 messages for context
                    },
                }),
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }

            const data = await response.json();
            
            return {
                message: data.message || data.response,
                confidence: data.confidence,
                sources: data.sources,
            };
        } catch (error) {
            console.error('Chat API error:', error);
            
            // Fallback to static response on error
            return this.getStaticResponse(request);
        }
    }

    /**
     * Clear conversation history
     */
    clearHistory(): void {
        this.conversationHistory = [];
    }

    /**
     * Get conversation history
     */
    getHistory(): ChatMessage[] {
        return [...this.conversationHistory];
    }
}

// Export singleton instance
export const chatService = new ChatService();

/**
 * Helper function to generate contextual questions based on location
 */
export function getContextualQuestions(selectedLocation?: ChatLocation | null): string[] {
    if (selectedLocation) {
        // Get risk level for display
        let riskLevel = 'unknown';
        if ('riskLevel' in selectedLocation) {
            riskLevel = selectedLocation.riskLevel;
        } else if ('flood_risk' in selectedLocation) {
            riskLevel = selectedLocation.flood_risk.toLowerCase();
        }

        return [
            `What's the flood risk in ${selectedLocation.name}?`,
            `Show me evacuation routes from ${selectedLocation.name}`,
            `What are the current conditions in ${selectedLocation.name}?`,
            `Safety tips for ${riskLevel} risk areas`,
        ];
    } else {
        return [
            "What areas have the highest flood risk?",
            "How do I prepare for flood season?",
            "Where are the emergency shelters?",
            "What should I do during a flood warning?",
            "Show me current weather conditions",
        ];
    }
}
