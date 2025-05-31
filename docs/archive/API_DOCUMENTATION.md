# Enhanced Variable Picker API Documentation

## Overview
The Enhanced Variable Picker API provides semantic search capabilities for demographic and behavioral variables, supporting the audience refinement workflow with AI-powered suggestions and real-time search.

## Base URL
```
Production: https://your-domain.com/api
Staging: https://staging-domain.com/api
Development: http://localhost:8000/api
```

## Authentication
All API endpoints require authentication via user_id parameter or session token.

```bash
# Using user_id parameter
GET /api/audiences/123?user_id=demo_user

# Using session token (if implemented)
Authorization: Bearer <token>
```

## Core Endpoints

### 1. Search Variables

#### Enhanced Semantic Search
```http
POST /api/enhanced-variable-picker/search
Content-Type: application/json

{
  "query": "high income urban millennials",
  "top_k": 10,
  "use_semantic": true,
  "use_keyword": true,
  "use_advanced_processing": true,
  "filters": {
    "category": "demographic",
    "domain": "lifestyle"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "code": "HIGH_INCOME_URBAN",
      "description": "High income urban professionals",
      "score": 0.95,
      "category": "demographic",
      "domain": "income",
      "theme": "socioeconomic",
      "product": "lifestyle_targeting"
    }
  ],
  "total_found": 47,
  "query_context": {
    "original_query": "high income urban millennials",
    "processed_query": "high income urban millennial professional",
    "semantic_concepts": ["income", "geography", "generation"]
  },
  "search_methods": {
    "semantic": true,
    "keyword": true,
    "hybrid_score": true
  },
  "query_optimization": {
    "concepts": [
      {
        "concept": "high_income",
        "confidence": 0.92,
        "related_variables": ["INCOME_75K_PLUS", "AFFLUENT_LIFESTYLE"]
      }
    ],
    "suggested_refinements": ["urban professionals", "tech workers"],
    "alternative_queries": ["affluent millennials in cities"]
  }
}
```

#### Variable by ID
```http
GET /api/enhanced-variable-picker/variable/{var_id}
```

**Response:**
```json
{
  "code": "HIGH_INCOME_URBAN",
  "description": "High income urban professionals with household income >$75K living in metropolitan areas",
  "category": "demographic", 
  "domain": "income_geography",
  "theme": "socioeconomic_location",
  "product": "lifestyle_targeting",
  "data_type": "boolean",
  "coverage": "85%",
  "last_updated": "2024-01-15",
  "related_variables": ["URBAN_PROFESSIONAL", "HIGH_INCOME", "METRO_RESIDENT"]
}
```

#### Search by Category
```http
GET /api/enhanced-variable-picker/category/{category}?top_k=50
```

**Response:**
```json
{
  "category": "demographic",
  "results": [
    {
      "code": "AGE_25_34",
      "description": "Adults aged 25-34",
      "score": null,
      "category": "demographic",
      "domain": "age"
    }
  ],
  "count": 23
}
```

#### Get Variable Statistics
```http
GET /api/enhanced-variable-picker/stats
```

**Response:**
```json
{
  "total_variables": 1247,
  "themes": {
    "demographic": 156,
    "behavioral": 234, 
    "psychographic": 189,
    "geographic": 98
  },
  "products": {
    "lifestyle_targeting": 445,
    "purchase_intent": 267,
    "digital_behavior": 189
  },
  "domains": {
    "age": 67,
    "income": 45,
    "interests": 234
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

#### Get Concept Suggestions
```http
POST /api/enhanced-variable-picker/concepts/suggestions
Content-Type: application/json

