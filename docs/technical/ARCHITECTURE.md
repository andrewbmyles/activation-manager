# Technical Architecture

## System Overview

The Activation Manager is a cloud-native application built with modern web technologies and deployed on Google Cloud Platform. It consists of a React frontend, Flask backend API, and integrates with Claude AI for natural language processing.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users (Browser)                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Load Balancer                           │
│                  (SSL/TLS Termination)                          │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    │                           │
                    ▼                           ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│     Cloud Run            │    │     Cloud Run            │
│     Frontend             │    │     Backend API          │
│  (audience-manager)      │    │ (audience-manager-api)   │
│                          │    │                          │
│  - React SPA            │    │  - Flask REST API       │
│  - Express Server       │    │  - Session Auth         │
│  - Static Assets        │    │  - CORS Enabled         │
└──────────────────────────┘    └──────────────────────────┘
                    │                           │
                    │         API Calls         │
                    └──────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │    External Services     │
                    │  - Claude AI API         │
                    │  - Future: Database      │
                    └──────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Tailwind CSS
- **State Management**: React Context + TanStack Query
- **Routing**: React Router v6
- **Build Tool**: Create React App
- **Icons**: Lucide React
- **HTTP Client**: Fetch API

### Backend
- **Framework**: Flask 3.0
- **Language**: Python 3.11
- **Authentication**: Flask-Session with Werkzeug password hashing
- **CORS**: Flask-CORS
- **Server**: Gunicorn (production)
- **Data Processing**: NumPy, Pandas, scikit-learn

### Infrastructure
- **Cloud Provider**: Google Cloud Platform
- **Compute**: Cloud Run (serverless containers)
- **Container Registry**: Artifact Registry
- **Build System**: Cloud Build
- **DNS/CDN**: Cloudflare
- **SSL**: Google-managed certificates
- **Monitoring**: Cloud Logging, Cloud Monitoring

## Embeddings Infrastructure

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    Embeddings Service                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Variables  │  │  OpenAI API  │  │   FAISS Index      │   │
│  │   (48.3k)   │→ │ Embeddings   │→ │ (1536 dimensions)  │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
│         │                                       │                │
│         ↓                                       ↓                │
│  ┌─────────────┐                    ┌─────────────────────┐   │
│  │   TF-IDF    │                    │  Similarity Search │   │
│  │   Vectors   │                    │   (Cosine/L2)      │   │
│  └─────────────┘                    └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Embedding Generation**
   - Model: OpenAI text-embedding-3-small
   - Batch size: 100 variables per request
   - Total processing time: ~10 minutes for full dataset
   - Storage format: JSONL with base64-encoded vectors

2. **Vector Storage**
   - FAISS IndexFlatL2 for exact similarity search
   - Memory usage: ~300MB for full index
   - Load time: <2 seconds from disk

3. **Search Pipeline**
   ```python
   Query → Embed → Search FAISS → Combine with TF-IDF → Rank → Return Top-K
   ```

4. **Caching Strategy**
   - LRU cache for frequent queries
   - TTL: 1 hour for embedding results
   - Memory limit: 100MB cache size

## Component Details

### Frontend Components

#### Core Components
```
src/
├── App.tsx                 # Main app with routing and auth
├── components/
│   ├── Login.tsx          # Authentication component
│   ├── Layout.tsx         # Main layout with navigation
│   ├── EnhancedNLAudienceBuilder.tsx  # NL interface
│   ├── VariableSelector.tsx           # Variable selection
│   └── ErrorBoundary.tsx              # Error handling
├── pages/
│   ├── Dashboard.tsx      # Main dashboard
│   ├── AudienceBuilder.tsx # Audience creation
│   └── Analytics.tsx      # Analytics views
└── services/
    └── api.ts            # API client
```

#### Key Features
- **Authentication Flow**: Session-based with secure cookies
- **Responsive Design**: Mobile-first approach
- **Error Handling**: Global error boundary
- **Loading States**: Skeleton screens and spinners

### Backend API

#### API Endpoints
```
GET  /                      # API info
GET  /health               # Health check (public)
POST /api/auth/login       # User login
POST /api/auth/logout      # User logout
GET  /api/auth/status      # Auth status

# Protected endpoints (require auth)
POST /api/nl/start_session # Start NL session
POST /api/nl/process       # Process NL query
GET  /api/audiences        # List audiences
POST /api/audiences        # Create audience
GET  /api/export/:id       # Export CSV

# Variable Picker endpoints
POST /api/variable-picker/start     # Start variable selection session
POST /api/variable-picker/process   # Process natural language query
POST /api/variable-picker/confirm   # Confirm selected variables
GET  /api/variable-picker/export    # Export confirmed variables
```

#### Security Features
- **Password Hashing**: Werkzeug with salted hashes
- **Session Management**: Secure HTTP-only cookies
- **CORS**: Restricted to allowed origins
- **Input Validation**: Request schema validation

### Data Processing Pipeline

```
User Query → NL Processing → Variable Selection → Clustering → Segments
     │             │                │                 │           │
     │             │                ├─── TF-IDF ────→│           │
     │             │                └─ Embeddings ──→│           │
     └─────────────┴────────────────┴─────────────────┴───────────┘
                            Activation Manager Core
                                    │
                         ┌──────────┴──────────┐
                         │  48,333 Variables   │
                         │  130MB+ Embeddings  │
                         └─────────────────────┘
```

