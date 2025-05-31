# Audience Builder - Natural Language Audience Segmentation

A sophisticated audience segmentation system that uses Claude AI to interpret natural language requests and create targeted customer segments using constrained K-Medians clustering.

## Overview

The Audience Builder allows marketing professionals to describe their target audience in plain English and automatically generates actionable customer segments. The system combines:

- **Natural Language Understanding**: Claude interprets user requests
- **Variable Selection**: Maps descriptions to available data variables
- **Constrained Clustering**: Creates balanced segments (5-10% each)
- **Actionable Insights**: Provides profiles for each segment

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask API server:**
   ```bash
   python audience_api.py
   ```

3. **Test the system:**
   ```bash
   python test_audience_builder.py
   ```

## Architecture

### Core Components

1. **audience_builder.py** - Main implementation
   - `VariableSelector`: Analyzes requests and suggests variables
   - `DataRetriever`: Fetches data for selected variables
   - `ConstrainedKMedians`: Clustering with size constraints
   - `AudienceBuilder`: Orchestrates the entire process

2. **variable_catalog.py** - Variable metadata
   - Maps Q-codes to descriptions
   - Categorizes by type (demographic, behavioral, etc.)

3. **audience_api.py** - REST API endpoints
   - `/api/variable_selector` - Suggest relevant variables
   - `/api/cluster_analyzer` - Perform clustering
   - `/api/analyze` - Complete analysis in one call

4. **claude_nlweb_integration.py** - Claude AI integration
   - Natural language processing
   - NLWeb browser interface

## Usage Examples

### API Usage

```bash
# Analyze a natural language request
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Find environmentally conscious millennials with high income in urban areas",
    "auto_select": true
  }'
```

### Python Usage

```python
from audience_builder import AudienceBuilder
from variable_catalog import get_full_catalog

# Initialize
builder = AudienceBuilder(
    variable_catalog=get_full_catalog(),
    data_path="path/to/data.csv"
)

# Analyze request
request = "Tech-savvy urban professionals interested in premium brands"
suggestions = builder.variable_selector.analyze_request(request)

# Build audience
selected_vars = [var['code'] for var in suggestions[:7]]
results = builder.build_audience(request, selected_vars)
profiles = builder.get_group_profiles()
```

## Data Format

The system expects CSV data with:
- `PostalCode`: Postal code
- `LATITUDE`, `LONGITUDE`: Geographic coordinates
- `PRIZM_SEGMENT`: Consumer segment code
- Q-coded variables: Various demographic/behavioral metrics

## Clustering Constraints

The K-Medians algorithm ensures:
- Minimum segment size: 5% of total population
- Maximum segment size: 10% of total population
- Balanced, actionable segments for marketing

## Integration with NLWeb

The system integrates with NLWeb through:
1. Claude API for natural language understanding
2. REST endpoints for tool execution
3. JavaScript interface for browser integration

## API Endpoints

### GET /api/health
Health check endpoint

### GET /api/variables
List all available variables grouped by type

### POST /api/variable_selector
Analyze user request and suggest relevant variables

### POST /api/analyze
Complete analysis: variable selection + clustering

## Next Steps

1. **Production Deployment**:
   - Set up proper authentication
   - Configure production database
   - Implement caching for performance

2. **Enhanced Features**:
   - Export segments to marketing platforms
   - Schedule recurring segmentation
   - A/B testing capabilities

3. **Monitoring**:
   - Track usage metrics
   - Monitor clustering performance
   - Collect user feedback

## Security Notes

- Store API keys in environment variables
- Implement rate limiting
- Add authentication for production use
- Sanitize user inputs

## Support

For questions or issues, please refer to the documentation in CLAUDE.md or create an issue in the repository.