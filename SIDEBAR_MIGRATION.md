# Sidebar Migration Guide - From Timeline to Sparklines

## 🔄 Quick Migration

Replace the old sidebar with sparklines in **3 easy steps**.

---

## Step 1: Update Import

### **Before**:
```tsx
import EnhancedSidebar from '@/components/enhanced-sidebar';
```

### **After**:
```tsx
import SidebarWithSparklines from '@/components/sidebar-with-sparklines';
```

---

## Step 2: Update Component Usage

### **Before**:
```tsx
<EnhancedSidebar
  onLocationSelect={handleLocationSelect}
  selectedLocation={selectedLocation}
/>
```

### **After**:
```tsx
<SidebarWithSparklines
  onLocationSelect={handleLocationSelect}
  selectedLocation={selectedLocation}
/>
```

**Note**: Props remain the same! No changes needed.

---

## Step 3: Adjust Layout Width (Optional)

The new sidebar is wider (`420px` vs `320px`).

### **If you have hardcoded widths**:

**Before**:
```tsx
<div className="flex">
  <div className="w-80">{/* Sidebar */}</div>
  <div className="flex-1">{/* Map */}</div>
</div>
```

**After**:
```tsx
<div className="flex">
  <div className="w-[420px]">{/* Sidebar */}</div>
  <div className="flex-1">{/* Map */}</div>
</div>
```

### **If using Tailwind's responsive classes**:
No changes needed! The sidebar handles its own width.

---

## 📋 Side-by-Side Comparison

| Feature | Old Sidebar | New Sidebar |
|---------|------------|-------------|
| Width | 320px | 420px |
| Data Display | Text timeline | Sparkline charts |
| Grouping | Single list | Risk-based groups |
| Collapsible | No | Yes (by risk level) |
| Visual Trends | Text (↑↓) | Color-coded charts |
| Auto-refresh | Whole sidebar | Per-card (smart) |
| Space Efficiency | ~10 lines/location | ~4 lines/location |
| Performance | Good | Better (lazy loading) |

---

## 🎯 Benefits of Migration

### **Visual Improvements**:
- ✅ Instant trend recognition
- ✅ Color-coded risk indicators  
- ✅ Professional dashboard appearance
- ✅ Better data density

### **UX Improvements**:
- ✅ Collapsible sections reduce clutter
- ✅ Priority-based organization
- ✅ Click to select locations
- ✅ Real-time sparkline updates

