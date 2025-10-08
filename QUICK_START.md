# Chat Interface - Quick Start Guide

## 🚀 Current Status
Your chat interface is **fully functional** with static responses and ready to connect to an API when you're ready.

## 📁 What Changed

```
frontend/
├── src/
│   ├── components/
│   │   ├── chat-interface.tsx          ✨ Refactored with loading states
│   │   └── chat-interface-examples.tsx  📘 Usage examples
│   └── lib/
│       └── api/
│           ├── chatService.ts           🔧 New service layer
│           └── CHAT_SERVICE_README.md   📖 Full documentation
└── CHAT_REFACTORING_SUMMARY.md         📝 This guide
```

## 🎯 How It Works Now

### Static Mode (Current - Development)
```
User Question → Chat Service (Static) → Predefined Response → UI Update
                      ↓
                  Simulated 1s delay
                      ↓
                  Loading states
```

### API Mode (When Ready - Production)
```
User Question → Chat Service (API) → Your AI Agent → Response → UI Update
                      ↓                      ↓
              Loading states         If error: fallback to static
```

## 🎨 Loading States in Action

### 1. User Types Message
```
┌─────────────────────────────────────┐
│ Ask about flood risks...        [×] │
│─────────────────────────────────────│
│                                     │
│ Hello! I can help you...            │
│                                     │
│                             What's  │
│                     the flood risk? │
│                                     │
│─────────────────────────────────────│
│ Ask about flood risks... [Send]     │
└─────────────────────────────────────┘
```

### 2. Processing (Loading State)
```
┌─────────────────────────────────────┐
│ Waiting for response...         [×] │
│─────────────────────────────────────│
│                                     │
│ Hello! I can help you...            │
│                                     │
│                             What's  │
│                     the flood risk? │
│                                     │
│ ● ● ●                               │  ← Animated typing indicator
│                                     │
│─────────────────────────────────────│
│ Waiting for response... [⟳]         │  ← Disabled input, spinner button
└─────────────────────────────────────┘
```

### 3. Response Received
```
┌─────────────────────────────────────┐
│ Ask about flood risks...        [×] │
│─────────────────────────────────────│
│                                     │
│ Hello! I can help you...            │
│                                     │
│                             What's  │
│                     the flood risk? │
│                                     │
│ Areas with highest flood risk:      │
│ San Fernando (CRITICAL)...          │
│                                     │
│─────────────────────────────────────│
│ Ask about flood risks... [Send]     │
└─────────────────────────────────────┘
```

## 🔧 Switch to API Mode (3 Steps)

### Step 1: Open Configuration
File: `frontend/src/lib/api/chatService.ts`

### Step 2: Change These Lines
```typescript
// Line 7-8: Change from true to false
const USE_STATIC_RESPONSES = false;  // ← Change this

// Line 9: Update with your API URL
const CHAT_API_BASE_URL = 'https://your-agent-api.com';  // ← Update this
```

### Step 3: That's It!
The chat will now use your API automatically. All loading states, error handling, and fallback logic work the same.

## 📡 API Requirements

Your API endpoint should accept:
```typescript
POST /api/chat
Content-Type: application/json

{
  "message": "User's question",
  "context": {
    "selectedLocation": {
      "name": "St. Augustine",
      "latitude": 10.6406,
      "longitude": -61.3994,
      "flood_risk": "HIGH",
      // ... other fields
    },
    "conversationHistory": [
      { "role": "user", "content": "Previous message" },
      { "role": "assistant", "content": "Previous response" }
    ]
  }
}
```

And return:
```typescript
{
  "message": "AI agent's response text",
  "confidence": 0.95,        // Optional
  "sources": ["Source 1"]    // Optional
}
```

## 🧪 Test It Now

### Test Static Responses
1. Run your frontend: `npm run dev` or `pnpm dev`
2. Open the chat interface
3. Try these questions:
   - "What areas have the highest flood risk?"
   - "What should I do during a flood warning?"
   - "Show me current weather conditions"

### Watch Loading States
1. Type a message
2. Press Send
3. Observe:
   - Input becomes disabled
   - Button shows spinner
   - Typing indicator appears (● ● ●)
   - After ~1 second, response appears
   - Input re-enables and focuses

### Test Context Awareness
1. Select a location on the map
2. Notice suggested questions update
3. Bot acknowledges the location
4. Ask location-specific questions

## 💡 Pro Tips

### Customize Static Responses
Edit `chatService.ts` → `getStaticResponse()` method:
```typescript
else if (inputText.includes('your-keyword')) {
    responseText = 'Your custom response';
}
```

### Adjust Loading Delay
```typescript
// Line 73: Change delay time
await new Promise(resolve => setTimeout(resolve, 500)); // 0.5s instead of 1-1.5s
```

### Modify Suggested Questions
Edit the `getContextualQuestions()` function at the bottom of `chatService.ts`

## 📚 Documentation Files

1. **CHAT_SERVICE_README.md** - Complete technical documentation
2. **chat-interface-examples.tsx** - Code examples and patterns  
3. **CHAT_REFACTORING_SUMMARY.md** - Detailed summary
4. **QUICK_START.md** - This file

## ⚡ Key Features

- ✅ **Loading States**: Animated indicators, disabled inputs, visual feedback
- ✅ **Error Handling**: Automatic fallback, user-friendly messages
- ✅ **Context Aware**: Location-specific responses and suggestions
- ✅ **Type Safe**: Full TypeScript support
- ✅ **API Ready**: Switch modes with one config change
- ✅ **Conversation History**: Tracks last 10 messages for context
- ✅ **Responsive**: Works in expanded and compact modes

## 🆘 Troubleshooting

### Chat Not Responding
→ Check browser console for errors
→ Verify `USE_STATIC_RESPONSES = true` for testing

### Loading State Stuck
→ Check console for JavaScript errors
→ Verify API endpoint is accessible (if in API mode)

### Questions Not Contextual
→ Ensure `selectedLocation` prop is passed to ChatInterface
→ Check location object has required fields

## 🎉 You're All Set!

Your chat interface is production-ready. When your AI agent API is ready:
1. Update 2 lines in `chatService.ts`
2. Deploy
3. Done!

---

**Questions?** Check the other documentation files for more details.
