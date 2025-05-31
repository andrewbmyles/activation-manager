# Technical Documentation Index

Last Updated: May 30, 2025

## Core Documentation

### Architecture
- [System Architecture](./ARCHITECTURE.md) - Overall system design
- [Data Persistence Architecture](./DATA_PERSISTENCE_ARCHITECTURE.md) - Storage layer design
- [API Documentation](./API_DOCUMENTATION.md) - Complete API reference

### Features
- [Enhanced Variable Picker](./ENHANCED_VARIABLE_PICKER_API.md) - Advanced search capabilities
- [Enhanced Audience Features](./ENHANCED_AUDIENCE_FEATURES.md) - Audience management
- [Complex Query Support](./API_COMPLEX_QUERY_REFERENCE.md) - Natural language queries
- [Similarity Filtering](./ENHANCED_VARIABLE_PICKER_PERFORMANCE.md) - Duplicate reduction

### Implementation Guides
- [Variable Refine Documentation](./VARIABLE_REFINE_DOCUMENTATION.md) - Refine functionality
- [Semantic Display Documentation](./SEMANTIC_DISPLAY_DOCUMENTATION.md) - UI enhancements
- [Natural Language Multivariate Builder](./NATURAL_LANGUAGE_MULTIVARIATE_AUDIENCE_BUILDER.md)

## Deployment Documentation

### Deployment Guides
- [Production Deployment Guide](./deployment/PRODUCTION_DEPLOYMENT.md)
- [Vercel Deployment](./deployment/VERCEL_DEPLOYMENT.md)
- [Enhanced Deployment Guide](./deployment/ENHANCED_DEPLOYMENT_GUIDE.md)
- [Deployment Options](./deployment/DEPLOYMENT_OPTIONS.md)

### Quick References
- [Deployment Quick Guide](./deployment/DEPLOYMENT_QUICK_GUIDE.md)
- [Deployment Decision Tree](./deployment/DEPLOYMENT_DECISION_TREE.md)
- [Unified Search Deployment](./deployment/UNIFIED_SEARCH_DEPLOYMENT.md)

## Operations

### Monitoring and Maintenance
- [Operations Guide](./operations/OPERATIONS_GUIDE.md) - Day-to-day operations
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
- [Migration Guide](./MIGRATION_GUIDE.md) - Version migration procedures

### Security
- [SOC2 Compliance Assessment](./security/SOC2_COMPLIANCE_ASSESSMENT.md)
- [API Security](./security/API_SECURITY.md) - Authentication and authorization
- [Outbound API Calls Inventory](./OUTBOUND_API_CALLS_INVENTORY.md)

## Development

### Getting Started
- [Development Setup](./development/SETUP.md) - Local environment setup
- [Testing Guide](./development/TESTING.md) - Running tests
- [Contributing Guidelines](./development/CONTRIBUTING.md)

### Component Development
- [Component Development Guide](./COMPONENT-DEVELOPMENT-GUIDE.md)
- [Data Structures & Types](./DATA-STRUCTURES-TYPES.md)
- [State Management](./STATE-MANAGEMENT.md)
- [Styling & Design System](./STYLING-DESIGN-SYSTEM.md)

### API Development
- [API Variable Picker](./API_VARIABLE_PICKER.md)
- [Enhanced Variable Picker API](./ENHANCED_VARIABLE_PICKER_API.md)
- [Data Persistence API Reference](./DATA_PERSISTENCE_API_REFERENCE.md)

## Recent Updates

### May 30, 2025
- [Refactoring Complete Documentation](./REFACTORING_COMPLETE_20250530.md) - Unified search implementation
- [v1.8.0 Deployment Success](../DEPLOYMENT_SUCCESS_V180.md) - Critical bug fix deployment

### May 29, 2025
- Enhanced Audience Management features
- Similarity filtering implementation

### May 28, 2025
- Complex query support
- Data persistence layer

## Product Documentation

### User Guides
- [Product Documentation](./product/PRODUCT_DOCUMENTATION.md) - End-user documentation
- [Data Persistence User Guide](./DATA_PERSISTENCE_USER_GUIDE.md)
- [API User Guide](./api/USER_GUIDE.md)

### Technical Specifications
- [Technical Documentation](./technical/TECHNICAL_DOCUMENTATION.md)
- [Architecture Overview](./technical/ARCHITECTURE.md)
- [Authentication System](./technical/AUTHENTICATION.md)

## Implementation Guides (8-Part Series)

1. [Part 1 - Foundation](./IMPLEMENTATION-GUIDE-PART1.md)
2. [Part 2 - Components](./IMPLEMENTATION-GUIDE-PART2.md)
3. [Part 3 - State Management](./IMPLEMENTATION-GUIDE-PART3.md)
4. [Part 4 - API Integration](./IMPLEMENTATION-GUIDE-PART4.md)
5. [Part 5 - Advanced Features](./IMPLEMENTATION-GUIDE-PART5.md)
6. [Part 6 - Testing](./IMPLEMENTATION-GUIDE-PART6.md)
7. [Part 7 - Deployment](./IMPLEMENTATION-GUIDE-PART7.md)
8. [Part 8 - Maintenance](./IMPLEMENTATION-GUIDE-PART8.md)

## Quick Links

### Critical Files
- [main.py](../main.py) - Main application entry point
- [app_production.yaml](../app_production.yaml) - Production configuration
- [requirements.txt](../requirements.txt) - Python dependencies
- [package.json](../package.json) - Node.js dependencies

### Key Modules
- [Enhanced Variable Picker API](../activation_manager/api/enhanced_variable_picker_api.py)
- [Enhanced Semantic Search V2](../activation_manager/core/enhanced_semantic_search_v2.py)
- [Similarity Filter](../activation_manager/core/similarity_filter.py)
- [Unified Search](../activation_manager/search/unified_search.py)

### Test Suites
- [Final Integration Test](../test_final_integration.py)
- [Staging Test](../test_staging_fix.py)
- [Production Stability Test](../test_production_stability.py)

## Documentation Standards

### File Naming
- Use UPPERCASE for documentation files
- Use underscores for spaces
- Include dates for time-sensitive docs (YYYYMMDD format)

### Content Structure
1. Overview/Summary
2. Technical Details
3. Implementation Guide
4. Examples
5. Troubleshooting
6. References

### Versioning
- Document major changes in CHANGELOG.md
- Tag releases with semantic versioning
- Archive outdated documentation in `archive/` folder

## Need Help?

- Check [Troubleshooting Guide](./TROUBLESHOOTING.md) first
- Review relevant implementation guides
- Search codebase for examples
- Contact development team

---

*This index is maintained as part of the Activation Manager project. Please keep it updated when adding new documentation.*