{
  "query": "environmentally conscious urban professionals"
}
```

**Response:**
```json
{
  "concepts": [
    {
      "concept": "environmental_consciousness",
      "confidence": 0.89,
      "variables": [
        {
          "code": "ECO_CONSCIOUS",
          "description": "Environmentally conscious consumers",
          "relevance": 0.95
        }
      ]
    }
  ],
  "semantic_expansion": {
    "synonyms": ["eco-friendly", "sustainable", "green"],
    "related_concepts": ["climate_awareness", "organic_preference"],
    "suggested_combinations": [
      "eco_conscious + urban + professional",
      "sustainable_lifestyle + high_income"
    ]
  },
  "query_refinements": [
    "eco-conscious urban professionals with high income",
    "sustainable lifestyle urban millennials"
  ]
}
```

### 2. Audience Management

#### Get Audience Details
```http
GET /api/audiences/{audience_id}?user_id={user_id}
```

**Response:**
```json
{
  "success": true,
  "audience": {
    "audience_id": "aud_123456",
    "name": "Gaming Enthusiasts Q4",
    "enhanced_name": "Gaming-Enthusiast Gen Z Males",
    "description": "Find males aged 18-24 interested in gaming",
    "natural_language_criteria": "Males between ages 18-24 who are interested in video games",
    "audience_size": 67842,
    "total_audience_size": 67842,
    "selected_variables": ["AGE_18_24", "GENDER_MALE", "GAMING_INTEREST"],
    "variable_details": [
      {
        "code": "GAMING_INTEREST",
        "description": "Gaming Interest Level", 
        "relevance_score": 0.95
      }
    ],
    "segments": [
      {
        "segment_id": "seg_1", 
        "name": "Console Gamers",
        "size": 34521
      }
    ],
    "insights": [
      "Focused audience of 68K+ targeted users",
      "Digital-native generation",
      "High engagement with gaming content"
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T14:22:00Z",
    "status": "active",
    "data_type": "synthetic"
  }
}
```

#### List User Audiences
```http
GET /api/audiences?user_id={user_id}&status=active&limit=20&offset=0
```

**Response:**
```json
{
  "success": true,
  "audiences": [
    {
      "audience_id": "aud_123456",
      "name": "Gaming Enthusiasts Q4",
      "enhanced_name": "Gaming-Enthusiast Gen Z Males",
      "audience_size": 67842,
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 156,
  "has_more": true,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total_pages": 8
  }
}
```

#### Update Audience Status
```http
PUT /api/audiences/{audience_id}/status
Content-Type: application/json

{
  "user_id": "demo_user",
  "status": "archived"
}
```

**Response:**
```json
{
  "success": true,
  "audience_id": "aud_123456",
  "status": "archived",
  "updated_at": "2024-01-15T16:45:00Z"
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": true,
  "error_code": "INVALID_QUERY",
  "message": "Query parameter is required and cannot be empty",
  "details": {
    "parameter": "query",
    "received": "",
    "expected": "non-empty string"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123"
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_QUERY` | 400 | Query parameter missing or invalid |
| `SEARCH_FAILED` | 500 | Search service unavailable |
| `AUDIENCE_NOT_FOUND` | 404 | Audience ID not found |
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `RATE_LIMITED` | 429 | Too many requests |
| `VARIABLE_NOT_FOUND` | 404 | Variable ID not found |
| `INVALID_PARAMETERS` | 400 | Request parameters invalid |

## Rate Limiting

### Limits
- **Search Requests**: 100 per minute per user
- **Audience Operations**: 50 per minute per user
- **Variable Lookups**: 200 per minute per user

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642248000
```

### Rate Limit Response
```json
{
  "error": true,
  "error_code": "RATE_LIMITED",
  "message": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

## Query Optimization

### Advanced Processing
When `use_advanced_processing: true` is enabled:

1. **Concept Extraction**: Identifies semantic concepts in complex queries
2. **Query Expansion**: Adds related terms and synonyms
3. **Re-ranking**: Scores results based on concept relevance
4. **Suggestions**: Provides alternative and refined queries

### Example Advanced Processing
```json
{
  "query": "environmentally conscious millennials with high disposable income",
  "use_advanced_processing": true
}
```

**Enhanced Response:**
```json
{
  "results": [...],
  "query_optimization": {
    "extracted_concepts": [
      {
        "concept": "environmental_consciousness", 
        "confidence": 0.91,
        "keywords": ["eco", "sustainable", "green"]
      },
      {
        "concept": "generation_millennial",
        "confidence": 0.94, 
        "keywords": ["millennial", "gen y", "25-40"]
      },
      {
        "concept": "high_income",
        "confidence": 0.87,
        "keywords": ["disposable income", "affluent", "high earning"]
      }
    ],
    "concept_relationships": [
      {
        "from": "environmental_consciousness",
        "to": "high_income", 
        "type": "correlation",
        "strength": 0.73
      }
    ],
    "optimized_query": "eco conscious affluent millennials sustainable lifestyle high income",
    "alternative_queries": [
      "sustainable lifestyle high income millennials",
      "environmentally aware affluent gen y"
    ]
  }
}
```

## SDK Usage Examples

### JavaScript/TypeScript
```typescript
import { EnhancedVariablePickerAPI } from './api/enhanced-variable-picker';

const api = new EnhancedVariablePickerAPI({
  baseUrl: 'https://api.example.com',
  apiKey: 'your-api-key'
});

// Search variables
const results = await api.searchVariables({
  query: 'high income urban professionals',
  topK: 10,
  useAdvancedProcessing: true
});

// Get variable details
const variable = await api.getVariable('HIGH_INCOME_URBAN');

// Get concept suggestions
const suggestions = await api.getConceptSuggestions({
  query: 'eco-conscious millennials'
});
```

### Python
```python
from api.enhanced_variable_picker import EnhancedVariablePickerAPI

api = EnhancedVariablePickerAPI(
    base_url='https://api.example.com',
    api_key='your-api-key'
)

# Search variables
results = api.search_variables(
    query='high income urban professionals',
    top_k=10,
    use_advanced_processing=True
)

# Get variable details  
variable = api.get_variable('HIGH_INCOME_URBAN')
```

### cURL Examples
```bash
# Search variables
curl -X POST "https://api.example.com/api/enhanced-variable-picker/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gaming enthusiasts",
    "top_k": 10,
    "use_semantic": true,
    "use_advanced_processing": true
  }'

# Get audience
curl "https://api.example.com/api/audiences/aud_123456?user_id=demo_user"

# Get variable stats
curl "https://api.example.com/api/enhanced-variable-picker/stats"
```

## Performance Considerations

### Caching
- **Search Results**: Cached for 5 minutes
- **Variable Details**: Cached for 1 hour  
- **Statistics**: Cached for 15 minutes

### Optimization Tips
1. **Use Filters**: Narrow searches with category/domain filters
2. **Limit Results**: Use appropriate `top_k` values (10-50)
3. **Batch Requests**: Combine related operations when possible
4. **Cache Client-Side**: Store frequently accessed variables

### Response Times
- **Simple Search**: < 200ms
- **Advanced Processing**: < 500ms
- **Variable Lookup**: < 100ms
- **Statistics**: < 150ms

## Testing

### Test Endpoints
```bash
# Health check
GET /api/health

# Test search with known query
POST /api/enhanced-variable-picker/search
{
  "query": "test query",
  "top_k": 5
}
```

### Test Data
```json
{
  "test_variables": [
    "TEST_VARIABLE_1",
    "TEST_VARIABLE_2", 
    "TEST_VARIABLE_3"
  ],
  "test_audiences": [
    "test_aud_123",
    "test_aud_456"
  ]
}
```

---

*For API support or to report issues, contact the development team.*