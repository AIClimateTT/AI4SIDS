// Chat service — connects to the RAG service's OpenAI-compatible API
// Manages conversation history with localStorage persistence

import { env } from '@/lib/env/client';

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

const STORAGE_KEY = 'ai4sids-chat-history';
const USER_ID_KEY = 'ai4sids-user-id';
/**
 * Main chat service — speaks OpenAI /v1/chat/completions format
 */
class ChatService {
    /**
     * Send a message along with conversation history to the RAG service.
     * Returns the assistant's reply as a string.
     */
    async sendMessage(userMessage: string, history: ChatMessage[]): Promise<string> {
        const apiBase = env.VITE_CHAT_API_BASE_URL;

        const messages = [
            ...history.map(m => ({ role: m.role, content: m.content })),
            { role: 'user' as const, content: userMessage },
        ];
        const userId = this.getUserId();
        
        const response = await fetch(`${apiBase}/v1/chat/completions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                model: 'ai4sids-climate-assistant',
                messages,
            }),
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        const reply = data.choices?.[0]?.message?.content;

        if (!reply) {
            throw new Error('No response content from API');
        }

        return reply;
    }

    getUserId(): string {
        let userId = localStorage.getItem(USER_ID_KEY);
        if (!userId) {
            userId = crypto.randomUUID();
            localStorage.setItem(USER_ID_KEY, userId);
        }
        return userId;
    }

    /**
     * Load conversation history from localStorage.
     * Returns an empty array if nothing is stored.
     */
    loadHistory(): ChatMessage[] {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return [];
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) return parsed;
        } catch {
            // Corrupt data — start fresh
        }
        return [];
    }

    /**
     * Save conversation history to localStorage.
     */
    saveHistory(messages: ChatMessage[]): void {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
        } catch {
            // Storage full or unavailable — silently ignore
        }
    }

    /**
     * Clear saved conversation history.
     */
    clearHistory(): void {
        localStorage.removeItem(STORAGE_KEY);
    }
}

// Export singleton instance
export const chatService = new ChatService();

/**
 * Suggested questions for the chat UI (no location dependency)
 */
/**
 * Suggested questions ordered to match the demo video flow:
 *   1. Broad overview  →  2. Location drill-down  →  3. River trend
 *   4. Community pulse →  5. Off-topic guard      →  6. Emergency action
 */
export function getContextualQuestions(_selectedLocation?: unknown): string[] {
    return [
        "What's the flood risk right now?",
        "I'm in St. Augustine, what should I know?",
        "Is the water rising near Caroni?",
        "What are people saying on social media?",
        "How do I cook pork?",
        "Should I evacuate? What do I do if flooding starts?",
    ];
}