#### Variable Selection Algorithm

The system employs a hybrid approach for searching through 48,000+ variables:

1. **TF-IDF Vectorization**: Convert variable descriptions to vectors
   - Processes 48,333 variables (Demostats: 36,610, PRIZM: 68, Social Values: 11,655)
   - Optimized for real-time search with pre-computed indices

2. **Embeddings-Based Semantic Search**: 
   - Uses OpenAI text-embedding-3-small (1536 dimensions)
   - FAISS vector index for efficient similarity search
   - Enables semantic understanding beyond keyword matching

3. **Hybrid Scoring**:
   - Combines TF-IDF scores with embedding similarity
   - Weighted approach: 60% semantic, 40% keyword
   - Returns top-k most relevant variables

4. **Performance Optimizations**:
   - Lazy loading of embeddings (130MB+ dataset)
   - In-memory caching of frequent queries
   - Batch processing for multiple queries

#### Clustering Algorithm
- **Method**: K-Medians with constraints
- **Constraints**: 5-10% segment size limits
- **Features**: Normalized and weighted by relevance
- **Output**: Balanced segments with demographic profiles

## Deployment Architecture

### Container Strategy
- **Frontend**: Node.js Express server serving React build
- **Backend**: Python Flask app with Gunicorn
- **Base Images**: Official slim variants for security

### Scaling Configuration
```yaml
Frontend:
  Min Instances: 0
  Max Instances: 10
  Memory: 512Mi
  CPU: 1
  Concurrency: 1000

Backend:
  Min Instances: 0
  Max Instances: 10
  Memory: 256Mi
  CPU: 1
  Concurrency: 100
```

### Environment Configuration
- **Development**: Local with hot reload
- **Staging**: Separate GCP project
- **Production**: tobermory.ai domain

## Security Architecture

### Authentication Flow
```
1. User enters credentials
2. Frontend sends POST to /api/auth/login
3. Backend validates credentials
4. Backend creates secure session
5. Session cookie sent to browser
6. Subsequent requests include session
7. Backend validates session on each request
```

### Security Measures
1. **HTTPS Only**: Enforced at load balancer
2. **Secure Cookies**: HTTP-only, secure, SameSite
3. **CORS Policy**: Whitelist specific origins
4. **Input Sanitization**: All inputs validated
5. **Rate Limiting**: Planned implementation
6. **Secret Management**: Environment variables

## Data Flow

### Audience Creation Flow
```
1. User describes audience in natural language
2. Frontend sends query to backend
3. Backend processes with Claude AI
4. Variable selector finds relevant variables
5. Clustering algorithm creates segments
6. Results returned to frontend
7. User can export as CSV
```

### Session Management
- **Storage**: Server-side sessions
- **Identifier**: Secure random token
- **Expiration**: 24 hours (configurable)
- **Cleanup**: Automatic expired session removal

## Performance Optimization

### Frontend
- **Code Splitting**: Lazy loading of routes
- **Asset Optimization**: Minified and compressed
- **Caching**: Browser cache headers
- **CDN**: Cloudflare caching

### Backend
- **Connection Pooling**: Reuse connections
- **Response Caching**: Cache repeated queries
- **Async Processing**: Non-blocking I/O
- **Resource Limits**: Memory and CPU caps

### Large Dataset Optimizations (48k+ Variables)

1. **Memory Management**
   - Lazy loading of embeddings on first search
   - Partial index loading for specific categories
   - Memory-mapped files for large indices

2. **Search Performance**
   - Pre-computed TF-IDF matrices
   - Batch embedding queries
   - Parallel search across indices
   - Response time: <100ms for 95th percentile

3. **Startup Optimization**
   - Progressive loading: metadata → TF-IDF → embeddings
   - Background index warming
   - Total startup time: <5 seconds

4. **Query Optimization**
   - Early termination for high-confidence matches
   - Approximate nearest neighbor search for scale
   - Result caching with smart invalidation

## Monitoring and Observability

### Metrics
- **Application**: Response times, error rates
- **Infrastructure**: CPU, memory, requests
- **Business**: User sessions, audiences created

### Logging
```
Frontend → Browser Console → Cloud Logging
Backend → Python Logger → Cloud Logging
```

### Health Checks
- **Endpoint**: `/health`
- **Frequency**: Every 10 seconds
- **Timeout**: 5 seconds
- **Failure Threshold**: 3 consecutive

## Disaster Recovery

### Backup Strategy
- **Code**: Git repository (GitHub)
- **Data**: Currently stateless (future: Cloud SQL backups)
- **Configuration**: Version controlled

### Recovery Procedures
1. **Service Failure**: Auto-restart by Cloud Run
2. **Region Failure**: Manual failover to backup region
3. **Data Loss**: Restore from backups
4. **Security Breach**: Rotate secrets, audit logs

## Future Enhancements

### Planned Improvements
1. **Database Integration**: Cloud SQL for persistence
2. **Caching Layer**: Redis for session storage
3. **Queue System**: Cloud Tasks for async processing
4. **File Storage**: Cloud Storage for exports
5. **API Gateway**: Centralized API management

### Scalability Considerations
- **Horizontal Scaling**: Add more instances
- **Database Sharding**: Partition by tenant
- **CDN Expansion**: Multi-region deployment
- **Microservices**: Split monolith if needed