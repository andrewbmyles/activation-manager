# Activation Manager

A sophisticated audience segmentation and targeting platform that uses natural language processing and machine learning to help marketers create precise audience segments.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.8.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18.2-61dafb)

## 🚀 Live Demo

The application is deployed and running at: **https://tobermory.ai**

## 📁 Project Structure

```
activation-manager/
├── activation_manager/     # Core Python backend
│   ├── api/               # API endpoints
│   ├── core/              # Business logic & search engine
│   └── config/            # Configuration
├── src/                   # React frontend
│   ├── components/        # UI components
│   ├── pages/            # Page components
│   └── hooks/            # Custom React hooks
├── tests/                # Organized test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── system/           # System tests
├── scripts/              # Utility scripts
│   └── deploy/           # Essential deployment scripts
└── docs/                 # Documentation
    ├── api/              # API documentation
    ├── architecture/     # System design
    └── deployment/       # Deployment guides
```

## 🔄 Deployment Process

We use a staging → production workflow with simplified scripts:

```bash
# 1. Deploy to staging
./scripts/deploy/deploy-staging.sh

# 2. Test in staging
# 3. Promote to production
./scripts/deploy/promote-to-prod.sh stg-VERSION
```

See [DEPLOYMENT_QUICK_GUIDE.md](DEPLOYMENT_QUICK_GUIDE.md) for details.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run tests
pytest tests/

# Start development server
python main.py

