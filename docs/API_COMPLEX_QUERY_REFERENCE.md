# Complex Query API Reference

This document describes the API endpoints and features for the enhanced complex query functionality in the Activation Manager.

## Overview

The complex query enhancement adds advanced natural language understanding to the variable search API, allowing for multi-faceted queries that express complex audience criteria.

## API Endpoints

### Search Variables with Advanced Processing

**Endpoint:** `POST /api/variable-picker/search`

Enhanced search endpoint that now supports complex query processing.

#### Request Body

```json
{
  "query": "Find environmentally conscious millennials with high disposable income in urban areas",
  "top_k": 50,
  "use_semantic": true,
  "use_keyword": true,
  "use_advanced_processing": true,
  "filters": {
    "category": "Demographics",
    "domain": "demographic"
  }
}
```

#### Parameters

- `query` (string, required): Natural language search query
- `top_k` (integer): Number of results to return (default: 50)
- `use_semantic` (boolean): Enable semantic search (default: true)
- `use_keyword` (boolean): Enable keyword search (default: true)
- `use_advanced_processing` (boolean): Enable complex query processing (default: true)
- `filters` (object): Optional filters by category, domain, etc.

#### Response

```json
{
  "results": [
    {
      "code": "URBAN_MILL_HIGH_INC",
      "description": "Urban Millennials High Income Green Living",
      "category": "Demographics",
      "score": 0.92,
      "original_score": 0.75,
      "matched_concepts": [
        {
          "concept": "millennials",
          "type": "demographic",
          "confidence": 0.9,
          "match_reason": "Direct match: 'millennials'"
        },
        {
          "concept": "high income",
          "type": "financial",
          "confidence": 0.9,
          "match_reason": "Financial indicator match"
        },
        {
          "concept": "urban",
          "type": "geographic",
          "confidence": 0.85,
          "match_reason": "Direct match: 'urban'"
        },
        {
          "concept": "environmentally conscious",
          "type": "behavioral",
          "confidence": 0.85,
          "match_reason": "Related term: 'green'"
        }
      ],
      "concept_coverage": {
        "demographic": 1,
        "financial": 1,
        "geographic": 1,
        "behavioral": 1
      },
      "coverage_score": 1.0,
      "relevance_explanation": "Matches demographic criteria: millennials | Matches financial profile: high income | Geographic match: urban | Indicates behaviors: environmentally conscious"
    }
  ],
  "total_found": 2547,
  "query_context": {
    "original_query": "Find environmentally conscious millennials with high disposable income in urban areas"
  },
  "advanced_context": {
    "concepts": [
      {
        "text": "environmentally conscious",
        "type": "behavioral",
        "confidence": 0.85,
        "synonyms": ["eco-friendly", "green", "sustainable"],
        "related_terms": ["environmental", "ecological", "conservation"],
        "modifiers": []
      }
    ],
    "expanded_terms": ["environmentally", "conscious", "eco-friendly", "green", "millennials"],
    "query_interpretation": "Looking for millennials in urban areas who are environmentally conscious and have high disposable income",
    "variable_patterns": [
      "MILL_*_ECO",
      "URBAN_*_GREEN",
      "HIGH_INC_*_ENVIRONMENTAL"
    ]
  },
  "query_optimization": {
    "original_query": "Find environmentally conscious millennials with high disposable income in urban areas",
    "segments": [
      {
        "text": "with high disposable income",
        "intent": "filter",
        "entities": ["financial:income", "financial:disposable"],
        "modifiers": ["intensity:high:high"],
        "weight": 0.9
      }
    ],
    "reformulations": [
      {
        "query": "environmentally conscious aware mindful millennials gen y high income affluent urban city",
        "strategy": "synonym_expansion",
        "description": "Add synonyms for key concepts"
      }
    ],
    "optimization_score": 0.85
  }
}
```

### Get Concept Suggestions

**Endpoint:** `POST /api/variable-picker/concepts/suggestions`

Get concept-based variable suggestions for a complex query.

#### Request Body

```json
{
  "query": "wealthy urban families interested in green technology and organic products"
}
```

#### Response

