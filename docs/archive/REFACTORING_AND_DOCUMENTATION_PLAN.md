# Activation Manager - Refactoring and Documentation Plan

## Executive Summary
This plan outlines a systematic approach to refactor the Activation Manager codebase, create comprehensive technical documentation, and establish proper GitHub repository management. The goal is to improve code maintainability, reduce technical debt, and enable easier onboarding for new developers.

## Phase 1: Immediate Cleanup (Week 1)

### 1.1 Test File Organization
**Current State**: 50+ test files scattered in root directory
**Action Items**:
```bash
# Move test files to organized structure
tests/
├── unit/
│   ├── test_enhanced_semantic_search.py
│   ├── test_similarity_filter.py
│   └── test_variable_selector.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_search_workflow.py
├── system/
│   ├── test_full_system.py
│   └── test_deployment.py
└── fixtures/
    └── test_data.py
```

### 1.2 Deployment Script Consolidation
**Current State**: 20+ deployment scripts with unclear purposes
**Action Items**:
- Create `scripts/deploy/` directory
- Consolidate into 3 main scripts:
  - `deploy-staging.sh` - For staging deployments
  - `deploy-production.sh` - For production deployments
  - `deploy-local.sh` - For local testing
- Archive old scripts in `scripts/archive/`
- Create `DEPLOYMENT_GUIDE.md` with decision tree

### 1.3 Remove/Archive Deprecated Code
**Files to Review**:
- `/activation_manager/archive/` - 4 files
- Old UI components that are no longer used
- Duplicate configuration files

## Phase 2: Code Refactoring (Weeks 2-3)

### 2.1 Consolidate Search Implementations

#### Current Structure:
```python
# Three separate implementations
- enhanced_semantic_search.py (665 lines)
- enhanced_semantic_search_v2.py (641 lines)  
- variable_selector.py (364 lines)
```

#### Proposed Structure:
```python
# Unified search module
activation_manager/search/
├── __init__.py
├── base.py              # Abstract base class
├── engine.py            # Main search engine
├── strategies/
│   ├── keyword.py       # Keyword search strategy
│   ├── semantic.py      # Semantic search strategy
│   └── hybrid.py        # Hybrid search strategy
├── filters/
│   ├── similarity.py    # Similarity filtering
│   └── category.py      # Category filtering
└── config.py           # Centralized configuration
```

### 2.2 Refactor Complex Functions

#### Target Functions for Refactoring:
1. `_filter_similar_variables()` (140+ lines)
   ```python
   # Break into:
   - _group_by_pattern()
   - _apply_similarity_threshold()
   - _select_representatives()
   ```

2. `search()` method
   ```python
   # Separate concerns:
   - query_preprocessing()
   - execute_search()
   - apply_filters()
   - format_results()
   ```

### 2.3 Implement Proper Dependency Injection

#### Current (Anti-pattern):
```python
# Global singleton
_enhanced_picker_instance = None

def get_enhanced_picker():
    global _enhanced_picker_instance
    if _enhanced_picker_instance is None:
        _enhanced_picker_instance = EnhancedVariablePickerAPI()
    return _enhanced_picker_instance
```

#### Proposed:
```python
# Dependency injection
class Application:
    def __init__(self, search_engine, config):
        self.search_engine = search_engine
        self.config = config

# In main.py
app = Application(
    search_engine=create_search_engine(config),
    config=load_config()
)
```

### 2.4 Extract Shared Configuration

Create centralized configuration module:
```python
# activation_manager/config/search_config.py
class SearchConfig:
    DOMAIN_CONFIGS = {
        "demographics": {...},
        "financial": {...},
        "geographic": {...}
    }
    
    DEFAULT_WEIGHTS = {
        "semantic": 0.7,
        "keyword": 0.3
    }
    
    FILTERING_DEFAULTS = {
        "similarity_threshold": 0.75,
        "max_similar_per_group": 2
    }
```

## Phase 3: Documentation Creation (Weeks 3-4)

### 3.1 API Documentation

#### Create OpenAPI Specification:
```yaml
# docs/api/openapi.yaml
openapi: 3.0.0
info:
  title: Activation Manager API
  version: 2.0.0
paths:
  /api/enhanced-variable-picker/search:
    post:
      summary: Search for variables
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchRequest'
```

#### Generate API Reference:
- Use Swagger UI for interactive documentation
- Create `docs/api/README.md` with examples
- Document all endpoints, parameters, and responses

### 3.2 Architecture Documentation

#### Create Single Source of Truth:
```markdown
# docs/architecture/README.md
# Activation Manager Architecture

## System Overview
[Architecture diagram using Mermaid]

## Components
- Frontend (React)
- Backend API (Flask)
- Search Engine
- Data Layer

## Data Flow
[Sequence diagram]

## Deployment Architecture
[Infrastructure diagram]
```