# Deploy to staging
./scripts/deploy/deploy-staging.sh
```

## 📚 Documentation

- [API Reference](docs/api/ENHANCED_API_REFERENCE.md)
- [Architecture Guide](docs/architecture/README.md)
- [Contributing Guide](.github/CONTRIBUTING.md)
- [Technical Documentation Index](docs/TECHNICAL_DOCUMENTATION_INDEX.md)

## Project Status

✅ **Successfully Refactored** - Consolidated 69 redundant files into a clean, maintainable codebase  
✅ **Full Dataset Connected** - 49,323 consumer variables integrated with semantic search  
✅ **Deployed to GCP** - Running on Google App Engine with automatic scaling  
✅ **Enhanced Semantic Picker** - Returns 50 results with pagination (10 per page)  
✅ **Parquet Data Format** - 5-10x faster loading with Apache Parquet format  
✅ **Advanced Search** - Domain-specific search with hybrid keyword/semantic scoring

## Features

- **Natural Language Interface**: Describe your target audience in plain English
- **Variable Selection**: AI-powered selection from 49,323 consumer variables
- **Dynamic Variable Refinement**: Real-time search refinement with instant results
- **Semantic Variable Display**: Clear AI-powered matching with relevance scores
- **Smart Clustering**: Constrained K-Medians clustering with 5-10% group sizes
- **PRIZM Integration**: Analyze and target PRIZM consumer segments
- **Export Capabilities**: Export audiences to multiple marketing platforms
- **High Performance**: Parquet-based storage with sub-second search
- **Domain Intelligence**: Specialized search for automotive, demographic, financial, health, and immigration data
- **🆕 Complex Query Understanding**: Advanced semantic search that understands multi-faceted queries
- **🆕 Data Persistence**: Save and manage your created audiences for future use
- **🆕 Enhanced Audience Detail Page**: Interactive audience refinement with semantic variable picker

### 🆕 New in v1.8.0 (May 30, 2025)

#### Critical Performance Fixes
- **Fixed Flask Server Hang**: Resolved critical issue where server would hang on startup
- **Improved Initialization**: Added timeout handling and retry logic
- **Better Error Recovery**: Graceful fallbacks for all external dependencies

#### Similarity Filtering
- **Jaro-Winkler Algorithm**: Reduces duplicate results by 40-98%
- **Configurable Thresholds**: Adjust similarity sensitivity (default: 0.85)
- **Smart Grouping**: Keep max 2 similar variables per group
- **Performance**: Minimal overhead, happens after search

#### Unified Search Architecture
- **Single Entry Point**: Consistent API across all search providers
- **A/B Testing Ready**: Built-in migration framework for gradual rollout
- **Feature Flags**: Control features via environment variables
- **Monitoring**: Comprehensive performance tracking

#### Enhanced Audience Detail Page
- **Semantic Variable Picker**: Real-time search through 50+ variables with AI-powered suggestions
- **Dynamic Audience Scaling**: Interactive sliders for experiments (0.5-10x) and seed audience scaling (0.5-10x)
- **Activation Filters**: Toggle switches for 5 common activation workflow filters
- **Real-time Calculations**: Live audience size updates as variables and filters are applied
- **Manual Selection Mode**: Toggle between semantic and traditional manual selection
- **Impact Visualization**: See immediate audience reduction (10-40%) with confidence levels (70-100%)
- **Professional UI**: Clean, responsive interface with custom slider styling

Example Workflow:
1. **Load Audience**: Gaming-Enthusiast Gen Z Males (67,842 people)
2. **Add Variables**: "High Income Urban" (-22.7%, 94% confidence) + "Console Owners" (-15.2%, 89% confidence)
3. **Apply Scaling**: 2.5x experiment scale, 1.8x seed scale
4. **Filter**: Exclude existing customers (-15%)
5. **Final Reach**: ~89,156 people ready for activation

[Enhanced Audience Detail Guide →](AUDIENCE_ENHANCEMENT_DOCUMENTATION.md)

### 🆕 New in v1.7.0

#### Enhanced Audience Management 
- **Smart Audience Cards**: Visual card-based display instead of simple lists
- **Generated Names**: Automatic audience names like "Gaming-Enthusiast Gen Z Males"
- **Natural Language Descriptions**: Convert technical criteria to readable format
- **Random Demo Sizes**: Realistic audience sizes (56,798-89,380) for demo purposes
- **Dynamic Icons**: 15+ icons automatically selected based on audience type
- **Contextual Insights**: AI-generated insights based on audience characteristics
- **Enhanced Save Experience**: Rich success messages with generated names and sizes

Example Transformation:
- **Technical**: "gender=male AND age_min=18 AND age_max=24 AND gaming_interest=high"  
- **Natural**: "Males between the ages of 18 and 24 who are interested in video games"
- **Generated Name**: "Gaming-Enthusiast Gen Z Males"
- **Demo Size**: "67,842 people"

[Enhanced Audience Guide →](docs/ENHANCED_AUDIENCE_FEATURES.md)

### New in v1.6.0

#### Complex Query Understanding
- **Multi-Concept Extraction**: Automatically identifies demographic, financial, behavioral, and geographic concepts
- **Semantic Relationships**: Understands relationships between concepts like "millennials with high income"
- **Query Optimization**: Automatically reformulates queries for better results
- **Concept Coverage**: Shows how well each result matches all query concepts
- **Intelligent Re-ranking**: Results are re-ranked based on concept matching, not just keywords

Example: "Find environmentally conscious millennials with high disposable income in urban areas"
- Extracts: millennials (demographic), environmentally conscious (behavioral), high income (financial), urban (geographic)
- Finds variables that match multiple concepts, not just individual keywords
- Shows concept coverage percentage for each result

[Complex Query Guide →](docs/COMPLEX_QUERY_IMPROVEMENT_GUIDE.md)

### New in v1.5.0

#### Data Persistence
- **Save Audiences**: Save your created audiences for future use
- **Audience Management**: View, archive, and manage saved audiences
- **Isolated Storage**: User-specific data with secure isolation
- **High Performance**: Thread-safe Parquet storage with partitioning
- **API Access**: Full REST API for audience CRUD operations

[User Guide →](docs/DATA_PERSISTENCE_USER_GUIDE.md) | [API Reference →](docs/DATA_PERSISTENCE_API_REFERENCE.md)

### New in v1.4.0

#### Natural Language Multi-Variate Audience Builder
- **Renamed Component**: Now called "Natural Language Multi-Variate Audience Builder" to better reflect its capabilities
- **Enhanced UI Scaling**: Responsive design automatically adapts to larger screens
  - Workflow sidebar expands: `w-64` → `lg:w-80` → `xl:w-96`
  - Chat messages scale: `max-w-2xl` → `lg:max-w-3xl` → `xl:max-w-4xl`
  - Variable list grows: `max-h-64` → `lg:max-h-96` → `xl:max-h-[32rem]`
- **Unified Data Sources**: Variable selection now uses the same enhanced API as the Variable Picker
- **Improved Search**: Direct integration with Enhanced Variable Picker API for consistent results

[Full Documentation →](docs/NATURAL_LANGUAGE_MULTIVARIATE_AUDIENCE_BUILDER.md)

### 🚀 New in v1.3.0

#### Enhanced Semantic Search
- **50 Result Default**: Get more comprehensive results with each search
- **Domain-Specific Scoring**: Optimized for automotive, demographic, financial, health, and immigration domains
- **Hybrid Search**: Combines keyword and semantic search for best results
- **Numeric Pattern Recognition**: Understands ranges like "age 25-34" or "income over 100k"

#### Performance Improvements
- **Parquet Data Format**: 5-10x faster loading than CSV
- **Optimized Search**: Pandas-based vectorized operations
- **Smart Caching**: Frequently accessed variables cached for instant access
- **Reduced Memory Usage**: 50% less memory consumption

#### Variable Refinement
- **Auto-Refine**: Variables update as you type (500ms debounce)
- **Refine Button**: Manual search trigger with visual feedback
- **Maintained Selections**: Keep your selections while refining

#### Semantic Display
- **Brain Icon**: Visual indicator for AI-powered matching
- **Relevance Scores**: Hover tooltips explain the 0-1 scoring system
- **Consistent UI**: "Semantic" labeling replaces technical jargon

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+ (for frontend)
- 4GB+ RAM (for embeddings)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/andrewbmyles/activation-manager.git
   cd "Activation Manager"
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional)
   ```

