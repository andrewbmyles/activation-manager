# Changelog

All notable changes to the Activation Manager project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2025-05-30

### Fixed - Critical Performance Issues
- **Resolved Flask Server Hangs**: Fixed critical issue where server would hang on enhanced picker initialization
  - Root cause: spaCy model loading timeout during startup
  - Solution: Added timeout handling and environment variable controls
  - Default: `DISABLE_SPACY=true` to prevent production hangs
  
- **Enhanced Variable Picker Stability**: Improved initialization robustness
  - Added retry logic with exponential backoff
  - Implemented lazy loading for heavy components
  - Added caching to prevent duplicate initialization across workers
  
- **OpenAI Client Initialization**: Fixed hanging when no API key provided
  - Added proper error handling and logging
  - Made OpenAI client truly optional
  
### Added - Complex Query Support
- **Advanced Query Understanding**: Natural language processing for multi-faceted queries
  - Concept extraction and relationship mapping
  - Support for queries like "find millennial women with high income who are environmentally conscious"
  - Intelligent query expansion with synonyms and related terms
  
- **Enhanced Search Results**: Richer metadata and explanations
  - Concept matching information
  - Coverage scores showing how well variables match query intent
  - Relevance explanations for better user understanding
  
### Improved - Performance Optimizations
- **Faster Startup Times**: Reduced initialization overhead
  - Disabled spaCy by default (can be enabled via `DISABLE_SPACY=false`)
  - Optimized FAISS loading with better error handling
  - Implemented shared cache for cross-worker efficiency
  
- **Better Error Recovery**: Graceful fallbacks for all failure modes
  - Basic parquet search when enhanced search unavailable
  - Keyword-only search when semantic search fails
  - Comprehensive error logging for debugging

## [1.7.0] - 2025-05-29

### Added - Enhanced Audience Management
- **Smart Audience Cards**: Visual card-based display replacing simple lists
  - 3-column responsive grid layout with hover effects
  - Rich information display with icons, sizes, and descriptions
  - Interactive elements and professional styling
  
- **Generated Audience Names**: Automatic descriptive naming system
  - Smart name generation like "Gaming-Enthusiast Gen Z Males"
  - Combines demographics, interests, and location data
  - Fallback to "Custom Audience Segment" for unrecognized patterns
  
- **Natural Language Descriptions**: Convert technical criteria to readable format
  - Transform "gender=male AND age_min=18" to "Males between the ages of 18 and 24"
  - Support for demographics, interests, locations, and income indicators
  - Graceful fallbacks for complex or unmatched queries
  
- **Random Demo Sizes**: Realistic audience sizes for demonstration
  - Random generation between 56,798-89,380 people
  - Consistent formatting with comma separators
  - Used throughout save and display workflow
  
- **Dynamic Icon System**: 15+ icons automatically selected by audience type
  - Gaming (🎮), Fashion (👜), Health (💪), Business (💼), Travel (✈️)
  - Color-coded system with unique colors per category
  - Fallback to Users icon for unrecognized types
  
- **Contextual Insights**: AI-generated insights based on audience characteristics
  - Size-based insights (Large audience 80K+, Focused audience 60K+)
  - Query-based insights (High purchasing power, Digital-native generation)
  - Up to 2 insights displayed per audience card

### Enhanced Features
- **Enhanced Save Experience**: Rich success messages with generated names
- **Improved Display Logic**: Enhanced data with graceful legacy fallbacks
- **Utility Functions**: Complete audienceUtils.ts with 6 core functions
- **Comprehensive Testing**: 67 unit tests + integration tests (100% pass rate)

### Technical Improvements
- **Dynamic Imports**: Code splitting for utility functions
- **Performance Optimization**: Debounced search and efficient rendering
- **Memory Management**: Proper cleanup and leak prevention
- **Type Safety**: Full TypeScript support with interface definitions
- **Backward Compatibility**: Legacy audiences display without enhanced fields

### Documentation
- Created ENHANCED_AUDIENCE_FEATURES.md with complete feature guide
- Updated README.md with v1.7.0 feature highlights
- Comprehensive testing documentation with 95%+ coverage
- API integration examples and troubleshooting guide

## [1.5.0] - 2025-05-30

### Added
- **Data Persistence**: Complete audience save and management functionality
  - Save button in Natural Language Multi-Variate Audience Builder
  - Saved Audiences page with list view
  - Archive functionality for audience management
  - Thread-safe Parquet file storage with user isolation
  - REST API endpoints for audience CRUD operations
  - Navigation link for Saved Audiences in sidebar
  - Comprehensive unit tests (19 backend tests, all passing)
  - User guide and API documentation

### Technical Improvements
- Added `parquet_handlers_fixed.py` with proper timestamp handling
- Implemented write locks for concurrent operations
- Created partitioned storage structure (by user and date)
- Added graceful error handling for persistence failures
- Fixed PyArrow timestamp conversion issues
- Added flexible schema handling for missing fields

