# Enhanced Audience API Documentation

## Overview

The Enhanced Audience API extends the existing audience management endpoints to support enhanced audience features including generated names, natural language descriptions, contextual insights, and visual elements.

## Enhanced Data Fields

### Audience Object (Extended)

```typescript
interface EnhancedAudience {
  // Existing fields
  audience_id: string;
  user_id: string;
  name: string;
  description: string;
  data_type: string;
  selected_variables: string[];
  segments: Segment[];
  total_audience_size: number;
  status: string;
  created_at: string;
  metadata: object;
  
  // Enhanced fields (v1.7.0+)
  enhanced_name?: string;           // Generated smart name
  natural_language_criteria?: string; // Readable criteria description
  audience_size?: number;           // Demo audience size
  insights?: string[];              // Contextual insights
  original_query?: string;          // Original user query for icon selection
}
```

## API Endpoints

### Save Enhanced Audience

**POST** `/api/audiences`

Save a new audience with enhanced fields.

#### Request Body
```json
{
  "user_id": "demo_user",
  "name": "Audience - 05/29/2025",
  "enhanced_name": "Gaming-Enthusiast Gen Z Males",
  "description": "Find males aged 18-24 interested in gaming consoles",
  "natural_language_criteria": "Males between the ages of 18 and 24 who are interested in video games",
  "audience_size": 67842,
  "insights": [
    "Focused audience of 68K+ targeted users",
    "Technology-savvy consumers",
    "Digital-native generation"
  ],
  "data_type": "first_party",
  "original_query": "Find males aged 18-24 interested in gaming consoles",
  "selected_variables": ["gaming_interest", "age_min", "age_max", "gender"],
  "variable_details": [
    {
      "code": "gaming_interest",
      "description": "Gaming Interest Level",
      "relevance_score": 0.95,
      "type": "interest",
      "category": "Entertainment"
    }
  ],
  "segments": [
    {
      "segment_id": 1,
      "name": "Core Gaming Segment",
      "size": 45000,
      "size_percentage": 66.3,
      "characteristics": {"primary_interest": "console_gaming"},
      "prizm_segments": ["Young & Restless", "Shotguns & Pickups"]
    }
  ],
  "total_audience_size": 67842,
  "status": "active",
  "metadata": {
    "created_from": "nl_audience_builder",
    "session_id": "session_123"
  }
}
```

#### Response
```json
{
  "success": true,
  "audience_id": "aud_67842_20250529",
  "message": "Audience saved successfully",
  "enhanced_data": {
    "generated_name": "Gaming-Enthusiast Gen Z Males",
    "natural_criteria": "Males between the ages of 18 and 24 who are interested in video games",
    "demo_size": 67842,
    "insights_count": 3
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "enhanced_name": "Must be a non-empty string",
    "audience_size": "Must be a positive integer"
  }
}
```

### Get Enhanced Audiences

**GET** `/api/audiences?user_id=demo_user`

Retrieve all audiences for a user, including enhanced fields.

#### Response
```json
{
  "success": true,
  "audiences": [
    {
      "audience_id": "aud_001",
      "user_id": "demo_user",
      "name": "Audience - 05/29/2025",
      "enhanced_name": "Gaming-Enthusiast Gen Z Males",
      "description": "Find males aged 18-24 interested in gaming",
      "natural_language_criteria": "Males between the ages of 18 and 24 who are interested in video games",
      "audience_size": 67842,
      "total_audience_size": 67842,
      "insights": [
        "Focused audience of 68K+ targeted users",
        "Technology-savvy consumers"
      ],
      "original_query": "Find males aged 18-24 interested in gaming consoles",
      "segments": [
        {
          "segment_id": 1,
          "name": "Core Gaming Segment"
        }
      ],
      "created_at": "2025-05-29T10:30:00Z",
      "status": "active"
    },
    {
      // Legacy audience without enhanced fields
      "audience_id": "aud_legacy",
      "user_id": "demo_user",
      "name": "Health Conscious Consumers",
      "description": "People interested in health and wellness products",
      "total_audience_size": 56798,
      "segments": [
        {
          "segment_id": 1,
          "name": "Fitness Enthusiasts"
        }
      ],
      "created_at": "2025-05-28T14:20:00Z",
      "status": "active"
    }
  ],
  "metadata": {
    "total_count": 2,
    "enhanced_count": 1,
    "legacy_count": 1
  }
}
```

## Client-Side Integration

### Generating Enhanced Data

The enhanced audience data is generated client-side using utility functions:

```typescript
import {
  generateAudienceName,
  formatCriteriaNaturalLanguage,
  generateRandomAudienceSize,
  generateAudienceInsights
} from '../utils/audienceUtils';

// Generate enhanced data before saving
const enhancedName = generateAudienceName(originalUserQuery);
const naturalLanguage = formatCriteriaNaturalLanguage(
  originalUserQuery,
  Array.from(selectedVariables),
  variableDetails
);
const randomSize = generateRandomAudienceSize();
const insights = generateAudienceInsights(originalUserQuery, randomSize);
```

### Displaying Enhanced Data

When displaying audiences, the system gracefully handles both enhanced and legacy data:

