# Activation Manager Refactoring Plan

## Overview
This document outlines the refactoring plan for the Activation Manager codebase to improve maintainability, reduce duplication, and streamline deployment processes.

## Phase 1: Code Consolidation (Priority: High)

### 1.1 Backend Consolidation
- [ ] Merge all `main*.py` files into a single `main.py`
- [ ] Remove duplicate backend implementations
- [ ] Consolidate requirements into single `requirements.txt`
- [ ] Move all backend code to `backend/` directory

### 1.2 Frontend Organization
- [ ] Remove Python files from React src directory
- [ ] Consolidate all frontend code under `audience-manager/`
- [ ] Remove duplicate build artifacts

### 1.3 Deployment Script Consolidation
- [ ] Create single master deployment script `deploy.sh`
- [ ] Remove 35+ duplicate deployment scripts
- [ ] Create configuration-based deployment system

## Phase 2: Documentation Update (Priority: High)

### 2.1 API Documentation
- [ ] Document all Variable Picker endpoints
- [ ] Document Natural Language processing endpoints
- [ ] Create OpenAPI/Swagger specification

### 2.2 Architecture Documentation
- [ ] Create system architecture diagram
- [ ] Document data flow
- [ ] Document component interactions

### 2.3 Deployment Documentation
- [ ] Single deployment guide
- [ ] Troubleshooting guide
- [ ] Environment configuration guide

## Phase 3: Configuration Management (Priority: Medium)

### 3.1 Environment Configuration
- [ ] Create `.env.example` template
- [ ] Implement configuration class
- [ ] Remove hardcoded values

### 3.2 App Engine Configuration
- [ ] Consolidate to single `app.yaml`
- [ ] Use environment-based overrides
- [ ] Document configuration options

## Phase 4: Testing Infrastructure (Priority: Medium)

### 4.1 Unit Tests
- [ ] Add missing component tests
- [ ] Increase code coverage to 80%+
- [ ] Implement test naming conventions

### 4.2 Integration Tests
- [ ] Test API endpoints
- [ ] Test data flow
- [ ] Test deployment pipeline

## Phase 5: Data Management (Priority: Low)

### 5.1 Data Storage
- [ ] Move large files to cloud storage
- [ ] Implement data versioning
- [ ] Document data schemas

### 5.2 Embeddings Management
- [ ] Consolidate embedding formats
- [ ] Optimize loading strategy
- [ ] Document embedding usage

## Proposed Directory Structure

```
activation-manager/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── variable_picker.py
│   │   ├── natural_language.py
│   │   └── audience_builder.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── search.py
│   │   └── data_loader.py
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_core.py
│   │   └── test_integration.py
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   └── README.md
├── deployment/
│   ├── deploy.sh
│   ├── app.yaml
│   └── configs/
│       ├── production.yaml
│       └── development.yaml
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
├── data/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── README.md
└── CHANGELOG.md
```

## Implementation Timeline

### Week 1-2: Code Consolidation
- Merge duplicate files
- Reorganize directory structure
- Clean up unused code

### Week 3: Documentation
- Write comprehensive documentation
- Update existing docs
- Create diagrams

### Week 4: Configuration & Testing
- Implement configuration management
- Add missing tests
- Setup CI/CD

## Success Metrics
- Reduce codebase size by 40%
- Achieve 80% test coverage
- Single deployment command
- Complete API documentation
- Clear architecture documentation

## Notes
- No deployment until explicitly requested
- Maintain backward compatibility
- Preserve all functionality
- Git history will track all changes