### 3.3 Developer Documentation

#### Essential Guides:
1. **Getting Started Guide**
   ```markdown
   # docs/development/getting-started.md
   - Prerequisites
   - Environment setup
   - Running locally
   - Running tests
   ```

2. **Contributing Guide**
   ```markdown
   # .github/CONTRIBUTING.md
   - Code style guide
   - Commit message format
   - PR process
   - Testing requirements
   ```

3. **Deployment Guide**
   ```markdown
   # docs/deployment/README.md
   - Deployment decision tree
   - Staging deployment
   - Production deployment
   - Rollback procedures
   ```

### 3.4 Code Documentation Standards

Implement consistent docstring format:
```python
def search_variables(self, query: str, **kwargs) -> Dict[str, Any]:
    """
    Search for variables using hybrid search strategy.
    
    Args:
        query: Search query string
        **kwargs: Additional search parameters
            - top_k (int): Number of results (default: 50)
            - filter_similar (bool): Apply similarity filter (default: False)
            - similarity_threshold (float): Similarity threshold (default: 0.75)
    
    Returns:
        Dict containing:
            - results: List of matching variables
            - total_found: Total number of results
            - search_metadata: Search execution details
    
    Raises:
        SearchError: If search execution fails
        
    Example:
        >>> results = search_variables("household income", top_k=10)
        >>> print(f"Found {results['total_found']} results")
    """
```

## Phase 4: GitHub Repository Setup (Week 4)

### 4.1 Repository Structure
```
activation-manager/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml          # Continuous Integration
│   │   ├── deploy-staging.yml
│   │   └── deploy-prod.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CONTRIBUTING.md
│   ├── CODE_OF_CONDUCT.md
│   └── SECURITY.md
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── deployment/
│   └── development/
├── src/
│   ├── activation_manager/
│   └── frontend/
├── tests/
├── scripts/
├── .gitignore
├── README.md
└── LICENSE
```

### 4.2 CI/CD Pipeline

#### GitHub Actions Workflow:
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=activation_manager
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 4.3 Updated README

```markdown
# Activation Manager

![Build Status](https://github.com/your-org/activation-manager/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/your-org/activation-manager/branch/main/graph/badge.svg)
![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)

## 🚀 Overview
Activation Manager is a powerful variable selection and audience building platform...

## 📋 Features
- ✨ Enhanced semantic search with 50-result capability
- 🔍 Smart similarity filtering to reduce duplicate results
- 🎯 Natural language audience building
- 📊 Advanced query processing

## 🛠️ Quick Start
```bash
# Clone the repository
git clone https://github.com/your-org/activation-manager.git

# Install dependencies
pip install -r requirements.txt
npm install

# Run locally
python main.py
```

## 📖 Documentation
- [API Reference](docs/api/README.md)
- [Architecture Guide](docs/architecture/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Contributing Guide](.github/CONTRIBUTING.md)

## 🧪 Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=activation_manager
```

## 🚢 Deployment
See our [Deployment Guide](docs/deployment/README.md) for detailed instructions.

## 📈 Performance
- Search latency: <100ms for 50k variables
- Filtering reduces duplicates by up to 98%
- Supports 1000+ concurrent users

## 🤝 Contributing
See [CONTRIBUTING.md](.github/CONTRIBUTING.md)

## 📄 License
[Your License]
```

## Implementation Timeline

### Week 1: Immediate Cleanup
- [ ] Organize test files
- [ ] Consolidate deployment scripts
- [ ] Archive deprecated code
- [ ] Create basic deployment guide

### Week 2: Search Refactoring
- [ ] Design unified search architecture
- [ ] Implement base search classes
- [ ] Migrate existing functionality
- [ ] Update tests

### Week 3: Complete Refactoring & Documentation
- [ ] Refactor complex functions
- [ ] Implement dependency injection
- [ ] Create API documentation
- [ ] Write architecture guide

### Week 4: GitHub & Final Polish
- [ ] Set up GitHub repository structure
- [ ] Implement CI/CD pipeline
- [ ] Complete all documentation
- [ ] Update README and guides

## Success Metrics
- [ ] All tests organized in proper directories
- [ ] Single, unified search implementation
- [ ] 100% of public APIs documented
- [ ] CI/CD pipeline running on all PRs
- [ ] Deployment time reduced by 50%
- [ ] New developer onboarding time < 1 hour

## Maintenance Plan
- Weekly code reviews to prevent technical debt
- Monthly documentation updates
- Quarterly architecture reviews
- Automated dependency updates via Dependabot

---

This plan provides a structured approach to improving the Activation Manager codebase. Each phase builds on the previous one, ensuring steady progress while maintaining system stability.