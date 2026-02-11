# Chat Service Documentation

## Overview

The chat service provides an abstraction layer for the AI flood risk assistant, allowing seamless switching between static responses (for development/demo) and a real AI agent API.

## File Structure

```
src/lib/api/
├── chatService.ts          # Main service with static/API switching logic
├── client.ts               # API client for flood data
├── types.ts                # TypeScript type definitions
└── CHAT_SERVICE_README.md  # This file
```

## Configuration

### Switching Between Static and API Responses

In `chatService.ts`, modify the configuration at the top of the file:

```typescript
// Set to false when ready to use real API
const USE_STATIC_RESPONSES = true;

// Update with your agent API URL
const CHAT_API_BASE_URL = 'http://localhost:8000';
```

### Development Mode (Current)
- `USE_STATIC_RESPONSES = true`
- Uses predefined responses based on keyword matching
- Simulates API delay (1-1.5 seconds) for realistic UX
- No external API calls

### Production Mode (When Ready)
- `USE_STATIC_RESPONSES = false`
- Makes real API calls to your agent endpoint
- Falls back to static responses on error
- Maintains conversation history

## API Integration

### Expected API Endpoint

The service expects a POST endpoint at `/api/chat` that accepts:

```json
{
  "message": "What's the flood risk in St. Augustine?",
  "context": {
    "selectedLocation": {
      "name": "St. Augustine",
      "latitude": 10.6406,
      "longitude": -61.3994,
      // ... other location fields
    },
    "conversationHistory": [
      { "role": "user", "content": "..." },
      { "role": "assistant", "content": "..." }
    ]
  }
}
```

### Expected API Response

```json
{
  "message": "Response text from the agent",
  "confidence": 0.95,  // Optional
  "sources": ["Source 1", "Source 2"]  // Optional
}
```

## Features

### Loading States
- Typing indicator (animated dots) while waiting for response
- Disabled input field during loading
- Loading spinner on send button
- Visual feedback throughout the interaction

### Error Handling
- Automatic fallback to static responses on API error
- User-friendly error messages
- Maintains conversation continuity

### Context Awareness
- Tracks selected location from map
- Generates contextual suggested questions
- Maintains conversation history (last 10 messages)
- Updates when location changes

### Suggested Questions
Dynamically generated based on:
- Current selected location
- User's conversation context
- Available features (evacuation routes, weather, etc.)

## Usage

### In Components

```typescript
import { chatService, getContextualQuestions } from '@/lib/api/chatService';

// Send a message
const response = await chatService.sendMessage({
  message: "What's the current flood risk?",
  context: {
    selectedLocation: myLocation,
  }
});

// Get contextual questions
const questions = getContextualQuestions(selectedLocation);

// Clear conversation history
chatService.clearHistory();

// Get conversation history
const history = chatService.getHistory();
```

### Message Flow

1. User types message or clicks suggested question
2. User message added to chat UI
3. Typing indicator appears
4. Service processes message (static or API)
5. Response received and displayed
6. Typing indicator removed
7. Input re-enabled for next message

## Supported Topics (Static Mode)

### Location-Specific
- Port of Spain
- San Fernando
- Arima
- Chaguanas
- Point Fortin
- St. Augustine

### General Topics
- Flood risk levels
- Evacuation routes
- Current conditions
- Emergency shelters
- Safety tips (risk-level specific)
- Weather conditions
- Flood season preparation
- Flood warning actions

## Customization

### Adding New Static Responses

In `chatService.ts`, add to the `getStaticResponse` method:

```typescript
else if (inputText.includes('your-keyword')) {
    responseText = 'Your custom response';
}
```

### Modifying API Integration

Update the `getApiResponse` method in `chatService.ts`:

```typescript
private async getApiResponse(request: ChatRequest): Promise<ChatResponse> {
    // Customize headers, body structure, etc.
    const response = await fetch(`${CHAT_API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${YOUR_API_KEY}`, // Add if needed
        },
        body: JSON.stringify({
            // Customize request structure
        }),
    });
    
    // Parse and return response
}
```

## Testing

### Test Static Responses
1. Keep `USE_STATIC_RESPONSES = true`
2. Test various questions and topics
3. Verify loading states and error handling
4. Check context awareness with location changes

### Test API Integration
1. Set up your API endpoint
2. Update `CHAT_API_BASE_URL`
3. Set `USE_STATIC_RESPONSES = false`
4. Test with sample requests
5. Verify fallback to static on error

## Type Safety

The service uses TypeScript interfaces for type safety:

- `ChatMessage`: Individual messages in conversation
- `ChatRequest`: Request to send message
- `ChatResponse`: Response from service
- `ChatLocation`: Union type for FloodLocation | LocationSummary

## Performance Considerations

- Conversation history limited to last 10 messages
- Simulated delay in static mode for realistic UX
- Async/await for non-blocking operations
- Error boundaries prevent chat crashes

## Future Enhancements

Potential improvements when connecting to real API:

1. **Streaming Responses**: Display text as it's generated
2. **Multi-modal**: Support images, charts, maps in responses
3. **Voice Input**: Add speech-to-text capability
4. **Sentiment Analysis**: Adjust tone based on risk level
5. **Proactive Alerts**: Push notifications for critical updates
6. **Multi-language**: Support for different languages
7. **Offline Mode**: Cache common responses
8. **Analytics**: Track common questions and improve responses

## Troubleshooting

### API Not Responding
- Check `CHAT_API_BASE_URL` is correct
- Verify API is running and accessible
- Check network tab in browser dev tools
- Service will fallback to static responses

### Loading State Stuck
- Check browser console for errors
- Verify API response format matches expected structure
- Timeout may need adjustment in production

### Context Not Working
- Verify `selectedLocation` prop is passed correctly
- Check location object has required fields
- Confirm location name matches expected format

## Support

For issues or questions:
1. Check browser console for errors
2. Verify API endpoint configuration
3. Test with static responses first
4. Review TypeScript type errors
5. Check network requests in dev tools
