# Activation Manager API Documentation

## Base URL
- Production: `https://tobermory.ai/api`
- Development: `http://localhost:8080/api`

## Authentication
Currently using session-based authentication with password protection. API endpoints are accessible after initial authentication.

## Endpoints

### Variable Picker API

#### 1. Start Variable Search Session
```http
POST /api/variable-picker/start
```

**Request Body:**
```json
{
  "query": "young affluent millennials",
  "top_k": 30
}
```

**Response:**
```json
{
  "session_id": "vp-69aca9b5",
  "query": "young affluent millennials",
  "suggested_count": 30,
  "variables": [
    {
      "code": "PRIZM01",
      "description": "Elite Estates",
      "category": "Demographics",
      "type": "demographic",
      "score": 95.5,
      "search_method": "semantic"
    }
  ],
  "status": "active",
  "embeddings_ready": true
}
```

#### 2. Refine Search
```http
POST /api/variable-picker/refine/{session_id}
```

**Request Body:**
```json
{
  "refinement": "who shop online frequently",
  "exclude_codes": ["PRIZM01", "PRIZM02"],
  "original_query": "young affluent millennials"
}
```

**Response:** Same format as start session

#### 3. Confirm Variables
```http
POST /api/variable-picker/confirm/{session_id}
```

**Request Body:**
```json
{
  "confirmed_codes": ["PRIZM01", "PRIZM03", "PRIZM05"],
  "all_variables": [/* array of variable objects */]
}
```

**Response:**
```json
{
  "session_id": "vp-69aca9b5",
  "confirmed_variables": [/* filtered variable objects */],
  "status": "confirmed"
}
```

#### 4. Export Variables
```http
POST /api/variable-picker/export/{session_id}?format=json
```

**Query Parameters:**
- `format`: `json` or `csv`

**Request Body:**
```json
{
  "confirmed_variables": [/* array of variable objects */],
  "query": "original search query"
}
```

**Response:**
- JSON format: Returns JSON object with variables
- CSV format: Returns CSV file download

### Natural Language Processing API

#### 1. Start NL Session
```http
POST /api/start_session
```

**Response:**
```json
{
  "session_id": "nl-abc123",
  "status": "active"
}
```

#### 2. Process Natural Language
```http
POST /api/nl/process
```

**Request Body:**
```json
{
  "session_id": "nl-abc123",
  "action": "process",
  "payload": {
    "input": "Find me young families interested in organic products"
  }
}
```

**Response:**
```json
{
  "status": "variables_suggested",
  "suggested_variables": {
    "demographic": [...],
    "behavioral": [...],
    "psychographic": [...],
    "geographic": [...],
    "technographic": [...]
  },
  "message": "Found 45 relevant variables"
}
```

#### 3. Confirm Audience
```http
POST /api/nl/process
```

**Request Body:**
```json
{
  "session_id": "nl-abc123",
  "action": "confirm",
  "payload": {
    "selected_variables": [/* array of selected variables */]
  }
}
```

### Health & Status API

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-05-29T08:00:00Z"
}
```

#### Embeddings Status
```http
GET /api/embeddings-status
```

**Response:**
```json
{
  "status": "ready",
  "method": "gcs",
  "message": "Embeddings available",
  "variable_count": 49323
}
```

## Variable Object Schema

```typescript
interface Variable {
  code: string;           // Unique variable identifier
  description: string;    // Human-readable description
  category: string;       // Main category
  type: string;          // Variable type (demographic, behavioral, etc.)
  score?: number;        // Relevance score (0-100)
  search_method?: string; // How it was found (semantic/keyword)
  theme?: string;        // Additional categorization
  context?: string;      // Additional context
}
```

### Enhanced Variable Picker API

#### Enhanced Variable Search
```http
POST /api/enhanced-variable-picker/search
```

**Description:** Advanced semantic search for variables with concept understanding and similarity filtering

**Request Body:**
```json
{
  "query": "high income millennials",
  "top_k": 50,
  "use_semantic": true,
  "use_keyword": true,
  "use_advanced_processing": true,
  "filter_similar": false,
  "similarity_threshold": 0.85,
  "max_similar_per_group": 2
}
```

**Parameters:**
- `query` (string, required): Natural language search query
- `top_k` (integer, default: 50): Maximum number of results to return
- `use_semantic` (boolean, default: true): Enable semantic search
- `use_keyword` (boolean, default: true): Enable keyword search
- `use_advanced_processing` (boolean, default: true): Enable advanced query processing
- `filter_similar` (boolean, default: false): Enable similarity filtering to reduce redundant results
- `similarity_threshold` (float, default: 0.85): Minimum Jaro-Winkler similarity score to consider variables as similar (0-1)
- `max_similar_per_group` (integer, default: 2): Maximum number of similar variables to keep per group

**Response:**
```json
{
  "results": [
    {
      "code": "INC_100K_PLUS",
      "name": "Income $100K+",
      "description": "Household income $100,000 or more",
      "category": "Financial",
      "score": 0.92,
      "matched_concepts": ["high income", "financial"],
      "relevance_explanation": "Matches financial profile: high income"
    }
  ],
  "total_found": 25,
  "query_interpretation": {
    "concepts": ["high income", "millennials"],
    "expanded_terms": ["affluent", "wealthy", "age 25-40"]
  }
}
```

**Note:** When `filter_similar` is enabled, the system uses Jaro-Winkler similarity to identify and group similar variables based on their descriptions. Only the top-scoring variables from each similarity group are returned, reducing redundancy in the results.

#### Get Variable Statistics
```http
GET /api/enhanced-variable-picker/stats
```

**Response:**
```json
{
  "total_variables": 5000,
  "themes": {"Demographics": 1200, "Financial": 800, ...},
  "products": {"PRIZM": 68, "ConneXions": 120, ...},
  "domains": {"Household": 1500, "Individual": 3500},
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

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": "Error message",
  "details": "Additional error details"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting
- No explicit rate limiting in current implementation
- Google App Engine automatic scaling handles load

## Notes
- All endpoints are CORS-enabled
- Sessions are ephemeral in production (stateless design)
- Variable search uses both keyword and semantic matching
- Export functionality supports both JSON and CSV formats