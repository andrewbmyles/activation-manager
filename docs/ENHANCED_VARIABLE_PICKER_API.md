# Enhanced Variable Picker API Documentation

## Overview

The Enhanced Variable Picker API provides advanced semantic search capabilities for finding relevant variables from large datasets. It integrates with the Natural Language Multi-Variate Audience Builder to enable intuitive variable selection using natural language queries.

## Architecture

### Data Flow
```
User Query → Enhanced Variable Picker API → Semantic Search Engine
                                          ↓
                                    Variable Database
                                   (Parquet/CSV/Cache)
                                          ↓
                                    Ranked Results
```

### Components

1. **EnhancedVariablePickerAPI**: Main API class handling search requests
2. **EnhancedSemanticSearch**: Core search engine with semantic capabilities
3. **Data Loaders**: 
   - EnhancedParquetLoader (primary)
   - CSVVariableLoader (fallback)
   - VariableSelector (cache)

## API Endpoints

### 1. Variable Search

**Endpoint:** `POST /api/enhanced-variable-picker/search`

**Description:** Search for variables using natural language with semantic understanding.

**Request:**
```python
{
    "query": str,           # Required: Natural language search query
    "top_k": int,          # Optional: Number of results (default: 50)
    "use_semantic": bool,  # Optional: Enable semantic search (default: true)
    "use_keyword": bool,   # Optional: Enable keyword search (default: true)
    "filters": dict       # Optional: Additional filters
}
```

**Response:**
```python
{
    "results": [
        {
            "code": str,              # Variable identifier
            "name": str,              # Human-readable name
            "description": str,       # Detailed description
            "score": float,          # Relevance score (0-1)
            "category": str,         # Variable category
            "dataType": str,         # Data type
            "search_method": str,    # How it was found (semantic/keyword)
            "keywords": [str]        # Matched keywords
        }
    ],
    "total_found": int,              # Total matching variables
    "query_context": {
        "original_query": str,       # User's original query
        "processed_query": str,      # Processed/expanded query
        "search_time_ms": float      # Search duration
    },
    "search_methods": {
        "semantic": bool,            # Whether semantic search was used
        "keyword": bool              # Whether keyword search was used
    }
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "young affluent millennials who shop online",
    "top_k": 20,
    "use_semantic": true,
    "use_keyword": true
  }'
```

### 2. Variable Statistics

**Endpoint:** `GET /api/enhanced-variable-picker/stats`

**Description:** Get statistics about the loaded variable database.

**Response:**
```python
{
    "total_variables": int,          # Total number of variables
    "themes": {                      # Variable count by theme
        "Demographics": int,
        "Behavior": int,
        "Lifestyle": int
    },
    "products": {                    # Variable count by product
        "DaaS": int,
        "Custom": int
    },
    "domains": {                     # Variable count by domain
        "Individual": int,
        "Household": int
    },
    "has_embeddings": bool,          # Whether semantic search is available
    "search_config": {
        "default_top_k": int,        # Default result count
        "hybrid_weights": {
            "semantic": float,       # Semantic search weight
            "keyword": float         # Keyword search weight
        }
    }
}
```

### 3. Get Variable by ID

**Endpoint:** `GET /api/enhanced-variable-picker/variable/<var_id>`

**Description:** Retrieve detailed information about a specific variable.

**Response:**
```python
{
    "code": str,
    "name": str,
    "description": str,
    "category": str,
    "dataType": str,
    "theme": str,
    "product": str,
    "domain": str,
    "metadata": dict         # Additional variable-specific metadata
}
```

### 4. Search by Category

**Endpoint:** `GET /api/enhanced-variable-picker/category/<category>`

**Description:** Find all variables in a specific category.

**Query Parameters:**
- `top_k`: Maximum number of results (default: 50)

**Response:**
```python
{
    "category": str,
    "results": [Variable],
    "count": int
}
```

## Implementation Details

### Initialization Process

```python
class EnhancedVariablePickerAPI:
    def __init__(self, openai_api_key: Optional[str] = None):
        # Priority order for data loading:
        # 1. Try Parquet (fastest)
        # 2. Try VariableSelector (cached)
        # 3. Fallback to CSV (slowest)
```

### Search Algorithm

1. **Query Processing**
   - Tokenization and normalization
   - Synonym expansion
   - Intent detection

2. **Hybrid Search**
   - **Semantic Search**: Uses embeddings for meaning-based matching
   - **Keyword Search**: Traditional text matching with fuzzy logic
   - **Score Fusion**: Weighted combination of both methods

3. **Ranking**
   - Relevance scoring (0-1 scale)
   - Category boosting for matched intents
   - Result deduplication

### Data Sources

