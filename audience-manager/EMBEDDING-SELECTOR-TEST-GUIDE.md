# Embedding Selector Testing Guide

## Overview

This guide provides thoughtful guidance for writing comprehensive unit tests for the embedding-based variable selector when you're ready to implement them.

## Test Categories

### 1. Embedding Service Tests (`test_embedding_service.py`)

#### Core Functionality Tests
```python
class TestEmbeddingSearcher:
    """Test the EmbeddingSearcher class"""
    
    def test_load_embeddings_from_gcs(self):
        """Test loading embeddings from Google Cloud Storage"""
        # Mock GCS client
        # Verify embeddings and metadata are loaded correctly
        # Test error handling for missing files
    
    def test_create_faiss_index(self):
        """Test FAISS index creation"""
        # Verify index is created with correct dimensions
        # Test index contains all embeddings
        # Verify search functionality works
    
    def test_get_query_embedding(self):
        """Test OpenAI API integration for query embeddings"""
        # Mock OpenAI API calls
        # Verify correct model is used (text-embedding-ada-002)
        # Test error handling for API failures
        # Test retry logic
    
    def test_search_similar_variables(self):
        """Test similarity search functionality"""
        # Test with various query types
        # Verify score calculation
        # Test top_k parameter
        # Test edge cases (empty query, special characters)
```

#### Performance Tests
```python
class TestEmbeddingPerformance:
    def test_search_latency(self):
        """Ensure search completes within acceptable time"""
        # Load test dataset
        # Measure search time for various queries
        # Assert < 300ms for warm queries
    
    def test_memory_usage(self):
        """Test memory consumption stays within limits"""
        # Load embeddings
        # Measure memory usage
        # Assert < 2GB total
    
    def test_concurrent_searches(self):
        """Test handling of concurrent search requests"""
        # Simulate multiple concurrent searches
        # Verify thread safety
        # Check response times remain acceptable
```

### 2. Integration Tests (`test_embedding_integration.py`)

#### API Integration Tests
```python
class TestEmbeddingAPIIntegration:
    def test_embedding_search_endpoint(self):
        """Test /api/embeddings/search endpoint"""
        # Test authenticated requests
        # Verify response format
        # Test various query parameters
        
    def test_nl_process_with_embeddings(self):
        """Test NL process uses embeddings when available"""
        # Mock embedding service
        # Verify embeddings are used over TF-IDF
        # Test fallback behavior
    
    def test_embedding_status_endpoint(self):
        """Test /api/embeddings/status endpoint"""
        # Verify returns correct statistics
        # Test when embeddings not loaded
```

#### Cache Integration Tests
```python
class TestEmbeddingCache:
    def test_query_caching(self):
        """Test query result caching"""
        # Make same query twice
        # Verify second query uses cache
        # Test cache expiration
    
    def test_cache_invalidation(self):
        """Test cache clears when embeddings reload"""
        # Load new embeddings
        # Verify cache is cleared
```

### 3. Fallback and Error Handling Tests

```python
class TestEmbeddingFallback:
    def test_fallback_to_tfidf(self):
        """Test graceful fallback when embeddings unavailable"""
        # Simulate embedding service failure
        # Verify system uses TF-IDF
        # Check user experience remains smooth
    
    def test_partial_embedding_failure(self):
        """Test handling of partial data corruption"""
        # Corrupt some embeddings
        # Verify system continues with available data
        # Test error reporting
    
    def test_openai_api_failure(self):
        """Test handling of OpenAI API failures"""
        # Mock API failures (rate limit, network, etc.)
        # Verify appropriate error messages
        # Test retry behavior
```

### 4. Data Validation Tests

```python
class TestEmbeddingDataValidation:
    def test_embedding_dimension_validation(self):
        """Verify all embeddings have correct dimensions"""
        # Load embeddings
        # Check all are 1536-dimensional
        # Test handling of incorrect dimensions
    
    def test_metadata_consistency(self):
        """Test metadata matches embeddings"""
        # Verify each variable in metadata has embeddings
        # Check description counts match
        # Test handling of mismatches
    
    def test_variable_code_validation(self):
        """Test variable code format and uniqueness"""
        # Verify codes follow expected format
        # Check for duplicates
        # Test special character handling
```

### 5. Frontend Component Tests

```typescript
describe('Enhanced Variable Selector with Embeddings', () => {
  test('displays embedding-based results', async () => {
    // Mock embedding search API
    // Render component
    // Type query
    // Verify results show similarity scores
    // Check result ordering
  });
  
  test('shows embedding vs TF-IDF indicator', () => {
    // Verify UI indicates which search method is used
    // Test toggle between methods if implemented
  });
  
  test('handles embedding service errors gracefully', () => {
    // Mock embedding service failure
    // Verify fallback to TF-IDF
    // Check error message display
  });
});
```

## Testing Best Practices

