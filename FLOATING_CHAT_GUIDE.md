# Floating Chat Button - Implementation Guide

## 🎉 What Changed

The chat interface now has a **floating action button (FAB)** that appears in the bottom-right corner of the screen. The chat is hidden by default and opens when you click the button.

## 📐 Visual Layout

### Before (Hidden State)
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                                                     │
│         Your Main Content (Map, Dashboard)         │
│                                                     │
│                                                     │
│                                                     │
│                                                     │
│                                                     │
│                                            ┌─────┐ │
│                                            │ 💬  │ │ ← Floating button
│                                            └─────┘ │
└─────────────────────────────────────────────────────┘
```

### After Clicking Button (Chat Open)
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│         Your Main Content (Map, Dashboard)         │
│                                            ┌─────┐ │
│                                            │Chat │ │
│                                            │     │ │
│                                            │ •••│ │
│                                            │     │ │
│                                            │     │ │
│                                            └─────┘ │
│                                            ┌─────┐ │
│                                            │  ✕  │ │ ← Close button
│                                            └─────┘ │
└─────────────────────────────────────────────────────┘
```

## 🚀 How to Use

### Option 1: Use the New Component (Recommended)

Replace your existing chat implementation with:

```tsx
import { ChatWithButton } from '@/components/chat-interface';

function YourPage() {
  return (
    <div className="h-screen">
      {/* Your main content */}
      <div className="h-full">
        {/* Map, dashboard, etc. */}
      </div>
      
      {/* Just add this - it handles everything! */}
      <ChatWithButton />
    </div>
  );
}
```

### Option 2: With Location Context

```tsx
import { ChatWithButton } from '@/components/chat-interface';
import { useState } from 'react';

function YourPage() {
  const [selectedLocation, setSelectedLocation] = useState(null);

  return (
    <div className="h-screen">
      {/* Your content */}
      <YourMapComponent onLocationSelect={setSelectedLocation} />
      
      {/* Chat with location awareness */}
      <ChatWithButton selectedLocation={selectedLocation} />
    </div>
  );
}
```

## 🎨 Component Exports

The chat interface now exports **two components**:

1. **`ChatInterface`** (default export)
   - The chat UI itself
   - Used internally by ChatWithButton
   - Use this if you want custom positioning/behavior

2. **`ChatWithButton`** (named export) ⭐ **Use this one**
   - Complete package with floating button
   - Handles show/hide automatically
   - Bottom-right positioning built-in

## 🔧 Customization

### Change Button Position

Edit `chat-interface.tsx` line ~280:
```tsx
<button
  className={`fixed bottom-6 right-6 z-40 ...`}
  //              ↑        ↑
  //         Change these values
```

### Change Button Colors

Edit `chat-interface.tsx` line ~282:
```tsx
className={`... ${
  isOpen 
    ? 'bg-red-600 hover:bg-red-700'      // When open (X button)
    : 'bg-blue-600 hover:bg-blue-700'    // When closed (chat icon)
} ...`}
```

### Change Chat Position When Open

Edit `chat-interface.tsx` line ~272:
```tsx
className={`fixed ${
  isExpanded 
    ? 'inset-4'              // Full screen mode
    : 'bottom-24 right-4'    // Normal mode - change these
} z-50 ...`}
```

## 🎯 Features

### ✅ Floating Action Button
- **Position**: Bottom-right corner (24px from edges)
- **Icon**: Chat bubble when closed, X when open
- **Color**: Blue when closed, red when open
- **Animation**: Smooth transitions
- **Accessibility**: ARIA labels for screen readers

### ✅ Chat Interface
- **Opens**: Above the FAB button
- **Closes**: Click the FAB or close button in header
- **Expand**: Full-screen mode available
- **Responsive**: Works on all screen sizes

### ✅ Smart Behavior
- **Auto-close on expand close**: Collapsing expanded chat doesn't close it
- **Focus management**: Input auto-focuses when appropriate
- **Z-index management**: Always appears on top (z-40 button, z-50 chat)
- **No positioning needed**: Works anywhere in your component tree

