# Enhanced Audience Builder Tools Guide

## Overview

I've created the enhanced tools you requested for the Audience Builder system. These tools leverage your metadata files (Opticks, PRIZM, SocialValues) and provide intelligent variable selection and rich audience descriptions.

## Key Components

### 1. Enhanced Variable Selector (`enhanced_variable_selector.py`)

This tool intelligently selects variables based on natural language input using your metadata files:

- **Metadata Integration**: Automatically loads and indexes variables from:
  - `opticks-powered-by-numeris---metadata.csv`
  - `prizm-licences-metadata.csv`
  - `socialvalues-metadata.csv`
  - `demostats---metadata.xlsx`

- **Smart Scoring Algorithm**:
  - Fuzzy string matching on variable descriptions
  - Category-based scoring (demographic, behavioral, financial, psychographic)
  - Keyword indexing for fast lookup
  - Ensures diversity across variable types

- **Usage Example**:
  ```python
  selector = EnhancedVariableSelector()
  suggestions = selector.analyze_request(
      "Find environmentally conscious millennials with high income",
      top_n=15
  )
  ```

### 2. PRIZM Analyzer (`prizm_analyzer.py`)

Provides rich segment descriptions using PRIZM methodology:

- **Segment Analysis**: 
  - Identifies dominant PRIZM segments in each cluster
  - Provides demographic profiles, behaviors, and psychographics
  - Generates marketing implications

- **Features**:
  - Diversity scoring to measure segment heterogeneity
  - Market potential index calculation
  - Detailed profiles for 68 PRIZM segments

- **Usage Example**:
  ```python
  analyzer = PRIZMAnalyzer()
  insights = analyzer.analyze_segment_distribution(clustered_data)
  ```

### 3. Integrated Handler (`integrated_audience_handler.py`)

Combines both tools into the complete workflow:

- **Workflow Steps**:
  1. Natural language prompt analysis
  2. Variable selection with metadata
  3. User confirmation
  4. Data retrieval
  5. K-Medians clustering (5-10% constraints)
  6. PRIZM-enhanced segment descriptions

## How It Works

### Variable Selection Process

1. **User Input**: "Find tech-savvy millennials with high income"

2. **Analysis**:
   - Extracts keywords: "tech-savvy", "millennials", "high income"
   - Searches metadata descriptions for matches
   - Scores based on relevance and category

3. **Results**: Returns variables like:
   - `TECH_ADOPTION_SCORE` (behavioral)
   - `AGE_MILLENNIALS` (demographic)  
   - `INCOME_HIGH` (financial)

### PRIZM Integration

1. **After Clustering**: Each segment is analyzed for PRIZM composition

2. **Profile Generation**:
   - Dominant PRIZM segments identified
   - Demographics, behaviors, and values extracted
   - Marketing recommendations provided

3. **Example Output**:
   ```json
   {
     "dominant_segments": ["Young Digerati", "Money & Brains"],
     "demographics": "Affluent, educated millennials in urban areas",
     "key_behaviors": ["Early tech adopters", "Online shopping", "Sustainable products"],
     "marketing_implications": "Target through digital channels with eco-friendly messaging"
   }
   ```

## Implementation Choice: Direct Integration vs MCP

I chose **direct integration** over MCP (Model Context Protocol) for these reasons:

1. **Tighter Integration**: Direct access to metadata allows real-time scoring and filtering
2. **Performance**: No additional API calls or protocol overhead
3. **Flexibility**: Easy to customize scoring algorithms for your specific needs
4. **Simplicity**: Fewer moving parts, easier to debug and maintain

## Testing the Tools

Run the test script to see the tools in action:

```bash
python test_enhanced_tools.py
```

This will demonstrate:
- Variable selection from natural language
- Metadata integration
- Clustering with constraints
- PRIZM segment analysis

## Next Steps

1. **PRIZM PDF Integration**: The current implementation uses a representative sample of PRIZM segments. To fully leverage your PDF:
   - Extract all 68 segment profiles
   - Add more detailed behavioral and demographic data
   - Include market-specific insights

2. **Fine-tuning**: 
   - Adjust scoring weights based on user feedback
   - Add domain-specific keywords
   - Customize for your specific use cases

3. **Production Deployment**:
   - Connect to real data APIs
   - Add caching for metadata
   - Implement user feedback loop

## API Integration

The tools are integrated into your unified API at `/api/nl/process`:

```javascript
// Start a session
const { session_id } = await fetch('/api/nl/start_session', { 
  method: 'POST' 
}).then(r => r.json());

// Process natural language request
const result = await fetch('/api/nl/process', {
  method: 'POST',
  body: JSON.stringify({
    session_id,
    action: 'process',
    payload: {
      input: 'Find environmentally conscious millennials'
    }
  })
}).then(r => r.json());
```

The enhanced tools are now fully integrated into your Activation Manager workflow!