### **Performance Improvements**:
- ✅ Lazy loading (collapsed sections don't render)
- ✅ Smart refresh (only expanded sections)
- ✅ Optimized data fetching
- ✅ Lower API call frequency for LOW risk

---

## 🔧 Configuration Options

### **Customize Initial Expanded Sections**:

In `sidebar-with-sparklines.tsx`:
```tsx
const [expandedSections, setExpandedSections] = useState({
  critical: true,   // Always show
  high: true,       // Show by default
  medium: false,    // Collapsed
  low: false,       // Collapsed
});
```

### **Adjust Auto-Refresh Behavior**:

In `sidebar-with-sparklines.tsx`:
```tsx
{groupedLocations.high.map((location) => (
  <SparklineCard
    autoRefresh={true}     // Change to false to disable
    refreshInterval={15000} // Change interval (ms)
    // ...
  />
))}
```

### **Modify Sidebar Width**:

In `sidebar-with-sparklines.tsx`:
```tsx
<div className="w-[420px] ...">
            ↑ Change this value
```

Recommended widths:
- **Compact**: `380px` - Tight but readable
- **Default**: `420px` - Balanced (current)
- **Spacious**: `480px` - More breathing room

---

## 🧪 Testing Checklist

After migration, test these scenarios:

### **Functionality**:
- [ ] Sidebar appears correctly
- [ ] Sparklines render with data
- [ ] Click location to select on map
- [ ] Expand/collapse sections work
- [ ] Auto-refresh updates charts
- [ ] System status displays correctly
- [ ] Alerts show when present

### **Visual**:
- [ ] Colors match risk levels
- [ ] Sparklines show correct trends
- [ ] Layout doesn't overlap
- [ ] Responsive on different screens
- [ ] Loading states work
- [ ] Error states display properly

### **Performance**:
- [ ] No lag when scrolling
- [ ] Charts update smoothly
- [ ] No console errors
- [ ] API calls are reasonable
- [ ] Memory usage is acceptable

---

## 📱 Mobile Considerations

The new sidebar is wider. For mobile views:

### **Option 1: Hide Sidebar on Mobile**:
```tsx
<div className="hidden md:block">
  <SidebarWithSparklines />
</div>
```

### **Option 2: Make Sidebar Full-Width on Mobile**:
```tsx
// In sidebar-with-sparklines.tsx
<div className="w-full md:w-[420px] ...">
```

### **Option 3: Slide-Over on Mobile**:
```tsx
const [sidebarOpen, setSidebarOpen] = useState(false);

<button 
  className="md:hidden"
  onClick={() => setSidebarOpen(true)}
>
  Menu
</button>

<div className={`
  fixed inset-y-0 left-0 z-50
  transform transition-transform
  ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
  md:relative md:translate-x-0
`}>
  <SidebarWithSparklines />
</div>
```

---

## 🐛 Common Issues & Solutions

### **Issue**: Sidebar too wide for layout

**Solution**: Adjust width in component
```tsx
<div className="w-[380px] ...">
```

### **Issue**: Sparklines not showing

**Solution**: 
1. Check backend `/api/history/{location}` is running
2. Verify `react-sparklines` is installed
3. Check browser console for errors

### **Issue**: Too many API calls

**Solution**: Disable auto-refresh for low-risk locations
```tsx
<SparklineCard autoRefresh={location.risk !== 'LOW'} />
```

### **Issue**: Performance lag with many locations

**Solution**: Keep more sections collapsed by default
```tsx
const [expandedSections, setExpandedSections] = useState({
  critical: true,
  high: false,    // Collapse high
  medium: false,
  low: false,
});
```

---

## 🔄 Rollback Plan

If you need to revert:

### **Step 1**: Change import back
```tsx
import EnhancedSidebar from '@/components/enhanced-sidebar';
```

### **Step 2**: Update component
```tsx
<EnhancedSidebar {...props} />
```

**Note**: Both sidebars will remain in the codebase, so you can switch anytime.

---

## 📊 Before vs After Screenshots

### **Old Sidebar** (Text Timeline):
```
┌──────────────────────────┐
│ AI4SIDS Monitor          │
├──────────────────────────┤
│ System Status            │
│ [4 Sensors] [Progress]   │
├──────────────────────────┤
│ 🔴 St. Augustine         │
│ 3.2m | +0.05m/15min      │
│ River Level: 3.2m        │
│ Change Rate: +0.05m      │
│ Last Updated: 2 min ago  │
│                          │
│ 🟠 Chaguanas            │
│ 2.8m | +0.03m/15min      │
│ River Level: 2.8m        │
│ ... (7 more lines)       │
└──────────────────────────┘
Height: ~15 lines per location
```

### **New Sidebar** (Sparklines):
```
┌────────────────────────────────┐
│ AI4SIDS Monitor    [2 Urgent]  │
├────────────────────────────────┤
│ System Status                  │
│ [4 Sensors]  [2 Alerts]        │
├────────────────────────────────┤
│ 🔴 CRITICAL (2)          ▼     │
│ ┌─────────────────────────┐    │
│ │ St. Augustine      3.2m │    │
│ │ [SPARKLINE CHART]  ↑    │    │
│ │ Updated: 14:30:00       │    │
│ └─────────────────────────┘    │
│                                │
│ 🟠 HIGH (3)              ▼     │
│ ┌─────────────────────────┐    │
│ │ Chaguanas          2.8m │    │
│ │ [SPARKLINE CHART]  ↑    │    │
│ └─────────────────────────┘    │
│                                │
│ 🟡 MEDIUM (5)            ▶     │
│ [Collapsed]                    │
└────────────────────────────────┘
Height: ~4 lines per location
```

**Space Savings**: 50-60% less vertical space

---

## ✅ Migration Complete!

Once you've completed these steps:

1. ✅ Import updated
2. ✅ Component replaced
3. ✅ Layout adjusted (if needed)
4. ✅ Testing completed

You're ready to use sparklines! 🎉

---

## 📚 Additional Resources

- **Full Implementation**: See `SPARKLINE_IMPLEMENTATION.md`
- **Component Docs**: Check `sparkline-card.tsx` comments
- **API Details**: Review `api/main.py` for endpoint info

---

**Need Help?** 
- Check the troubleshooting section above
- Review console for errors
- Test backend endpoint directly: `http://localhost:8000/api/history/St.%20Augustine`
