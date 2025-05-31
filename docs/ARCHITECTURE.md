# Activation Manager Architecture

## System Overview

The Activation Manager is a web-based audience segmentation platform that uses natural language processing and semantic search to help users find relevant demographic and behavioral variables from a database of 49,000+ variables.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Login     │  │  Dashboard   │  │  NL Multi-Variate │  │
│  │   Screen    │  │              │  │  Audience Builder │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Google App Engine                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Flask Backend (main.py)             │   │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐ │   │
│  │  │  API       │  │   Search    │  │  Embeddings  │ │   │
│  │  │  Endpoints │  │   Engine    │  │   Handler    │ │   │
│  │  └────────────┘  └─────────────┘  └──────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage                            │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  CSV Data    │  │ Parquet Data │  │  GCS Embeddings │   │
│  │  (49k vars)  │  │  (Optimized) │  │   (Optional)    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer (React + TypeScript)

**Key Components:**
- `App.tsx` - Main application router and authentication
- `Layout.tsx` - Navigation and layout wrapper
- `VariablePicker.tsx` - NL Multi-Variate Audience Builder interface
- `EnhancedNLAudienceBuilder.tsx` - Natural language input interface

**State Management:**
- Local component state using React hooks
- No global state management (Redux/Context not needed)

**API Communication:**
- Fetch API for HTTP requests
- Proxy configuration for development (port 3000 → 8080)

### 2. Backend Layer (Flask + Python)

**Core Modules:**

```
backend/
├── main.py                    # Flask application & API routes
├── activation_manager/
│   ├── core/
│   │   ├── csv_variable_loader.py      # CSV data loading
│   │   ├── parquet_variable_loader.py  # Parquet data loading
│   │   ├── embeddings_handler.py       # Embedding operations
│   │   └── enhanced_semantic_search.py # Semantic search
│   └── api/
│       └── enhanced_variable_picker_api.py # Enhanced search API
```

**Request Flow:**
1. Request → Flask Router
2. Router → Handler Function
3. Handler → Data Loader/Search Engine
4. Search Engine → Results
5. Results → JSON Response

### 3. Data Layer

**Variable Data Storage:**
- Primary: CSV file (49,323 variables)
- Optimized: Parquet format for faster loading
- Location: Deployed with application

**Embeddings Storage:**
- Optional: Google Cloud Storage
- Format: NumPy arrays
- Usage: Enhanced semantic search

**Data Schema:**
```python
{
    "VarId": "string",          # Unique identifier
    "Description": "string",     # Variable description
    "Category": "string",        # Main category
    "Theme": "string",          # Theme/subcategory
    "Type": "string",           # Variable type
    "Context": "string"         # Additional context
}
```

## Deployment Architecture

### Google App Engine Configuration

```yaml
runtime: python311
instance_class: F4

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.65
```

**Key Features:**
- Auto-scaling based on load
- Warm instance for quick response
- Static file serving with caching
- HTTPS by default

### Build Process

1. **Frontend Build:**
   ```bash
   cd audience-manager
   npm run build
   ```
   - Outputs to `audience-manager/build/`
   - Minified and optimized

2. **Backend Deployment:**
   ```bash
   gcloud app deploy app_production.yaml
   ```
   - Uploads entire project
   - Excludes files in `.gcloudignore`

## Search Architecture

### 1. Keyword Search (Default)
- Fast text matching on descriptions
- Category and theme filtering
- Relevance scoring based on match quality

### 2. Semantic Search (Optional)
- Pre-computed embeddings
- Cosine similarity matching
- Falls back to keyword if unavailable

### Search Flow:
```
User Query
    ↓
Text Processing
    ↓
Parallel Search
    ├── Keyword Search
    └── Semantic Search (if available)
    ↓
Result Merging & Deduplication
    ↓
Relevance Scoring
    ↓
Top-K Selection
    ↓
Response
```

## Security Considerations

1. **Authentication:**
   - Simple password protection
   - Session-based authentication
   - Password not exposed in UI

2. **API Security:**
   - CORS enabled for all origins
   - Input validation on all endpoints
   - Error messages sanitized

3. **Data Security:**
   - No PII stored
   - Variables are anonymous demographic codes
   - No user data persistence

## Performance Optimizations

1. **Data Loading:**
   - Parquet format 5-10x faster than CSV
   - Lazy loading of embeddings
   - In-memory caching

2. **Search Performance:**
   - Pandas vectorized operations
   - Limited result sets (max 100)
   - Efficient text matching

3. **Frontend Performance:**
   - Code splitting
   - Lazy component loading
   - Optimized bundle size

## Scalability

**Horizontal Scaling:**
- Stateless design
- No server-side sessions
- Google App Engine auto-scaling

**Vertical Scaling:**
- F4 instance class (2.4GHz, 1GB RAM)
- Can upgrade to F4_HIGHMEM if needed

**Limitations:**
- In-memory data storage
- No distributed caching
- Single region deployment

## Monitoring & Logging

**Available Metrics:**
- Google App Engine dashboard
- Request logs via `gcloud app logs`
- Error tracking in application logs

**Health Checks:**
- `/api/health` endpoint
- `/api/embeddings-status` for feature status

## Future Architecture Improvements

1. **Caching Layer:**
   - Redis for search results
   - CDN for static assets

2. **Database Migration:**
   - Move to Cloud SQL or Firestore
   - Better query capabilities

3. **Microservices:**
   - Separate search service
   - Independent embedding service

4. **Enhanced Monitoring:**
   - Application Performance Monitoring
   - Custom metrics dashboard