```json
{
  "by_concept": {
    "wealthy": [
      {
        "code": "INCOME_150K_PLUS",
        "description": "Household Income $150,000+",
        "match_reason": "Direct match: 'wealthy'"
      },
      {
        "code": "HIGH_NET_WORTH",
        "description": "High Net Worth Individuals",
        "match_reason": "Synonym match: 'affluent'"
      }
    ],
    "urban": [
      {
        "code": "URBAN_CORE",
        "description": "Urban Core Residents",
        "match_reason": "Direct match: 'urban'"
      }
    ],
    "families": [
      {
        "code": "FAMILY_WITH_CHILDREN",
        "description": "Families with Children Under 18",
        "match_reason": "Direct match: 'families'"
      }
    ]
  },
  "combinations": [
    {
      "code": "WEALTHY_URBAN_FAM_GREEN",
      "description": "Wealthy Urban Families - Green Technology Adopters",
      "matched_concepts": ["wealthy", "urban", "families", "green technology"],
      "match_count": 4
    }
  ],
  "missing_concepts": [
    {
      "concept": "organic products",
      "type": "behavioral",
      "alternatives": ["natural", "eco-friendly", "sustainable"]
    }
  ]
}
```

## Advanced Features

### Concept Types

The system recognizes and categorizes concepts into the following types:

- **demographic**: Age groups, generations, family status
- **financial**: Income levels, wealth indicators, spending patterns
- **behavioral**: Lifestyle choices, interests, activities
- **geographic**: Location types, urban/rural, regions
- **temporal**: Time-based concepts, recency, frequency
- **psychographic**: Values, attitudes, beliefs

### Query Optimization Strategies

When `use_advanced_processing` is enabled, the system applies several optimization strategies:

1. **Emphasis**: Duplicates important terms for stronger matching
2. **Synonym Expansion**: Adds related terms and synonyms
3. **Restructuring**: Reorders query segments by logical priority
4. **Simplification**: Creates simplified versions without modifiers

### Concept Scoring

Variables are scored based on concept matching:

- Base score from keyword/semantic matching
- Concept boost for each matched concept (weighted by type)
- Multi-concept bonus for matching multiple concepts:
  - 2 concepts: +20% bonus
  - 3 concepts: +40% bonus
  - 4+ concepts: +60% bonus
- Coverage penalty if important concepts are missing

### Integration Examples

#### Python Example

```python
import requests

# Search with complex query
response = requests.post(
    "https://your-domain.com/api/variable-picker/search",
    json={
        "query": "Find environmentally conscious millennials with high disposable income in urban areas",
        "top_k": 50,
        "use_advanced_processing": True
    }
)

results = response.json()

# Display results with concept coverage
for result in results['results'][:10]:
    print(f"{result['code']}: {result['description']}")
    print(f"  Coverage: {result['coverage_score']:.0%}")
    print(f"  Explanation: {result['relevance_explanation']}")
```

#### JavaScript Example

```javascript
// Get concept suggestions
const response = await fetch('/api/variable-picker/concepts/suggestions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'wealthy urban families interested in green technology'
  })
});

const suggestions = await response.json();

// Display suggestions by concept
Object.entries(suggestions.by_concept).forEach(([concept, variables]) => {
  console.log(`\n${concept}:`);
  variables.forEach(v => {
    console.log(`  - ${v.code}: ${v.description}`);
  });
});
```

## Best Practices

1. **Complex Queries**: Use for queries with 4+ words expressing multiple concepts
2. **Concept Coverage**: Look for variables with high coverage scores (>75%)
3. **Fallback**: If no high-coverage results, review individual concept matches
4. **Performance**: Complex processing adds ~100-200ms latency; disable for simple queries
5. **Caching**: Cache results for common complex queries

## Error Handling

### No Results

```json
{
  "results": [],
  "total_found": 0,
  "advanced_context": {
    "concepts": [...],
    "query_interpretation": "...",
    "message": "No variables found matching all concepts. Try broadening your search."
  }
}
```

### Processing Error

```json
{
  "error": "Advanced processing failed",
  "fallback_results": [...],
  "message": "Results shown using standard search"
}
```

## Configuration

### Environment Variables

- `ENABLE_ADVANCED_QUERY_PROCESSING`: Enable/disable globally (default: true)
- `MAX_CONCEPTS_PER_QUERY`: Maximum concepts to extract (default: 10)
- `CONCEPT_CONFIDENCE_THRESHOLD`: Minimum confidence for concepts (default: 0.5)

### Search Configuration

```python
# In SearchConfig
concept_type_weights = {
    'demographic': 1.0,
    'financial': 0.9,
    'behavioral': 0.85,
    'geographic': 0.8,
    'temporal': 0.7
}

multi_concept_bonus = 0.2  # Per additional concept
min_important_coverage = 0.5  # Minimum coverage for important concepts
```