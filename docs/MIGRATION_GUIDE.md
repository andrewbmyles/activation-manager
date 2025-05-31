# Migration Guide: From CSV to Enhanced Semantic Search

## Overview

This guide helps you migrate from the old CSV-based variable search to the new enhanced semantic search system with Parquet storage and improved performance.

## What's Changed

### Data Format
- **Old**: CSV file (15MB, slow loading)
- **New**: Apache Parquet (3MB, 5-10x faster)

### Search Capabilities
- **Old**: Basic keyword search, 10-20 results
- **New**: Hybrid keyword + semantic search, 50+ results

### API Endpoints
- **Old**: `/api/variable_picker/search`
- **New**: `/api/enhanced-variable-picker/search`

## Migration Steps

### Step 1: Convert CSV to Parquet

If you have custom CSV data, convert it to Parquet:

```python
import pandas as pd

# Read your CSV
df = pd.read_csv('your_variables.csv')

# Add optimized columns
df['code_lower'] = df['VarId'].str.lower()
df['description_lower'] = df['Description'].str.lower()

# Rename columns to match new schema
df = df.rename(columns={
    'VarId': 'code',
    'Description': 'description',
    'Category': 'category',
    'Theme': 'theme',
    'Context': 'context'
})

# Save as Parquet
df.to_parquet('variables_2022_can.parquet', compression='snappy', index=False)
```

### Step 2: Update Your Code

#### Python Integration

**Old Code**:
```python
from activation_manager.core.csv_variable_loader import CSVVariableLoader

loader = CSVVariableLoader()
results = loader.search_by_description("high income", limit=10)
```

**New Code**:
```python
from activation_manager.api.enhanced_variable_picker_api import EnhancedVariablePickerAPI

api = EnhancedVariablePickerAPI(openai_api_key=os.getenv('OPENAI_API_KEY'))
results = api.search_variables("high income", top_k=50)

# Access results
for var in results['results']:
    print(f"{var['code']}: {var['description']} (score: {var['score']})")
```

#### API Calls

**Old API Call**:
```bash
curl -X POST http://localhost:8080/api/variable_picker/search \
  -H "Content-Type: application/json" \
  -d '{"query": "millennials", "limit": 10}'
```

**New API Call**:
```bash
curl -X POST http://localhost:8080/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "millennials age 25-34",
    "top_k": 50,
    "use_semantic": true,
    "use_keyword": true
  }'
```

#### Frontend Integration

**Old Frontend Code**:
```javascript
// Old variable search
const response = await fetch('/api/variable_picker/search', {
  method: 'POST',
  body: JSON.stringify({ query: searchTerm, limit: 10 })
});
const data = await response.json();
const variables = data.variables;
```

**New Frontend Code**:
```javascript
// Enhanced variable search
const response = await fetch('/api/enhanced-variable-picker/search', {
  method: 'POST',
  body: JSON.stringify({ 
    query: searchTerm, 
    top_k: 50,
    use_semantic: true,
    use_keyword: true
  })
});
const data = await response.json();
const variables = data.results;

// Access additional features
console.log(`Found ${data.total_found} total matches`);
console.log(`Query intent: ${data.query_context.intent.primary_intent}`);
console.log(`Grouped by theme:`, data.grouped.by_theme);
```

### Step 3: Update Environment Variables

Add these to your `.env` or deployment configuration:

```bash
# Enable enhanced search features
USE_PARQUET=true
SEARCH_DEFAULT_TOP_K=50

# Optional: Add OpenAI key for semantic search
OPENAI_API_KEY=your-api-key-here

# Optional: Adjust hybrid search weights
HYBRID_WEIGHT_SEMANTIC=0.7
HYBRID_WEIGHT_KEYWORD=0.3
```

### Step 4: Update Frontend Components

If using the React components:

**Old Import**:
```javascript
import VariableSelector from './components/VariableSelector';
```

**New Import**:
```javascript
import EnhancedNLAudienceBuilder from './components/EnhancedNLAudienceBuilder';
```

