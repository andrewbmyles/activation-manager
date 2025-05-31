# Variable Refine Functionality Documentation

## Overview

The Variable Refine functionality allows users to dynamically search and filter variables during the audience building process. This feature enhances the variable selection experience by providing real-time semantic search capabilities.

## Features

### 1. Dynamic Search (Auto-Refine)
- **Trigger**: Automatically activates when user types in the input field during Step 4
- **Debounce**: 500ms delay after user stops typing to prevent excessive API calls
- **Visual Feedback**: Shows "Refining search..." with loading spinner

### 2. Manual Refine Button
- **Location**: Appears next to the submit button during Step 4
- **Style**: Purple button with Sparkles icon
- **States**: 
  - Enabled: When input has text and not currently searching
  - Disabled: When input is empty or search is in progress
  - Loading: Shows spinner during search

### 3. Semantic Variable Display
- **Label**: Shows "Semantic" instead of technical type names
- **Icon**: Brain icon (🧠) in indigo color indicating AI-powered matching
- **Score Tooltip**: Hover tooltip explaining relevance scores

## Implementation Details

### Component Structure

```typescript
// Key State Variables
const [currentStep, setCurrentStep] = useState(1);
const [userInput, setUserInput] = useState('');
const [isTyping, setIsTyping] = useState(false);
const [typingTimer, setTypingTimer] = useState<NodeJS.Timeout | null>(null);
const [suggestedVariables, setSuggestedVariables] = useState<Variable[]>([]);
```

### Refine Workflow

1. **User enters Step 4** after initial audience description
2. **Input field becomes active** for refining search
3. **As user types**:
   - Timer starts (500ms debounce)
   - After timeout, `handleDynamicSearch` is called
   - API request sent with refined query
4. **Results update** in real-time
5. **User can manually trigger** search with Refine button

### API Integration

```typescript
const handleDynamicSearch = async () => {
  if (!sessionId || !userInput.trim()) {
    setIsTyping(false);
    return;
  }

  try {
    const result = await processWorkflow.mutateAsync({
      action: 'process',
      payload: { input: userInput }
    });

    if (result.variables) {
      setSuggestedVariables(result.variables);
      // Pre-select top 8 variables
      const topVariables = result.variables.slice(0, 8);
      setSelectedVariables(new Set(topVariables.map(v => v.id)));
    }
  } catch (error) {
    console.error('Dynamic search error:', error);
  } finally {
    setIsTyping(false);
  }
};
```

## User Experience

### Visual Indicators

1. **Input Field State**
   - Placeholder: "Type to refine your search..."
   - Enabled during Step 4
   - Standard input styling with focus ring

2. **Refine Button**
   - Purple background (`bg-purple-500`)
   - Sparkles icon when ready
   - Loading spinner when processing
   - Disabled state styling

3. **Variable Display**
   - Brain icon with "Semantic" label
   - Relevance score with hover tooltip
   - Checkbox for selection
   - Hover effect on variable rows

### Score Tooltip Content

```
Relevance Score: [score]
This AI-generated score (0-1) indicates how closely 
this variable matches your audience description.
Higher scores = stronger semantic match
```

## Testing

### Unit Tests
- Input field enablement during Step 4
- Refine button visibility and states
- Dynamic search with debounce
- Loading states
- Variable list updates
- Score tooltip rendering

### Integration Tests
- Complete workflow from Step 1 to Step 4
- API mock responses
- State management
- User interactions

## Accessibility

- Keyboard navigation support
- Clear visual feedback for all states
- Descriptive tooltips
- Proper ARIA labels (to be implemented)

## Performance Considerations

- 500ms debounce prevents excessive API calls
- Efficient state updates
- Pre-selection of top variables for user convenience
- Optimized re-renders with React hooks

## Future Enhancements

1. **Advanced Filters**: Add category filters for variables
2. **Search History**: Remember previous searches
3. **Keyboard Shortcuts**: Quick actions for power users
4. **Batch Operations**: Select/deselect all matching variables
5. **Export Functionality**: Save refined variable sets