### 1. Mock External Dependencies

```python
# Mock OpenAI
@patch('openai.Embedding.create')
def test_embedding_creation(mock_create):
    mock_create.return_value = {
        'data': [{'embedding': [0.1] * 1536}]
    }
    # Test implementation

# Mock GCS
@patch('google.cloud.storage.Client')
def test_gcs_operations(mock_client):
    # Mock bucket and blob operations
    # Test file operations
```

### 2. Use Fixtures for Test Data

```python
@pytest.fixture
def sample_embeddings():
    """Generate sample embeddings for testing"""
    return {
        'VAR001': np.random.rand(5, 1536),  # 5 descriptions
        'VAR002': np.random.rand(10, 1536), # 10 descriptions
    }

@pytest.fixture
def sample_metadata():
    """Generate sample metadata for testing"""
    return [
        {
            'code': 'VAR001',
            'original_description': 'Test variable 1',
            'generated_descriptions': ['Desc 1', 'Desc 2', 'Desc 3', 'Desc 4', 'Desc 5']
        }
    ]
```

### 3. Test Data Generation

Create test data that covers:
- Different variable categories (demographic, psychographic, etc.)
- Various description lengths
- Edge cases (empty descriptions, special characters)
- Different languages if supported

### 4. Performance Benchmarks

```python
def test_search_performance_benchmark():
    """Ensure search performance meets requirements"""
    queries = [
        "young professionals",
        "environmentally conscious consumers",
        "tech-savvy millennials with high income"
    ]
    
    for query in queries:
        start = time.time()
        results = searcher.search(query)
        elapsed = time.time() - start
        
        assert elapsed < 0.3  # 300ms max
        assert len(results) > 0
```

### 5. Test Coverage Goals

Aim for:
- 90%+ code coverage for critical paths
- 100% coverage for error handling
- All edge cases covered
- Performance regression tests

## Testing Utilities

### Create Test Helpers

```python
# test_utils.py
class EmbeddingTestHelper:
    @staticmethod
    def create_test_embeddings(n_vars=10, n_desc_per_var=5):
        """Create test embeddings with known properties"""
        # Generate embeddings with controlled similarity
        
    @staticmethod
    def create_test_h5_file(filepath, embeddings):
        """Create test H5 file"""
        # Write embeddings in expected format
        
    @staticmethod
    def assert_search_quality(results, expected_vars):
        """Assert search results meet quality standards"""
        # Check relevance scores
        # Verify expected variables appear
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Embedding Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run embedding tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY_TEST }}
        run: |
          pytest tests/test_embedding_*.py -v --cov=embedding_service
      
      - name: Check performance benchmarks
        run: |
          python tests/benchmark_embedding_search.py
```

## Test Data Management

### Synthetic Test Data

Create synthetic embeddings for testing:

```python
def generate_test_embeddings():
    """Generate realistic test embeddings"""
    # Create clusters of similar variables
    clusters = {
        'demographic': create_demographic_cluster(),
        'psychographic': create_psychographic_cluster(),
        'behavioral': create_behavioral_cluster()
    }
    
    # Add noise and variations
    # Save in test format
```

### Test Scenarios

1. **Happy Path**: Standard searches return relevant results
2. **Edge Cases**: 
   - Empty queries
   - Very long queries
   - Special characters
   - Non-English queries
3. **Error Cases**:
   - Missing embeddings
   - Corrupted data
   - API failures
4. **Performance Cases**:
   - Large result sets
   - Concurrent requests
   - Cold starts

## Debugging Tests

### Logging in Tests

```python
import logging

# Configure test logging
logging.basicConfig(level=logging.DEBUG)

def test_embedding_search_debug():
    """Test with detailed logging"""
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Loading embeddings...")
    searcher = EmbeddingSearcher()
    
    logger.debug(f"Searching for: {query}")
    results = searcher.search(query)
    
    logger.debug(f"Found {len(results)} results")
    for r in results[:5]:
        logger.debug(f"  {r['code']}: {r['score']:.3f}")
```

## Future Test Considerations

### A/B Testing Framework

```python
class TestABComparison:
    def test_embedding_vs_tfidf_relevance(self):
        """Compare result relevance between methods"""
        # Run same queries through both systems
        # Measure relevance metrics
        # Statistical significance testing
```

### Model Version Testing

```python
def test_model_version_compatibility():
    """Test compatibility with different embedding models"""
    # Test with ada-002
    # Prepare for future models (ada-003, etc.)
    # Verify dimension handling
```

## Summary

When implementing these tests:

1. Start with core functionality tests
2. Add integration tests for API endpoints
3. Implement performance benchmarks
4. Create comprehensive test data
5. Set up CI/CD pipeline
6. Monitor test coverage

Remember: Good tests enable confident refactoring and catch regressions early. The embedding system is critical for search quality, so thorough testing is essential.