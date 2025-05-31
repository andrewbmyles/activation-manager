# Complex Query Semantic Search Improvement Guide

## Overview

This guide explains how to enhance your semantic search system to better handle complex, multi-faceted queries by understanding concepts, relationships, and user intent rather than just matching keywords.

## Problem Statement

Current semantic search systems often struggle with complex queries like:
- "Find environmentally conscious millennials with high disposable income in urban areas"

These queries contain multiple concepts that need to be understood together:
- **Behavioral**: environmentally conscious
- **Demographic**: millennials
- **Financial**: high disposable income
- **Geographic**: urban areas

## Solution Architecture

### 1. Advanced Query Processor

The `AdvancedQueryProcessor` extracts semantic concepts from queries:

```python
from activation_manager.core.advanced_query_processor import AdvancedQueryProcessor

processor = AdvancedQueryProcessor()
context = processor.expand_query_semantically(
    "Find environmentally conscious millennials with high disposable income in urban areas"
)

# Extracted concepts:
# - environmentally_conscious (behavioral, confidence: 0.85)
# - millennials (demographic, confidence: 0.9)
# - high income (financial, confidence: 0.9)
# - urban (geographic, confidence: 0.85)
```

### 2. Concept-Aware Scoring

The enhanced scoring system understands concept relationships:

```python
# Variables matching multiple concepts score higher
# Example: A variable like "Urban Millennials Income $100k+" would score highly because it matches:
# - Demographic (millennials)
# - Financial (high income)
# - Geographic (urban)
```

### 3. Query Optimization

The `SemanticQueryOptimizer` reformulates queries for better results:

```python
from activation_manager.core.semantic_query_optimizer import SemanticQueryOptimizer

optimizer = SemanticQueryOptimizer()
optimized = optimizer.optimize_query(complex_query)

# Generates variations like:
# - "millennials high income urban environmental"  (entity focus)
# - "environmentally conscious aware mindful millennials affluent wealthy urban city"  (synonym expansion)
```

## Implementation Steps

### Step 1: Install Dependencies

```bash
# If using NLP features
pip install spacy
python -m spacy download en_core_web_sm
```

### Step 2: Update Your Search API

Modify your existing search to use the enhanced version:

```python
# In your API handler
from activation_manager.core.enhanced_semantic_search_v2 import create_enhanced_search_v2

# Initialize enhanced search
search_engine = create_enhanced_search_v2(
    variables=your_variables,
    embeddings=your_embeddings,
    openai_api_key=your_api_key
)

# Perform search with advanced processing
results = search_engine.search(
    query=user_query,
    top_k=50,
    use_advanced_processing=True  # Enable concept extraction
)
```

### Step 3: Enhanced Results Display

Show users why results match their query:

```javascript
// In your frontend
results.forEach(result => {
    console.log(`${result.code}: ${result.description}`);
    
    // Show matched concepts
    if (result.matched_concepts) {
        console.log('Matches:');
        result.matched_concepts.forEach(mc => {
            console.log(`  - ${mc.concept} (${mc.type}): ${mc.match_reason}`);
        });
    }
    
    // Show concept coverage
    if (result.coverage_score) {
        console.log(`Concept Coverage: ${(result.coverage_score * 100).toFixed(0)}%`);
    }
});
```

## Key Features

### 1. Concept Extraction

Automatically identifies key concepts in queries:

| Query Text | Extracted Concept | Type | Confidence |
|------------|------------------|------|------------|
| "millennials" | millennials | demographic | 0.9 |
| "environmentally conscious" | environmental_consciousness | behavioral | 0.85 |
| "high disposable income" | high_income | financial | 0.9 |
| "urban areas" | urban | geographic | 0.85 |

### 2. Concept Mappings

Pre-built mappings for common concepts:

```python
'millennials': {
    'birth_years': (1981, 1996),
    'age_range_2024': (28, 43),
    'characteristics': ['digital natives', 'tech-savvy', 'social media'],
    'values': ['experiences', 'sustainability', 'authenticity'],
    'alternative_names': ['gen y', 'echo boomers']
}
```