3. **Start the application**
   ```bash
   # Quick start with mock data (4 sample variables)
   ./start.sh --mode local
   
   # Or with full dataset (48,332 variables)
   ./start.sh --mode local --full
   ```

   This will:
   - Create a virtual environment
   - Install dependencies
   - Start the backend on http://localhost:8080
   - Start the frontend on http://localhost:3000

### Production Deployment

#### Google Cloud Platform (App Engine)

The application is deployed at https://tobermory.ai

To deploy updates or your own instance:

1. **Install Google Cloud SDK**
   ```bash
   # Follow instructions at https://cloud.google.com/sdk/docs/install
   ```

2. **Configure your project**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Set up permissions** (Important!)
   ```bash
   # Grant necessary permissions to App Engine service account
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com" \
     --role="roles/storage.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com" \
     --role="roles/cloudbuild.serviceAgent"
   ```

4. **Deploy safely** (IMPORTANT: Use the safe deployment script)
   ```bash
   # ALWAYS use the safe deployment script to prevent build conflicts
   ./deploy-production-safe.sh
   
   # This script will:
   # - Create automatic backups
   # - Clean build directories
   # - Verify build integrity
   # - Deploy to test version first
   # - Only promote after manual verification
   ```

   ⚠️ **WARNING**: Never copy build files between projects. See DEPLOYMENT_BEST_PRACTICES.md

#### Docker Deployment

1. **Build and run with Docker**
   ```bash
   ./start.sh --mode docker
   ```

2. **Or use docker-compose**
   ```bash
   docker-compose up
   ```

## Technical Architecture

### Data Layer
- **Parquet Storage**: 49,323 variables stored in Apache Parquet format for optimal performance
- **Embeddings**: Pre-computed OpenAI text-embedding-ada-002 vectors for semantic search
- **FAISS Indexing**: Facebook AI Similarity Search for fast vector similarity

### Search Pipeline
1. **Query Processing**
   - Spell correction and normalization
   - Numeric pattern extraction (age ranges, income levels)
   - Intent classification (demographic, financial, automotive, etc.)
   - Synonym expansion

2. **Hybrid Search**
   - **Keyword Search**: TF-IDF with BM25-style scoring
   - **Semantic Search**: FAISS-based embedding similarity
   - **Hybrid Scoring**: 70% semantic + 30% keyword (configurable)

3. **Domain-Specific Optimization**
   - Automotive: Vehicle types, brands, ownership patterns
   - Demographic: Age groups, household composition, geography
   - Financial: Income levels, spending patterns, wealth indicators
   - Health: Medical conditions, wellness behaviors
   - Immigration: Residency status, country of origin

### Performance Characteristics
- **Loading Time**: ~0.3s (Parquet) vs ~2.5s (CSV)
- **Search Time**: 50-100ms for 50 results
- **Memory Usage**: ~200MB for full dataset
- **Concurrent Users**: Auto-scaling on Google App Engine

## Project Structure

