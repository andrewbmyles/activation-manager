# Plan to Fix Similar Variables Issue

## Problem Analysis

Based on the screenshot analysis, the current similarity filtering is not catching variables that share:
1. **Common base patterns** (e.g., "Contact with friends [Pst Mth]")
2. **Same semantic scores** (0.5 for all similar variables)
3. **Minor variations** in descriptors (All, Most, About half, A few, None)

### Current Issue
The Jaro-Winkler algorithm with 0.85 threshold is not aggressive enough to catch these variations because:
- The full strings are too different due to the suffix variations
- The algorithm compares entire descriptions, not base patterns

## Proposed Solution

### 1. Enhanced Similarity Detection Algorithm

```python
def _enhanced_filter_similar_variables(self, results, threshold=0.85, max_per_group=2):
    """
    Enhanced filtering that considers:
    1. Base pattern similarity (before first hyphen)
    2. Semantic score clustering
    3. Jaro-Winkler on normalized descriptions
    """
    
    # Step 1: Extract base patterns
    for result in results:
        description = result.get('description', '')
        # Extract base pattern (before first hyphen)
        base_pattern = description.split(' - ')[0].strip()
        result['base_pattern'] = base_pattern
        
    # Step 2: Group by base pattern AND similar scores
    groups = defaultdict(list)
    
    for result in results:
        base = result['base_pattern']
        score = round(result.get('score', 0), 1)  # Round to 0.1
        group_key = f"{base}_{score}"
        groups[group_key].append(result)
    
    # Step 3: Apply Jaro-Winkler within groups
    filtered_results = []
    
    for group_key, group_results in groups.items():
        if len(group_results) <= max_per_group:
            filtered_results.extend(group_results)
        else:
            # Sort by additional criteria
            sorted_group = sorted(group_results, key=lambda x: (
                -len(x.get('description', '')),  # Prefer longer descriptions
                x.get('code', '')  # Then by code
            ))
            
            # Take representatives
            representatives = []
            for candidate in sorted_group:
                is_similar = False
                for rep in representatives:
                    if self._jaro_winkler_similarity(
                        candidate['description'], 
                        rep['description']
                    ) > threshold:
                        is_similar = True
                        break
                
                if not is_similar:
                    representatives.append(candidate)
                    if len(representatives) >= max_per_group:
                        break
            
            filtered_results.extend(representatives)
    
    return filtered_results
```

### 2. Configuration Updates

```yaml
# Default configuration
SIMILARITY_CONFIG = {
    'base_pattern_grouping': True,
    'score_clustering_threshold': 0.1,  # Group scores within 0.1
    'description_similarity_threshold': 0.75,  # More aggressive
    'max_per_pattern_group': 2,  # Max 2 per base pattern
    'prefer_general_terms': True  # Prefer "All" over specific variations
}
```

### 3. Implementation Steps

#### Phase 1: Quick Fix (1-2 hours)
1. Update `_filter_similar_variables` to extract base patterns
2. Group by base pattern before applying Jaro-Winkler
3. Lower threshold to 0.75 for better filtering
4. Deploy to staging for testing

#### Phase 2: Enhanced Algorithm (2-3 hours)
1. Implement score-based clustering
2. Add preference logic for general vs specific terms
3. Add configuration for different variable types
4. Test with various query types

#### Phase 3: UI Enhancement (Optional, 3-4 hours)
1. Show filtered count indicator
2. Add "Show similar" expansion option
3. Display grouping rationale in tooltips

### 4. Specific Examples

**Current Result (7 variables):**
```
Contact with friends [Pst Mth] - Similar household income - All
Contact with friends [Pst Mth] - Similar household income - Most
Contact with friends [Pst Mth] - Similar household income - About half
Contact with friends [Pst Mth] - Similar household income - A few
Contact with friends [Pst Mth] - Similar household income - None
Contact with friends [Pst Mth] - Different household income - A higher household income
Contact with friends [Pst Mth] - Different household income - A lower household income
```

**After Fix (2-3 variables):**
```
Contact with friends [Pst Mth] - Similar household income - All
Contact with friends [Pst Mth] - Different household income - A higher household income
[Optional] + Show 5 similar variations
```

### 5. Testing Strategy

1. **Unit Tests:**
   - Test base pattern extraction
   - Test grouping logic
   - Test filtering within groups

2. **Integration Tests:**
   - Test with "contact with friends" query
   - Test with "household income" query
   - Test with mixed result sets

3. **Acceptance Criteria:**
   - Reduce "Contact with friends" from 7 to 2-3 results
   - Maintain distinct variable types
   - No loss of important variations

### 6. Risk Mitigation

1. **Over-filtering Risk:**
   - Keep configuration adjustable
   - Log filtered items for analysis
   - Provide UI option to show all

2. **Performance Risk:**
   - Cache base pattern extraction
   - Optimize grouping algorithm
   - Monitor response times

## Recommended Approach

I recommend starting with **Phase 1 Quick Fix** which will:
1. Extract base patterns before hyphens
2. Group variables by base pattern
3. Apply more aggressive filtering (0.75 threshold)
4. Keep max 2 per base pattern group

This should immediately reduce the "Contact with friends" variables from 7 to 2-3 while maintaining result quality.

## Next Steps

1. Review and approve this plan
2. Implement Phase 1 (Quick Fix)
3. Test on staging with the problematic queries
4. Iterate based on results
5. Consider Phase 2/3 enhancements if needed