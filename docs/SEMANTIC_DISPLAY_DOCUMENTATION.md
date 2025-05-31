# Semantic Variable Display Documentation

## Overview

The Semantic Variable Display feature transforms how variables are presented to users, emphasizing their AI-powered semantic matching capabilities rather than technical implementation details.

## Key Changes

### 1. Visual Branding
- **Before**: Variables showed technical types (e.g., "parquet", "demographic")
- **After**: All variables display "Semantic" with Brain icon

### 2. Relevance Score Enhancement
- **Interactive Tooltip**: Hover-activated explanation
- **Clear Scoring Scale**: 0-1 range with interpretation
- **User-Friendly Language**: Non-technical explanation

## Component Implementation

### Variable Display Structure

```tsx
<div className="flex-1">
  <p className="text-sm font-medium text-gray-800">{variable.description}</p>
  <div className="flex items-center gap-2 mt-1">
    {/* Semantic Badge */}
    <div className="flex items-center gap-1">
      <Brain className="w-3 h-3 text-indigo-500" />
      <span className="text-xs text-gray-500">Semantic</span>
    </div>
    
    {/* Separator */}
    <span className="text-xs text-gray-500">•</span>
    
    {/* Score with Tooltip */}
    <div className="group relative inline-flex items-center">
      <span className="text-xs text-gray-500">Score: {variable.relevance_score}</span>
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-50 pointer-events-none">
        <div className="bg-gray-900 text-white text-xs rounded px-3 py-2 whitespace-nowrap max-w-xs">
          <p className="font-medium mb-1">Relevance Score: {variable.relevance_score}</p>
          <p>This AI-generated score (0-1) indicates how closely this variable matches your audience description.</p>
          <p className="mt-1">Higher scores = stronger semantic match</p>
          {/* Tooltip Arrow */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
            <div className="border-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## Design Decisions

### 1. Brain Icon Choice
- **Icon**: Lucide React's Brain icon
- **Color**: Indigo-500 (`#6366f1`)
- **Size**: 3x3 (0.75rem)
- **Rationale**: Visually represents AI/cognitive processing

### 2. Semantic Label
- **Text**: "Semantic" 
- **Style**: Small, gray text
- **Position**: Next to brain icon
- **Purpose**: Clearly indicates AI-powered matching

### 3. Tooltip Design
- **Trigger**: Hover on score
- **Background**: Dark gray (`gray-900`)
- **Text**: White with clear hierarchy
- **Arrow**: CSS triangle pointing to score
- **Z-index**: 50 to ensure visibility

## User Benefits

1. **Clarity**: Users immediately understand variables are AI-matched
2. **Trust**: Brain icon builds confidence in intelligent selection
3. **Education**: Tooltip teaches users about scoring system
4. **Consistency**: All variables have uniform presentation

## Styling Guidelines

### Color Palette
- **Brain Icon**: `text-indigo-500` (#6366f1)
- **Labels**: `text-gray-500` (#6b7280)
- **Tooltip BG**: `bg-gray-900` (#111827)
- **Tooltip Text**: White (#ffffff)

### Spacing
- **Icon Gap**: 1 unit (0.25rem)
- **Section Gap**: 2 units (0.5rem)
- **Tooltip Margin**: 2 units bottom

### Typography
- **Variable Name**: `text-sm font-medium`
- **Labels**: `text-xs`
- **Tooltip**: `text-xs` with `font-medium` for score

## Accessibility Considerations

1. **Color Contrast**: Meets WCAG AA standards
2. **Hover States**: Clear visual feedback
3. **Tooltip Positioning**: Always visible within viewport
4. **Icon Alternative**: Text label accompanies icon

## Testing Coverage

### Visual Tests
- Brain icon rendering
- Semantic label display
- Tooltip appearance on hover
- Score formatting

### Interaction Tests
- Hover behavior
- Tooltip positioning
- Click-through functionality
- Responsive design

## Migration Notes

### For Developers
1. Import Brain icon from lucide-react
2. Replace type display logic with semantic badge
3. Wrap score in tooltip container
4. Test hover interactions

### For Users
- No action required
- Existing workflows unchanged
- Enhanced visual clarity
- Better understanding of AI matching

## Future Enhancements

1. **Animated Tooltips**: Smooth fade-in transitions
2. **Score Visualization**: Mini progress bar
3. **Confidence Indicators**: Show AI confidence levels
4. **Detailed Explanations**: Expandable score breakdowns
5. **Theme Support**: Dark mode tooltip variants