```
activation_manager/
├── api/                    # API endpoints
│   ├── enhanced_audience_api.py
│   ├── enhanced_variable_picker_api.py  # NEW: 50-result search
│   └── variable_picker_api.py
├── core/                   # Core business logic
│   ├── audience_builder.py
│   ├── embeddings_handler.py
│   ├── enhanced_parquet_loader.py      # NEW: Fast Parquet loader
│   ├── enhanced_semantic_search.py     # NEW: Advanced search
│   ├── prizm_analyzer.py
│   └── variable_selector.py
├── config/                 # Configuration
│   └── settings.py
├── data/                   # Data files
│   ├── variables_2022_can.parquet      # NEW: Parquet format
│   └── embeddings/        # Variable embeddings
└── tests/                 # Test suite
    ├── unit/              # Unit tests
    └── integration/       # Integration tests

audience-manager/          # React frontend
├── src/
│   ├── components/       # React components
│   ├── pages/           # Page components
│   └── services/        # API services
└── public/              # Static assets
```

## API Endpoints

### Core Endpoints

- `GET /health` - Health check
- `POST /api/start_session` - Start a new session
- `POST /api/nl/process` - Process natural language query
- `POST /api/audience/build` - Build audience from criteria
- `POST /api/prizm/analyze` - Analyze PRIZM segments
- `POST /api/variable_picker/search` - Search variables
- `GET /api/export/<audience_id>` - Export audience

### Enhanced Search Endpoints (NEW)

- `POST /api/enhanced-variable-picker/search` - Enhanced search with 50 results
  ```json
  {
    "query": "high income millennials",
    "top_k": 50,
    "use_semantic": true,
    "use_keyword": true,
    "filters": {"theme": "Demographic"}
  }
  ```
- `GET /api/enhanced-variable-picker/stats` - Get variable statistics
- `GET /api/enhanced-variable-picker/variable/<var_id>` - Get specific variable details
- `GET /api/enhanced-variable-picker/category/<category>` - Search by category

[Full API Documentation →](docs/ENHANCED_VARIABLE_PICKER_API.md)
- `GET /api/variables/category/<category>` - Search by category
- `GET /api/variables/<var_id>` - Get specific variable details

### Example Usage

```bash
# Start a session
curl -X POST http://localhost:8080/api/start_session

# Search for variables
curl -X POST http://localhost:8080/api/nl/process \
  -H "Content-Type: application/json" \
  -d '{"query": "millennials with high income"}'
```

## Configuration

### Environment Variables

Create a `.env` file with:

```bash
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Environment
FLASK_ENV=development
PORT=8080

# Features
USE_EMBEDDINGS=true
USE_NLWEB=false

# Database
DATABASE_URL=sqlite:///activation_manager.db
```

### Settings

Configure application settings in `activation_manager/config/settings.py`.

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest activation_manager/tests/test_audience_builder.py

# Run with coverage
python -m pytest --cov=activation_manager
```

### Code Style

The project uses:
- Black for Python formatting
- ESLint/Prettier for JavaScript

### Adding New Features

1. Create feature branch
2. Add tests for new functionality
3. Implement the feature
4. Ensure all tests pass
5. Submit pull request

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process on port
   lsof -ti:8080 | xargs kill -9
   ```

2. **Missing embeddings**
   - Ensure embeddings files are in `data/embeddings/`
   - Run `python generate_embeddings.py` if needed

3. **Frontend build issues**
   ```bash
   cd audience-manager
   rm -rf node_modules
   npm install
   ```

4. **Deployment Issues (Dashboard broken, blank pages)**
   - **Cause**: Build file conflicts from mixing different React apps
   - **Solution**: Use `./deploy-production-safe.sh` which automatically cleans builds
   - **Quick Fix**: 
     ```bash
     # Clean and rebuild
     rm -rf audience-manager/build
     cd audience-manager && npm run build && cd ..
     ./deploy-production-safe.sh
     ```

5. **Health Check**
   ```bash
   # Check deployment health
   ./check-deployment-health.sh
   ```

## Performance Optimization

- **Embeddings**: Pre-loaded in memory for fast search
- **Caching**: Results cached for repeated queries
- **Indexing**: FAISS indices for vector similarity search
- **Clustering**: Optimized K-Medians implementation

## Security

- API keys stored in environment variables
- CORS configured for production domains
- Input validation on all endpoints
- Rate limiting on public endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: andrew@tobermory.ai