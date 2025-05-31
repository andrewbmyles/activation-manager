# Variable Picker API Documentation

## Overview

The Variable Picker API provides endpoints and methods for semantic variable search, refinement, and selection within the Enhanced NL Audience Builder.

## API Endpoints

### 1. Process Workflow

**Endpoint**: `processWorkflow`  
**Method**: `POST`  
**Purpose**: Process user input to find semantically matching variables

#### Request

```typescript
{
  action: 'process',
  payload: {
    input: string  // User's search query or refinement text
  }
}
```

#### Response

```typescript
{
  variables: Array<{
    code: string;           // Unique variable identifier
    description: string;    // Human-readable variable name
    type: string;          // Variable category (demographic, lifestyle, etc.)
    relevance_score: number; // AI-generated relevance score (0-1)
    id?: string;           // Optional unique ID
    category?: string;     // Optional category grouping
    dataAvailability?: {   // Optional data source availability
      first_party: boolean;
      third_party: boolean;
      clean_room: boolean;
    }
  }>,
  segments?: Array<SegmentGroup>  // Optional segment data
}
```

#### Example Usage

```typescript
const result = await processWorkflow.mutateAsync({
  action: 'process',
  payload: { 
    input: 'environmentally conscious millennials' 
  }
});

// Result:
{
  variables: [
    {
      code: 'ECO_INDEX',
      description: 'Environmental Consciousness Score',
      type: 'lifestyle',
      relevance_score: 0.95,
      id: 'ECO_INDEX'
    },
    {
      code: 'AGE_25_40',
      description: 'Millennials (Age 25-40)',
      type: 'demographic',
      relevance_score: 0.92,
      id: 'AGE_25_40'
    }
  ]
}
```

## Component Methods

### handleDynamicSearch

Performs real-time variable search based on user input.

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

## State Management

### Key State Variables

```typescript
interface VariablePickerState {
  // Current workflow step (4 = variable selection)
  currentStep: number;
  
  // User's input for refinement
  userInput: string;
  
  // Loading state for searches
  isTyping: boolean;
  
  // Debounce timer reference
  typingTimer: NodeJS.Timeout | null;
  
  // List of suggested variables from API
  suggestedVariables: Variable[];
  
  // Set of selected variable IDs
  selectedVariables: Set<string>;
  
  // Session ID for API calls
  sessionId: string | null;
}
```

## Integration Points

### 1. With Enhanced NL Audience Builder

The variable picker integrates seamlessly with the audience builder workflow:

```typescript
// Step progression
1. Data Type Selection
2. Audience Description
3. Processing
4. Variable Selection (Refine enabled here)
5. Segment Creation
6. Review
7. Distribution
```

### 2. With Search Debouncing

Automatic search triggers after 500ms of inactivity:

```typescript
useEffect(() => {
  if (currentStep === 4 && userInput.trim().length > 0) {
    if (typingTimer) {
      clearTimeout(typingTimer);
    }
    
    setIsTyping(true);
    
    const timer = setTimeout(() => {
      handleDynamicSearch();
    }, 500);
    
    setTypingTimer(timer);
  }
}, [userInput, currentStep]);
```

## Error Handling

### API Errors

```typescript
try {
  const result = await processWorkflow.mutateAsync(payload);
  // Handle success
} catch (error) {
  console.error('Dynamic search error:', error);
  // Optional: Show user-friendly error message
  setMessages(prev => [...prev, {
    type: 'assistant',
    content: 'Unable to refine search. Please try again.'
  }]);
}
```

### Validation

- Empty input is ignored
- Session ID must be present
- Minimum 1 character for search

## Performance Considerations

1. **Debouncing**: 500ms delay prevents excessive API calls
2. **Pre-selection**: Top 8 variables auto-selected for convenience
3. **Batch Updates**: State updates batched for performance
4. **Memoization**: Consider memoizing variable lists for large datasets

## Usage Examples

### Basic Refinement

```typescript
// User types in refinement input
setUserInput('urban sustainability');

// After 500ms, triggers search
// API returns relevant variables
// UI updates with new suggestions
```

### Manual Refinement

```typescript
// User clicks Refine button
handleDynamicSearch();

// Immediate search execution
// Loading state shown
// Results update on completion
```

### Variable Selection

```typescript
// User toggles checkbox
const newSelected = new Set(selectedVariables);
if (checked) {
  newSelected.add(variableId);
} else {
  newSelected.delete(variableId);
}
setSelectedVariables(newSelected);
```

## Testing

### Unit Tests
- Mock API responses
- Test debounce timing
- Verify state updates
- Check error handling

### Integration Tests
- Full workflow testing
- API interaction verification
- State persistence
- UI synchronization

## Best Practices

1. **Always check session ID** before API calls
2. **Provide loading feedback** during searches
3. **Handle empty results** gracefully
4. **Maintain selection state** during refinements
5. **Clear error states** on successful operations

## Future Enhancements

1. **Caching**: Cache frequent searches
2. **Pagination**: Handle large result sets
3. **Filters**: Add category/type filters
4. **History**: Search history functionality
5. **Batch Operations**: Multi-select actions