```typescript
import { getAudienceIcon, getAudienceIconColor } from '../utils/audienceUtils';

// Display logic with fallbacks
const Icon = getAudienceIcon(audience.original_query || audience.description || '');
const iconColor = getAudienceIconColor(audience.original_query || audience.description || '');
const displaySize = audience.audience_size || audience.total_audience_size || 0;
const displayName = audience.enhanced_name || audience.name;
const displayCriteria = audience.natural_language_criteria || 
                       audience.description || 
                       'Custom audience based on selected criteria';
```

## Enhanced Features API

### Icon Selection API

**GET** `/api/audience-utils/icon?query={query}`

Get recommended icon for audience based on query (optional endpoint for server-side icon selection).

#### Parameters
- `query` (string): The audience query or description

#### Response
```json
{
  "success": true,
  "icon": "Gamepad2",
  "color": "#8B5CF6",
  "category": "gaming"
}
```

### Name Generation API

**POST** `/api/audience-utils/generate-name`

Generate audience name from query (optional endpoint for server-side generation).

#### Request Body
```json
{
  "query": "Find males aged 18-24 interested in gaming consoles",
  "variables": ["gaming_interest", "age_range", "gender"],
  "demographics": {
    "age_range": "18-24",
    "gender": "male",
    "interests": ["gaming"]
  }
}
```

#### Response
```json
{
  "success": true,
  "generated_name": "Gaming-Enthusiast Gen Z Males",
  "components": ["Gaming-Enthusiast", "Gen Z", "Males"],
  "confidence": 0.95
}
```

## Validation Rules

### Enhanced Name
- **Type**: String
- **Length**: 1-100 characters
- **Pattern**: Letters, numbers, spaces, hyphens allowed
- **Fallback**: "Custom Audience Segment"

### Natural Language Criteria
- **Type**: String
- **Length**: 1-500 characters
- **Required**: Must be readable sentence format
- **Fallback**: Original description or "Custom audience based on selected criteria"

### Audience Size
- **Type**: Integer
- **Range**: 1-10,000,000
- **Demo Range**: 56,798-89,380 (recommended for demos)
- **Format**: Displayed with comma separators

### Insights
- **Type**: Array of strings
- **Length**: 0-10 insights
- **Item Length**: 1-200 characters per insight
- **Display**: Show first 2 insights in cards

## Error Handling

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `INVALID_ENHANCED_NAME` | Generated name validation failed | Check name generation logic |
| `MISSING_ORIGINAL_QUERY` | No query provided for enhancement | Provide original user query |
| `INVALID_AUDIENCE_SIZE` | Size out of valid range | Use generateRandomAudienceSize() |
| `INSIGHTS_FORMAT_ERROR` | Insights not in array format | Ensure insights is string array |
| `ICON_SELECTION_FAILED` | Unable to determine appropriate icon | Falls back to Users icon |

### Error Response Format
```json
{
  "success": false,
  "error": "INVALID_ENHANCED_NAME",
  "message": "Generated audience name exceeds maximum length",
  "field": "enhanced_name",
  "provided_value": "VeryLongAudienceNameThatExceedsTheMaximumAllowedLength...",
  "expected_format": "String with 1-100 characters",
  "suggestion": "Use generateAudienceName() utility function"
}
```

## Migration Guide

### From v1.6.0 to v1.7.0

#### Backward Compatibility
- **No breaking changes** - all existing endpoints work unchanged
- **Enhanced fields are optional** - legacy save format still supported
- **Graceful degradation** - missing enhanced fields use fallbacks

#### Updating Save Calls
```typescript
// Before (v1.6.0)
const audienceData = {
  name: "My Audience",
  description: "Technical description",
  // ... other fields
};

// After (v1.7.0) - Enhanced
const audienceData = {
  name: "My Audience",
  enhanced_name: generateAudienceName(query),
  description: "Technical description", 
  natural_language_criteria: formatCriteriaNaturalLanguage(query),
  audience_size: generateRandomAudienceSize(),
  insights: generateAudienceInsights(query, size),
  original_query: query,
  // ... other fields
};
```

#### Updating Display Logic
```typescript
// Before (v1.6.0)
<h3>{audience.name}</h3>
<p>{audience.description}</p>
<span>{audience.total_audience_size} people</span>

// After (v1.7.0) - Enhanced with fallbacks
<h3>{audience.enhanced_name || audience.name}</h3>
<p>{audience.natural_language_criteria || audience.description}</p>
<span>{(audience.audience_size || audience.total_audience_size || 0).toLocaleString()} people</span>
```

## Performance Considerations

### Client-Side Generation
- **Fast execution**: All utility functions execute in <1ms
- **No API calls**: Generation happens client-side
- **Memory efficient**: Functions are stateless and cleanup properly
- **Bundle size**: ~10KB additional JavaScript

### Server-Side Storage
- **Minimal overhead**: Enhanced fields add ~1KB per audience
- **Optional fields**: No schema changes required
- **Indexing**: Consider indexing enhanced_name for search
- **Backward compatibility**: Existing queries unchanged

## Security & Privacy

### Data Protection
- **Demo sizes only**: No real audience data exposed
- **Client-side generation**: No sensitive data sent to servers for enhancement
- **Input validation**: All enhanced fields validated before storage
- **XSS prevention**: Proper escaping in display components

### API Security
- **Authentication**: Same authentication as existing audience endpoints
- **Authorization**: User can only access their own audiences
- **Rate limiting**: Standard rate limits apply
- **Input sanitization**: All text fields sanitized before processing

---

**API Version**: 1.7.0  
**Last Updated**: 2025-05-29  
**Compatibility**: Backward compatible with v1.5.0+