### Documentation
- Created DATA_PERSISTENCE_USER_GUIDE.md
- Created DATA_PERSISTENCE_API_REFERENCE.md  
- Created DATA_PERSISTENCE_ARCHITECTURE.md
- Updated README.md with v1.5.0 features

### Testing
- 19 backend unit tests for persistence handlers
- Thread safety and concurrency tests
- User isolation security tests
- Frontend component test structure

## [1.4.0] - 2025-05-28

### Added
- Natural Language Multi-Variate Audience Builder enhancements:
  - Responsive UI scaling for larger screens with dynamic breakpoints
  - Unified data source integration with Variable Picker
  - Direct integration with Enhanced Variable Picker API
  - Automatic fallback to original API when enhanced API fails
- Comprehensive unit tests for enhanced features
- API documentation for Enhanced Variable Picker endpoints
- Component documentation for Natural Language Multi-Variate Audience Builder
- Loading states for variable searches
- Enhanced error handling with graceful fallbacks

### Changed
- Renamed "Enhanced Natural Language Audience Builder" to "Natural Language Multi-Variate Audience Builder"
- Variable selection now uses same data sources as Variable Picker (Parquet/CSV)
- Improved responsive design with viewport-based scaling:
  - Workflow sidebar: `w-64` → `lg:w-80` → `xl:w-96`
  - Chat messages: `max-w-2xl` → `lg:max-w-3xl` → `xl:max-w-4xl`
  - Variable list: `max-h-64` → `lg:max-h-96` → `xl:max-h-[32rem]`
  - Main container: `h-[calc(100vh-16rem)]` with `min-h-[600px]`
- Enhanced padding scales with screen size for better readability

### Fixed
- Variable search consistency between Natural Language Builder and Variable Picker
- UI scaling issues on large displays
- API integration error handling
- Variable transformation for different API response formats

### Documentation
- Added NATURAL_LANGUAGE_MULTIVARIATE_AUDIENCE_BUILDER.md
- Added ENHANCED_VARIABLE_PICKER_API.md
- Updated README.md with v1.4.0 features
- Enhanced API documentation with examples

## [1.3.0] - 2025-05-28

### Added
- Enhanced semantic variable picker returning 50 results (up from 5)
- Pagination controls showing 10 results per page
- "Show All Variables" toggle option
- Auto-selection of top 10 most relevant variables
- Safe deployment script (`deploy-production-safe.sh`) with:
  - Automatic backups
  - Build directory cleaning
  - Build integrity verification
  - Test deployment before production
  - Deployment records
- Health check script (`check-deployment-health.sh`)
- Comprehensive deployment best practices documentation
- Unit tests for pagination functionality (11 new tests)

### Fixed
- Form submission bug where selecting variables caused page redirects
- Deployment build conflicts from mixing Tobermory Web and Activation Manager builds
- Dashboard UI breaking after deployments
- Relevance scores now properly normalized to 0-1 range

### Changed
- `/api/nl/process` endpoint now returns 50 results instead of 5
- Updated deployment process to prevent build conflicts
- Enhanced error handling in variable selection
- Improved build process to maintain file integrity

### Documentation
- Updated README.md with new deployment procedures
- Added DEPLOYMENT_BEST_PRACTICES.md
- Updated RELEASE-NOTES.md with version 1.3.0
- Enhanced deployment guides with safety warnings

## [1.2.2] - 2025-05-25

### Fixed
- K-Medians clustering workflow hang on step 5
- Audience builder criteria crash and redirect
- Logo alignment and sizing issues
- Distribution navigation white screen error

### Added
- Comprehensive error handling
- Debug logging for API requests
- Null safety checks throughout application
- Unit tests for all bug fixes

## [1.2.1] - 2025-05-25

### Fixed
- Dashboard logo sizing issues
- Logo alignment in platform status section

### Changed
- Increased logo sizes for better visibility
- Optimized CSS bundle size

## [1.2.0] - 2025-05-24

### Added
- Audience type classification system (1st Party, 3rd Party, Clean Room)
- Data source identifiers (RampID, UID2.0, PRIZM, etc.)
- Type badges on audience cards
- Cascading dropdowns for type/subtype selection

### Fixed
- Variable selection navigation issues
- Form stability and data persistence

### Improved
- TypeScript type safety
- Component architecture
- Responsive design

## [1.1.0] - 2025-05-23

### Added
- Variable metadata integration with 50+ variables
- Sophisticated VariableSelector component
- Advanced criteria management in audience builder

## [1.0.0] - 2025-05-22

### Added
- Core audience management functionality
- Platform integration dashboard
- Distribution center and analytics
- React Router navigation system
- Professional Activation Manager branding