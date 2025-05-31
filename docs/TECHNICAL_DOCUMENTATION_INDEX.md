# Technical Documentation Index

Welcome to the Activation Manager technical documentation. This index provides a comprehensive guide to all technical resources.

## 📚 Documentation Structure

### 1. Getting Started
- **[README.md](../README.md)** - Project overview and quick start
- **[docs/development/getting-started.md](development/getting-started.md)** - Detailed setup guide
- **[CONTRIBUTING.md](../.github/CONTRIBUTING.md)** - How to contribute

### 2. Architecture & Design
- **[docs/architecture/README.md](architecture/README.md)** - System architecture overview
- **[docs/architecture/search-architecture.md](architecture/search-architecture.md)** - Search engine design
- **[docs/architecture/data-flow.md](architecture/data-flow.md)** - Data flow diagrams
- **[REFACTORING_AND_DOCUMENTATION_PLAN.md](../REFACTORING_AND_DOCUMENTATION_PLAN.md)** - Technical debt and improvements

### 3. API Documentation
- **[docs/api/ENHANCED_API_REFERENCE.md](api/ENHANCED_API_REFERENCE.md)** - Complete API reference
- **[docs/api/openapi.yaml](api/openapi.yaml)** - OpenAPI specification
- **[API_DOCUMENTATION.md](../API_DOCUMENTATION.md)** - Legacy API docs

### 4. Component Documentation

#### Search & Filtering
- **[Enhanced Semantic Search](../activation_manager/core/enhanced_semantic_search_v2.py)** - Advanced search implementation
- **[Similarity Filter](../activation_manager/core/similarity_filter.py)** - Jaro-Winkler filtering
- **[Variable Selector](../activation_manager/core/variable_selector.py)** - Basic variable selection

#### Data Processing
- **[Enhanced Parquet Loader](../activation_manager/core/enhanced_parquet_loader.py)** - Efficient data loading
- **[Advanced Query Processor](../activation_manager/core/advanced_query_processor.py)** - NLP query processing

#### API Layer
- **[Enhanced Variable Picker API](../activation_manager/api/enhanced_variable_picker_api.py)** - Main API implementation

### 5. Deployment & Operations
- **[docs/deployment/DEPLOYMENT_DECISION_TREE.md](deployment/DEPLOYMENT_DECISION_TREE.md)** - Which deployment method to use
- **[DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)** - General deployment guide
- **[docs/deployment/staging-deployment.md](deployment/staging-deployment.md)** - Staging procedures
- **[docs/deployment/production-deployment.md](deployment/production-deployment.md)** - Production procedures
- **[docs/deployment/rollback-procedures.md](deployment/rollback-procedures.md)** - Emergency rollback

### 6. Testing
- **[docs/testing/testing-guide.md](testing/testing-guide.md)** - Comprehensive testing guide
- **[docs/testing/unit-testing.md](testing/unit-testing.md)** - Unit test best practices
- **[docs/testing/integration-testing.md](testing/integration-testing.md)** - Integration test patterns

### 7. Performance & Optimization
- **[COST_OPTIMIZATION_GUIDE.md](../COST_OPTIMIZATION_GUIDE.md)** - Cloud cost optimization
- **[docs/performance/search-optimization.md](performance/search-optimization.md)** - Search performance tuning
- **[docs/performance/caching-strategy.md](performance/caching-strategy.md)** - Caching implementation

### 8. Frontend Documentation
- **[src/components/README.md](../src/components/README.md)** - React component guide
- **[src/hooks/README.md](../src/hooks/README.md)** - Custom hooks documentation
- **[docs/frontend/state-management.md](frontend/state-management.md)** - State management patterns

### 9. Feature-Specific Documentation

#### Variable Picker Enhancement
- **[ENHANCED_VARIABLE_PICKER_API.md](../docs/ENHANCED_VARIABLE_PICKER_API.md)** - Enhanced picker features
- **[VARIABLE_PICKER_COMPLETION_SUMMARY.md](../VARIABLE_PICKER_COMPLETION_SUMMARY.md)** - Implementation summary

#### Audience Building
- **[ENHANCED_AUDIENCE_FEATURES.md](ENHANCED_AUDIENCE_FEATURES.md)** - Audience builder features
- **[NATURAL_LANGUAGE_MULTIVARIATE_AUDIENCE_BUILDER.md](NATURAL_LANGUAGE_MULTIVARIATE_AUDIENCE_BUILDER.md)** - NL interface

#### Data Persistence
- **[DATA_PERSISTENCE_IMPLEMENTATION.md](../DATA_PERSISTENCE_IMPLEMENTATION.md)** - Persistence layer
- **[DATA_PERSISTENCE_API_REFERENCE.md](DATA_PERSISTENCE_API_REFERENCE.md)** - Persistence API

### 10. Troubleshooting & Debugging
- **[docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[docs/debugging/logging-guide.md](debugging/logging-guide.md)** - Logging best practices
- **[docs/debugging/common-errors.md](debugging/common-errors.md)** - Error reference

## 🔧 Key Technical Concepts

### Search Architecture
The system uses a hybrid search approach combining:
1. **Keyword Search** - Fast text matching using pandas
2. **Semantic Search** - Vector similarity using FAISS (when available)
3. **Similarity Filtering** - Jaro-Winkler algorithm to reduce duplicates

### Data Flow
```
User Query → API Layer → Query Processing → Search Engine → Filtering → Results
                ↓                              ↓
           Validation                    Caching Layer
```

### Deployment Architecture
- **Google App Engine** - Main hosting platform
- **Cloud Storage** - Static assets and embeddings
- **GitHub Actions** - CI/CD pipeline
- **Staging Environment** - Testing before production

## 🚀 Quick References

### Common Commands
```bash
# Run tests
pytest tests/

# Deploy to staging
./deploy-staging.sh

# Promote to production
./promote-to-prod.sh VERSION

# View logs
gcloud app logs tail
```

### Environment Variables
```bash
USE_EMBEDDINGS=true/false     # Enable semantic search
OPENAI_API_KEY=sk-...         # OpenAI API key
GAE_APPLICATION=project-id    # Google Cloud project
```

### Key Files
- `main.py` - Flask application entry point
- `app.yaml` - App Engine configuration
- `requirements.txt` - Python dependencies
- `package.json` - Frontend dependencies

## 📈 Performance Metrics

- **Search Latency**: < 100ms for 50k variables
- **Filtering Reduction**: Up to 98% duplicate reduction
- **Memory Usage**: < 512MB per instance
- **Concurrent Users**: 1000+

## 🔗 External Resources

- [Google App Engine Documentation](https://cloud.google.com/appengine/docs)
- [React Documentation](https://reactjs.org/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pytest Documentation](https://docs.pytest.org/)

## 📝 Documentation Standards

When adding new documentation:
1. Use clear, descriptive titles
2. Include code examples
3. Add diagrams where helpful
4. Keep documentation close to code
5. Update this index

## 🤝 Contributing to Documentation

See [CONTRIBUTING.md](../.github/CONTRIBUTING.md) for guidelines on:
- Documentation style
- File organization
- Review process

---

Last updated: 2025-05-30