### 3. Multi-Concept Scoring

Variables matching multiple concepts receive bonus scores:
- 1 concept match: base score
- 2 concept matches: +20% bonus
- 3 concept matches: +40% bonus
- 4 concept matches: +60% bonus

### 4. Query Reformulation Strategies

- **Emphasis**: Duplicate important terms
- **Synonym Expansion**: Add related terms
- **Restructuring**: Reorder by logical priority
- **Simplification**: Remove modifiers for broader results

## Example Results

### Query: "Find environmentally conscious millennials with high disposable income in urban areas"

**Standard Search Results:**
```
1. [INCOME_100K] Household Income $100,000+
2. [AGE_25_34] Age 25-34
3. [URBAN_POP] Urban Population
```

**Enhanced Search Results:**
```
1. [URBAN_MILL_HIGH_INC] Urban Millennials High Income Green Living
   - Matched: environmental (behavioral), millennials (demographic), 
              high income (financial), urban (geographic)
   - Coverage: 100%
   
2. [ECO_CONSCIOUS_25_34_CITY] Eco-Conscious Age 25-34 City Dwellers $100k+
   - Matched: environmental (behavioral), millennials (demographic), 
              high income (financial), urban (geographic)
   - Coverage: 100%
   
3. [HIGH_INC_YOUNG_PROF_GREEN] High Income Young Professionals Environmental Values
   - Matched: millennials (demographic), high income (financial), 
              environmental (behavioral)
   - Coverage: 75%
```

## Configuration Options

### Search Configuration

```python
# In SearchConfig
class SearchConfig:
    # Concept weights by type
    concept_type_weights = {
        'demographic': 1.0,
        'financial': 0.9,
        'behavioral': 0.85,
        'geographic': 0.8,
        'temporal': 0.7
    }
    
    # Multi-concept bonuses
    multi_concept_bonus = 0.2  # Per additional concept
    
    # Coverage penalties
    min_important_coverage = 0.5  # Minimum coverage for important concepts
```

### Query Processing Options

```python
# Enable/disable features
search_options = {
    'use_advanced_processing': True,
    'extract_concepts': True,
    'optimize_query': True,
    'generate_reformulations': True,
    'apply_concept_scoring': True
}
```

## Performance Considerations

1. **Caching**: Cache concept extractions for repeated queries
2. **Batch Processing**: Process multiple query variations in parallel
3. **Selective Enhancement**: Only use advanced processing for queries with 4+ words
4. **Index Optimization**: Pre-compute concept matches for frequent searches

## Testing Complex Queries

Use the provided test script:

```bash
python test_complex_query_search.py
```

This will demonstrate:
- Concept extraction
- Query optimization
- Enhanced scoring
- Result explanations

## Migration from Basic Search

### Phase 1: Add Concept Extraction
- Deploy `AdvancedQueryProcessor`
- Log extracted concepts without changing ranking

### Phase 2: Implement Concept Scoring
- Add `ConceptAwareScorer`
- A/B test with subset of users

### Phase 3: Full Integration
- Enable query optimization
- Show concept matches in UI
- Monitor user engagement

## Troubleshooting

### Issue: Poor Concept Extraction
**Solution**: Add domain-specific concept mappings

### Issue: Too Many False Positives
**Solution**: Increase concept confidence thresholds

### Issue: Slow Performance
**Solution**: Limit concept extraction to first 100 words

## Future Enhancements

1. **Machine Learning**: Train concept extraction on user feedback
2. **Personalization**: Adjust concept weights based on user history
3. **Multi-language**: Support concept extraction in other languages
4. **Industry-Specific**: Add vertical-specific concept mappings

## Conclusion

These enhancements transform your semantic search from simple keyword matching to true semantic understanding, enabling it to handle complex, multi-faceted queries effectively. The system now understands not just what users are searching for, but the relationships and intent behind their queries.