## 📱 Responsive Behavior

### Desktop (≥768px)
```
Chat size: 384px wide × 500px tall
Position: 96px from bottom, 16px from right
Button: 24px from bottom and right
```

### Mobile (<768px)
The same positioning works, but you may want to adjust:
- Make chat take more screen width
- Position closer to edges
- Consider full-screen mode by default

## 🎭 Visual States

### 1. Hidden (Default)
- Only FAB visible
- Blue chat icon
- Subtle shadow

### 2. Chat Open
- FAB changes to red with X icon
- Chat appears above button
- Smooth slide-in animation

### 3. Chat Expanded
- Chat takes full screen (inset-4 = 16px from all edges)
- Minimize button in header
- FAB still visible to close

## 💡 Pro Tips

### Tip 1: Position Away from Other FABs
If you have other floating buttons:
```tsx
{/* Your other FAB */}
<button className="fixed bottom-6 left-6">...</button>

{/* Chat FAB - automatically on the right */}
<ChatWithButton />
```

### Tip 2: Add Notification Badge
Uncomment lines in `chat-interface.tsx` (~316) to show unread count:
```tsx
{!isOpen && true && ( // Change false to true
  <div className="fixed bottom-16 right-16 z-50 bg-red-500...">
    3
  </div>
)}
```

### Tip 3: Hide on Specific Pages
```tsx
const showChat = usePathname() !== '/admin'; // Hide on admin page

{showChat && <ChatWithButton />}
```

### Tip 4: Keyboard Shortcut
Add a keyboard shortcut to open chat:
```tsx
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.ctrlKey && e.key === '/') {
      setIsOpen(true);
    }
  };
  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
```

## 🔄 Migration Guide

### From Old Implementation

**Before:**
```tsx
<div className="absolute top-4 right-4 z-10">
  <ChatInterface 
    isExpanded={isExpanded}
    onToggleExpand={() => setIsExpanded(!isExpanded)}
    selectedLocation={selectedLocation}
  />
</div>
```

**After:**
```tsx
<ChatWithButton selectedLocation={selectedLocation} />
```

That's it! Remove all the positioning code, state management for isExpanded, and manual button creation.

## 🐛 Troubleshooting

### Button Not Showing
- Check z-index conflicts (chat uses z-40 and z-50)
- Verify parent container isn't hiding overflow
- Check if component is rendered

### Chat Appears Under Content
- Increase z-index values in `chat-interface.tsx`
- Check parent container stacking context

### Click Not Working
- Verify no elements covering the button
- Check pointer-events CSS
- Console log the click handler

### Position Wrong on Mobile
- Adjust `bottom-6 right-6` values
- Consider viewport units (vh/vw)
- Test on actual devices, not just browser resize

## 📊 Technical Details

**Component Structure:**
```
ChatWithButton
├── Chat Interface (conditionally rendered)
│   ├── Header with expand/collapse
│   ├── Suggested questions
│   ├── Messages area
│   │   └── Typing indicator
│   └── Input area
└── Floating Action Button
    ├── Chat icon (closed state)
    └── X icon (open state)
```

**State Management:**
- `isOpen`: Controls chat visibility
- `isExpanded`: Controls full-screen mode
- Automatically syncs when closing

**Props:**
```typescript
interface Props {
  selectedLocation?: LocationSummary | null;
}
```

## ✅ Testing Checklist

- [ ] Button appears bottom-right
- [ ] Click opens chat
- [ ] Click again closes chat
- [ ] Expand/collapse works
- [ ] Loading states show
- [ ] Suggested questions update
- [ ] Location context works
- [ ] Responsive on mobile
- [ ] No z-index conflicts
- [ ] Smooth animations

---

**Status**: ✅ Complete and ready to use!
**File**: `chat-interface.tsx`
**Export**: `ChatWithButton` (named export)