The new component includes:
- 50 result pagination (10 per page)
- Semantic match indicators
- Real-time refinement
- Better responsive design

### Step 5: Update Tests

**Old Test**:
```python
def test_variable_search():
    loader = CSVVariableLoader()
    results = loader.search_by_description("income")
    assert len(results) <= 10
```

**New Test**:
```python
def test_enhanced_variable_search():
    api = EnhancedVariablePickerAPI()
    results = api.search_variables("income", top_k=50)
    assert len(results['results']) <= 50
    assert 'query_context' in results
    assert 'grouped' in results
```

## Feature Comparison

| Feature | Old System | New System |
|---------|------------|------------|
| **Data Format** | CSV | Parquet |
| **Load Time** | 2.5s | 0.3s |
| **Search Speed** | 200-300ms | 50-100ms |
| **Default Results** | 10 | 50 |
| **Max Results** | 20 | 100 |
| **Search Methods** | Keyword only | Keyword + Semantic |
| **Numeric Patterns** | No | Yes ("age 25-34") |
| **Domain Awareness** | No | Yes (5 domains) |
| **Result Grouping** | No | By theme/domain |
| **Intent Detection** | No | Yes |
| **Spell Correction** | No | Yes (planned) |
| **Synonyms** | No | Yes |
| **Caching** | No | Yes |

## Backward Compatibility

The system maintains backward compatibility:

1. **CSV Fallback**: If Parquet fails, automatically uses CSV
2. **Old Endpoints**: Still work but redirect to new system
3. **Result Format**: Compatible with extra fields added

To force CSV mode (not recommended):
```python
os.environ['USE_PARQUET'] = 'false'
```

## Common Issues and Solutions

### Issue 1: Different Result Count

**Problem**: Getting 50 results instead of expected 10

**Solution**: 
- Update frontend to handle pagination
- Or explicitly set `top_k=10` in API calls

### Issue 2: Missing Scores

**Problem**: Old code expects 'relevance' field, new uses 'score'

**Solution**:
```python
# Add compatibility layer
for result in results['results']:
    result['relevance'] = result.get('score', 0)
```

### Issue 3: Memory Usage

**Problem**: Higher memory usage with embeddings

**Solution**:
- Use instance class F4 or higher
- Disable semantic search if not needed: `use_semantic=false`

### Issue 4: API Key Required

**Problem**: Semantic search requires OpenAI API key

**Solution**:
- Add key to environment variables
- Or disable semantic search: `use_semantic=false`

## Performance Tuning

### Optimize for Speed
```python
# Keyword-only search (fastest)
results = api.search_variables(query, use_semantic=False, top_k=20)
```

### Optimize for Accuracy
```python
# Full hybrid search (most accurate)
results = api.search_variables(
    query, 
    use_semantic=True,
    use_keyword=True,
    top_k=50
)
```

### Domain-Specific Search
```python
# Filter by domain for better relevance
results = api.search_variables(
    "luxury cars",
    filters={"domain": "automotive"},
    top_k=30
)
```

## Rollback Plan

If you need to rollback:

1. **Code Rollback**:
   ```bash
   git checkout <previous-commit>
   ```

2. **Environment Variable**:
   ```bash
   USE_PARQUET=false
   ```

3. **API Fallback**:
   - Old endpoints still work
   - Results automatically adapt

## Timeline Recommendations

1. **Week 1**: Test in development environment
2. **Week 2**: Deploy to staging, run parallel tests
3. **Week 3**: Gradual production rollout (10% → 50% → 100%)
4. **Week 4**: Remove old code and optimize

## Support

For migration assistance:
- GitHub Issues: Tag with `migration`
- Documentation: See `/docs` folder
- Examples: Check `/tests/integration`

## Next Steps

After migration:
1. Monitor search performance metrics
2. Gather user feedback on 50-result format
3. Enable semantic search if not already
4. Consider custom domain configurations
5. Optimize based on usage patterns