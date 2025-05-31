# Natural Language Multi-Variate Audience Builder

## Overview

The Natural Language Multi-Variate Audience Builder is an advanced AI-powered tool that enables marketers to create sophisticated audience segments using conversational language. This enhanced component provides a seamless interface for building complex multi-variable audiences without requiring technical expertise.

## Key Features

### 1. Natural Language Processing
- Describe your target audience in plain English
- AI automatically identifies relevant variables from your description
- Semantic search ensures high-quality variable matching

### 2. Enhanced UI Scaling
- **Responsive Design**: Optimized for larger screens with dynamic scaling
- **Flexible Layout**: 
  - Workflow sidebar: `w-64` (base) → `lg:w-80` → `xl:w-96`
  - Chat messages: `max-w-2xl` → `lg:max-w-3xl` → `xl:max-w-4xl`
  - Variable list: `max-h-64` → `lg:max-h-96` → `xl:max-h-[32rem]`
- **Adaptive Padding**: Content areas expand on larger displays for better readability

### 3. Unified Data Source Integration
- Uses the same comprehensive variable database as the Variable Picker tool
- Access to 50+ results through enhanced semantic search
- Supports both Parquet (fast) and CSV (fallback) data sources
- Real-time variable search with debounced input

### 4. Multi-Step Workflow
1. **Data Type Selection**: Choose between First Party, Third Party, or Clean Room data
2. **Audience Description**: Describe your target audience in natural language
3. **Variable Selection**: AI suggests relevant variables with relevance scores
4. **Variable Confirmation**: Review and confirm selected variables
5. **Segment Creation**: K-Medians clustering creates balanced segments
6. **Results Review**: Analyze segment characteristics and sizes
7. **Distribution**: Send segments to marketing platforms

## Technical Implementation

### Component Architecture
```typescript
interface Variable {
  code: string;
  description: string;
  type: string;
  relevance_score: number;
  category?: string;
  dataAvailability?: {
    first_party: boolean;
    third_party: boolean;
    clean_room: boolean;
  };
}
```

### API Integration
The component integrates with two API endpoints:
1. **Enhanced Variable Picker API**: `/api/enhanced-variable-picker/search`
   - Primary endpoint for semantic variable search
   - Returns up to 50 results with relevance scores
   - Supports both semantic and keyword search

2. **Original NL Process API**: `/api/nl/process` (fallback)
   - Used when enhanced API is unavailable
   - Maintains backward compatibility

### Enhanced Search Features
```javascript
// Dynamic search with debouncing
const handleDynamicSearch = async () => {
  const response = await fetch('/api/enhanced-variable-picker/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      query: userInput,
      top_k: 50,
      use_semantic: true,
      use_keyword: true
    })
  });
  // Process results...
};
```

## User Guide

### Getting Started
1. Click on "Natural Language Multi-Variate Audience Builder" in the navigation
2. Select your data environment (First Party, Third Party, or Clean Room)
3. Describe your audience in natural language
4. Review and select suggested variables
5. Confirm your selection to create segments
6. Review segment results and distribute to platforms

### Best Practices
- **Be Specific**: More detailed descriptions yield better variable suggestions
- **Review Scores**: Pay attention to relevance scores (0-1 scale)
- **Refine Search**: Use the dynamic search in step 4 to find additional variables
- **Balance Segments**: The system automatically creates 5-10% sized segments for optimal performance

### Example Queries
- "Find environmentally conscious millennials with high disposable income in urban areas"
- "Young professionals interested in sustainable fashion and organic products"
- "High-income families with children who frequently shop online"
- "Tech-savvy seniors interested in travel and leisure activities"

## API Reference

### Enhanced Variable Picker Endpoints

#### POST `/api/enhanced-variable-picker/search`
Search for variables using natural language.

**Request Body:**
```json
{
  "query": "young millennials who shop online",
  "top_k": 50,
  "use_semantic": true,
  "use_keyword": true,
  "filters": {} // Optional
}
```

**Response:**
```json
{
  "results": [
    {
      "code": "AGE_25_34",
      "name": "Age 25-34 (Millennials)",
      "score": 0.95,
      "category": "Demographics",
      "dataType": "demographic"
    }
  ],
  "total_found": 42,
  "query_context": {
    "original_query": "young millennials who shop online"
  },
  "search_methods": {
    "semantic": true,
    "keyword": true
  }
}
```

#### GET `/api/enhanced-variable-picker/stats`
Get statistics about available variables.

**Response:**
```json
{
  "total_variables": 15000,
  "themes": {
    "Demographics": 3000,
    "Behavior": 4500
  },
  "has_embeddings": true,
  "search_config": {
    "default_top_k": 50,
    "hybrid_weights": {
      "semantic": 0.7,
      "keyword": 0.3
    }
  }
}
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for semantic search functionality
- `GCS_BUCKET`: Google Cloud Storage bucket for embeddings (optional)

### Data Sources
The system prioritizes data sources in this order:
1. **Parquet File**: Fastest option, pre-processed data
2. **Variable Selector**: In-memory cache with embeddings
3. **CSV File**: Fallback option, slower but reliable

## Troubleshooting

### Common Issues

1. **"Variable search failed" error**
   - Check if the backend server is running
   - Verify API endpoints are accessible
   - Check browser console for detailed error messages

2. **Slow variable search**
   - The system may be falling back to CSV loading
   - Check if Parquet file is available and accessible
   - Consider pre-loading embeddings for better performance

3. **Missing variables in results**
   - Ensure search query is specific enough
   - Try both semantic and keyword search options
   - Check if data source contains expected variables

### Debug Mode
Enable debug logging in the browser console:
```javascript
localStorage.setItem('DEBUG_NL_BUILDER', 'true');
```

## Performance Optimization

### Caching Strategy
- Variable embeddings are cached in memory after first load
- Search results are debounced (500ms) to reduce API calls
- Pre-selection of top variables reduces user effort

### Scalability
- Handles 15,000+ variables efficiently
- Semantic search scales with embedding quality
- Fallback mechanisms ensure availability

## Future Enhancements

1. **Advanced Filtering**
   - Filter by data availability (1st/3rd party)
   - Category-based filtering
   - Custom relevance thresholds

2. **Saved Searches**
   - Save and reuse successful queries
   - Share audience definitions with team

3. **Export Options**
   - Direct platform integrations
   - Custom export formats
   - Scheduled distributions

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review browser console for errors
- Contact support with session ID and error details