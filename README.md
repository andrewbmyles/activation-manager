# Activation Manager

A sophisticated audience segmentation and targeting platform that uses natural language processing and machine learning to help marketers create precise audience segments.

## 🚀 Live Demo

The application is deployed and running at: **https://feisty-catcher-461000-g2.nn.r.appspot.com**

## Project Status

✅ **Successfully Refactored** - Consolidated 69 redundant files into a clean, maintainable codebase  
✅ **Full Dataset Connected** - 48,332 consumer variables integrated with semantic search  
✅ **Deployed to GCP** - Running on Google App Engine with automatic scaling

## Features

- **Natural Language Interface**: Describe your target audience in plain English
- **Variable Selection**: AI-powered selection from 48,000+ consumer variables
- **Smart Clustering**: Constrained K-Medians clustering with 5-10% group sizes
- **PRIZM Integration**: Analyze and target PRIZM consumer segments
- **Export Capabilities**: Export audiences to multiple marketing platforms

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

The application is already deployed at https://feisty-catcher-461000-g2.nn.r.appspot.com

To deploy your own instance:

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

4. **Deploy to App Engine**
   ```bash
   # Use the provided deployment script
   ./deploy_final_solution.sh
   
   # Or deploy directly
   gcloud app deploy
   ```

#### Docker Deployment

1. **Build and run with Docker**
   ```bash
   ./start.sh --mode docker
   ```

2. **Or use docker-compose**
   ```bash
   docker-compose up
   ```

## Project Structure

```
activation_manager/
├── api/                    # API endpoints
│   ├── enhanced_audience_api.py
│   └── variable_picker_api.py
├── core/                   # Core business logic
│   ├── audience_builder.py
│   ├── embeddings_handler.py
│   ├── prizm_analyzer.py
│   └── variable_selector.py
├── config/                 # Configuration
│   └── settings.py
├── data/                   # Data files
│   └── embeddings/        # Variable embeddings
└── tests/                 # Test suite

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