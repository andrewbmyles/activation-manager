# Test Suite Documentation

## Overview
This directory contains the official test suite for the Activation Manager project.

## Test Organization

### Unit Tests (`unit/`)
- `test_advanced_query_processor.py` - Query processing logic
- `test_audience_builder.py` - Audience creation functionality
- `test_enhanced_semantic_search.py` - Semantic search features
- `test_similarity_filter.py` - Jaro-Winkler similarity filtering
- `test_bug_fixes.py` - Regression tests for fixed bugs

### Integration Tests (`integration/`)
- `test_complete_workflow.py` - End-to-end workflows
- `test_enhanced_audience_api.py` - API integration
- `test_unified_api.py` - Unified search API tests

### System Tests (`system/`)
- `test_complete_system.py` - Full system tests
- `test_enhanced_tools.py` - Tool integration tests

### Performance Tests (`performance/`)
- Benchmarks for search performance
- Load testing scripts
- Memory usage tests

## Running Tests

### All Tests
```bash
python -m pytest tests/
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# With coverage
python -m pytest tests/ --cov=activation_manager
```

### Essential Integration Test
For quick validation of the entire system:
```bash
python test_final_integration.py
```

## Test Data

Test fixtures are located in `tests/fixtures/` and include:
- Sample variable data
- Mock API responses  
- Test embeddings

## Writing New Tests

1. Follow the existing structure
2. Use descriptive test names
3. Include docstrings explaining what's being tested
4. Mock external dependencies
5. Keep tests focused and isolated

## CI/CD Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Before deployments

See `.github/workflows/ci.yml` for configuration.