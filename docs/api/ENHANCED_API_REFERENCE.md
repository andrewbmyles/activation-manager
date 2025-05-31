# Activation Manager API Reference

## Base URL
- **Production**: `https://feisty-catcher-461000-g2.nn.r.appspot.com`
- **Staging**: `https://stg-VERSION-dot-feisty-catcher-461000-g2.nn.r.appspot.com`

## Authentication
Currently, the API does not require authentication. This may change in future versions.

## Endpoints

### 1. Enhanced Variable Search
Search for variables with advanced filtering and semantic capabilities.

**Endpoint**: `POST /api/enhanced-variable-picker/search`

**Request Body**:
```json
{
  "query": "household income",
  "top_k": 50,
  "filter_similar": true,
  "use_semantic": true,
  "use_keyword": true,
  "use_advanced_processing": true,
  "similarity_threshold": 0.75,
  "max_similar_per_group": 2,
  "filters": {
    "category": "demographic",
    "min_score": 0.5
  }
}
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | string | required | Search query text |
| top_k | integer | 50 | Maximum results to return |
| filter_similar | boolean | false | Enable similarity filtering |
| use_semantic | boolean | true | Use semantic search |
| use_keyword | boolean | true | Use keyword search |
| use_advanced_processing | boolean | true | Enable advanced query processing |
| similarity_threshold | float | 0.85 | Minimum similarity for filtering (0-1) |
| max_similar_per_group | integer | 2 | Max similar items per group |
| filters | object | null | Additional filters |

**Response**:
```json
{
  "results": [
    {
      "code": "HHI_100K_125K",
      "description": "Household Income $100,000 To $124,999",
      "category": "demographic",
      "theme": "income",
      "score": 0.95,
      "matched_concepts": [
        {
          "concept": "income",
          "type": "financial",
          "confidence": 0.9
        }
      ]
    }
  ],
  "total_found": 25,
  "query_context": {
    "original_query": "household income",
    "expanded_terms": ["household", "income", "earnings", "salary"]
  },
  "search_methods": {
    "keyword": true,
    "semantic": true
  },
  "fallback_mode": false,
  "advanced_context": {
    "concepts": [...],
    "query_interpretation": "User is looking for income-related variables"
  }
}
```

**Status Codes**:
- `200 OK`: Successful search
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

**Example**:
```bash
curl -X POST https://api.example.com/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "millennials with high income",
    "filter_similar": true,
    "top_k": 20
  }'
```

### 2. Variable Statistics
Get statistics about available variables.

**Endpoint**: `GET /api/enhanced-variable-picker/stats`

**Response**:
```json
{
  "total_variables": 49323,
  "themes": {
    "demographic": 15234,
    "financial": 8932,
    "behavioral": 12456,
    "geographic": 12701
  },
  "products": {
    "ENVISION": 23456,
    "SPOTLIGHT": 25867
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

### 3. Get Variable by ID
Retrieve detailed information about a specific variable.

**Endpoint**: `GET /api/enhanced-variable-picker/variable/{var_id}`

**Parameters**:
- `var_id`: Variable identifier (in URL path)

**Response**:
```json
{
  "code": "HHI_100K_125K",
  "description": "Household Income $100,000 To $124,999",
  "category": "demographic",
  "theme": "income",
  "product": "ENVISION",
  "year": 2024,
  "keywords": ["income", "household", "high-income"],
  "metadata": {
    "source": "Census",
    "confidence": "high"
  }
}
```

### 4. Search by Category
Search variables within a specific category.

**Endpoint**: `GET /api/enhanced-variable-picker/category/{category}`

**Parameters**:
- `category`: Category name (in URL path)
- `top_k`: Maximum results (query parameter, default: 50)

**Response**:
```json
{
  "category": "demographic",
  "results": [...],
  "count": 25
}
```

### 5. Concept Suggestions
Get concept-based variable suggestions for complex queries.

**Endpoint**: `POST /api/enhanced-variable-picker/concepts/suggestions`

**Request Body**:
```json
{
  "query": "young families interested in sustainability"
}
```

**Response**:
```json
{
  "by_concept": {
    "young families": [
      {
        "code": "FAM_YOUNG_CHILDREN",
        "description": "Families with Young Children",
        "match_reason": "Direct match: 'families'"
      }
    ],
    "sustainability": [
      {
        "code": "ENV_CONSCIOUS",
        "description": "Environmentally Conscious",
        "match_reason": "Synonym match: 'environmental'"
      }
    ]
  },
  "combinations": [
    {
      "code": "GREEN_FAMILIES",
      "description": "Eco-conscious Families",
      "matched_concepts": ["families", "sustainability"],
      "match_count": 2
    }
  ],
  "missing_concepts": []
}
```

### 6. Health Check
Simple endpoint to verify API availability.

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-05-30T20:15:30.123Z",
  "version": "2.0.0",
  "services": {
    "database": "connected",
    "search_engine": "ready"
  }
}
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "details": "Additional context about the error",
  "code": "ERROR_CODE",
  "timestamp": "2025-05-30T20:15:30.123Z"
}
```

**Common Error Codes**:
- `INVALID_QUERY`: Query parameter is missing or invalid
- `SEARCH_FAILED`: Search execution failed
- `NOT_FOUND`: Requested resource not found
- `INTERNAL_ERROR`: Unexpected server error

## Rate Limiting
Currently no rate limiting is implemented. This may change in future versions.

## Filtering Algorithm

The similarity filtering uses the Jaro-Winkler algorithm to identify and reduce duplicate results:

1. **Base Pattern Extraction**: Groups variables by their base pattern (text before first hyphen)
2. **Similarity Calculation**: Uses Jaro-Winkler to compute similarity between descriptions
3. **Representative Selection**: Keeps only the most relevant representatives per group

**Example**:
```
Input (50 results):
- Contact with friends - Similar income - All
- Contact with friends - Similar income - Most
- Contact with friends - Similar income - Some
...

Output with filtering (2 results):
- Contact with friends - Similar income - All
- Contact with friends - Different income - Higher
```

## Performance Considerations

- **Search Latency**: Average 50-100ms for 50k variables
- **Filtering Impact**: Adds ~20ms to search time
- **Caching**: Results are cached for 15 minutes
- **Concurrent Requests**: Supports 1000+ concurrent users

## Migration from Old API

If migrating from the old `/api/variables/search` endpoint:

**Old**:
```json
{
  "search_term": "income",
  "limit": 30
}
```

**New**:
```json
{
  "query": "income",
  "top_k": 30,
  "filter_similar": true
}
```

Key differences:
- `search_term` → `query`
- `limit` → `top_k`
- New filtering options available
- Richer response format

## Examples

### Example 1: Basic Search
```bash
curl -X POST https://api.example.com/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{"query": "income", "top_k": 10}'
```

### Example 2: Advanced Search with Filtering
```bash
curl -X POST https://api.example.com/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contact with friends",
    "top_k": 50,
    "filter_similar": true,
    "similarity_threshold": 0.75,
    "max_similar_per_group": 2
  }'
```

### Example 3: Category-specific Search
```bash
curl -X GET https://api.example.com/api/enhanced-variable-picker/category/demographic?top_k=20
```

## Changelog

### v2.0.0 (2025-05-30)
- Added similarity filtering to reduce duplicate results
- Implemented fallback filtering for robustness
- Enhanced search with 50-result capability
- Added concept-based suggestions

### v1.0.0 (2025-05-01)
- Initial API release
- Basic search functionality
- Category filtering