#### Parquet Format (Recommended)
```python
# Expected schema
{
    'VarId': str,           # Unique identifier
    'Description': str,     # Full description
    'Category': str,        # High-level category
    'DataType': str,        # Variable data type
    'Product': str,         # Product source
    'Theme': str,           # Thematic grouping
    'Domain': str           # Individual/Household
}
```

#### CSV Format (Fallback)
```csv
VarId,Description,Category,DataType,Product,Theme,Domain
AGE_18_24,"Age 18-24",Demographics,Numeric,DaaS,Age,Individual
```

## Integration Examples

### Python Client
```python
import requests

class VariablePickerClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def search(self, query, top_k=50):
        response = requests.post(
            f"{self.base_url}/api/enhanced-variable-picker/search",
            json={
                "query": query,
                "top_k": top_k,
                "use_semantic": True,
                "use_keyword": True
            }
        )
        return response.json()

# Usage
client = VariablePickerClient()
results = client.search("high income urban professionals")
for var in results['results'][:5]:
    print(f"{var['code']}: {var['name']} (score: {var['score']:.2f})")
```

### JavaScript/React Integration
```javascript
const searchVariables = async (query) => {
  const response = await fetch('/api/enhanced-variable-picker/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      top_k: 50,
      use_semantic: true,
      use_keyword: true
    })
  });
  
  if (!response.ok) {
    throw new Error('Variable search failed');
  }
  
  return response.json();
};

// Usage in React component
const [variables, setVariables] = useState([]);

const handleSearch = async (query) => {
  try {
    const results = await searchVariables(query);
    setVariables(results.results);
  } catch (error) {
    console.error('Search error:', error);
  }
};
```

## Performance Considerations

### Caching
- Variable metadata is cached in memory on first load
- Embeddings are loaded asynchronously to avoid blocking
- Search results can be cached client-side

### Optimization Tips
1. **Use Parquet files** for fastest loading (10x faster than CSV)
2. **Pre-load embeddings** during app initialization
3. **Batch requests** when searching for multiple criteria
4. **Set appropriate top_k** to limit result processing

### Benchmarks
- Parquet loading: ~500ms for 15,000 variables
- CSV loading: ~5-10s for 15,000 variables
- Semantic search: ~50-100ms per query
- Keyword search: ~10-20ms per query

## Error Handling

### Common Errors

1. **No Search Engine Initialized**
   ```json
   {
     "results": [],
     "total_found": 0,
     "error": "Search not initialized"
   }
   ```
   **Solution:** Check data source availability

2. **Invalid Query**
   ```json
   {
     "error": "Query is required"
   }
   ```
   **Solution:** Provide non-empty query string

3. **Data Source Unavailable**
   - API will attempt fallback options automatically
   - Check logs for specific failure reasons

### Logging
Enable debug logging:
```python
import logging
logging.getLogger('activation_manager.api.enhanced_variable_picker_api').setLevel(logging.DEBUG)
```

## Security Considerations

1. **API Key Protection**
   - Store OpenAI API key in environment variables
   - Never expose keys in client-side code

2. **Input Validation**
   - Queries are sanitized before processing
   - Maximum query length: 500 characters
   - Special characters are escaped

3. **Rate Limiting**
   - Implement rate limiting in production
   - Consider caching frequent queries

## Migration Guide

### From Variable Picker to Enhanced API

**Old endpoint:**
```
POST /api/variable-picker/start
{
  "query": "millennials",
  "top_k": 30
}
```

**New endpoint:**
```
POST /api/enhanced-variable-picker/search
{
  "query": "millennials",
  "top_k": 50,
  "use_semantic": true,
  "use_keyword": true
}
```

**Key differences:**
- Increased default top_k (30 → 50)
- Explicit search method control
- Richer response metadata
- Better relevance scoring

## Deployment

### Environment Variables
```bash
# Required for semantic search
export OPENAI_API_KEY="your-api-key"

# Optional: GCS for embeddings
export GCS_BUCKET="activation-manager-embeddings"

# Optional: Custom data paths
export PARQUET_PATH="/path/to/variables.parquet"
export CSV_PATH="/path/to/variables.csv"
```

### Docker Deployment
```dockerfile
FROM python:3.9

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY activation_manager/ /app/activation_manager/
COPY main.py /app/

# Set environment
ENV PYTHONPATH=/app
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Run
CMD ["python", "/app/main.py"]
```

## Support & Debugging

### Debug Checklist
1. ✓ Is the API key set correctly?
2. ✓ Is the data source accessible?
3. ✓ Are embeddings loaded (check /stats endpoint)?
4. ✓ Is the query properly formatted?
5. ✓ Check server logs for detailed errors

### Common Solutions
- **Slow searches**: Pre-load embeddings, use Parquet format
- **Missing results**: Try keyword-only search, check data coverage
- **API errors**: Verify endpoint URLs, check CORS settings

For additional support, refer to the main project documentation or file an issue in the repository.