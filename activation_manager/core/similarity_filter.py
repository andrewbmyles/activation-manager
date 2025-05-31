"""
Standalone similarity filtering for variables
"""
from typing import List, Dict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
    """
    Calculate Jaro-Winkler similarity between two strings
    
    Args:
        s1: First string
        s2: Second string
        p: Scaling factor (default 0.1, should not exceed 0.25)
        
    Returns:
        Similarity score between 0 and 1
    """
    # Convert to lowercase for comparison
    s1, s2 = s1.lower(), s2.lower()
    
    len_s1, len_s2 = len(s1), len(s2)
    
    # If either string is empty
    if len_s1 == 0 or len_s2 == 0:
        # Both empty strings are considered identical
        return 1.0 if len_s1 == 0 and len_s2 == 0 else 0.0
    
    # If strings are identical
    if s1 == s2:
        return 1.0
    
    # Calculate the match window
    match_window = max(len_s1, len_s2) // 2 - 1
    if match_window < 1:
        match_window = 1
    
    # Initialize the matched arrays
    s1_matches = [False] * len_s1
    s2_matches = [False] * len_s2
    
    matches = 0
    transpositions = 0
    
    # Find matches
    for i in range(len_s1):
        start = max(0, i - match_window)
        end = min(i + match_window + 1, len_s2)
        
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = s2_matches[j] = True
            matches += 1
            break
    
    if matches == 0:
        return 0.0
    
    # Find transpositions
    k = 0
    for i in range(len_s1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    
    # Calculate Jaro similarity
    jaro = (matches / len_s1 + matches / len_s2 + 
            (matches - transpositions / 2) / matches) / 3.0
    
    # Calculate common prefix length (up to 4 chars)
    common_prefix = 0
    for i in range(min(len_s1, len_s2, 4)):
        if s1[i] == s2[i]:
            common_prefix += 1
        else:
            break
    
    # Calculate Jaro-Winkler similarity
    jaro_winkler = jaro + common_prefix * p * (1 - jaro)
    
    return jaro_winkler


def filter_similar_variables(results: List[Dict], 
                           similarity_threshold: float = 0.85,
                           max_similar_per_group: int = 2) -> List[Dict]:
    """
    Filter out similar variables to reduce redundancy
    Enhanced to handle base pattern grouping for cases like "Contact with friends [Pst Mth] - ..."
    
    Args:
        results: List of search results
        similarity_threshold: Minimum similarity to consider variables as similar (0-1)
        max_similar_per_group: Maximum number of similar variables to keep per group
        
    Returns:
        Filtered list of results
    """
    logger.info(f"🔍 filter_similar_variables called with {len(results)} results, threshold={similarity_threshold}, max_per_group={max_similar_per_group}")
    
    if not results:
        return results
    
    # Step 1: Extract base patterns and group by them
    base_pattern_groups = defaultdict(list)
    
    for i, result in enumerate(results):
        desc = result.get('description', '').strip()
        
        # Always store index, even for empty descriptions
        result['_index'] = i
        
        if not desc:
            # Empty description - use a special key
            result['_base_pattern'] = '__empty__'
            base_pattern_groups['__empty__'].append(result)
            continue
        
        # Extract base pattern (text before first hyphen or bracket pattern)
        # Examples: 
        # "Contact with friends [Pst Mth] - Similar income - All" -> "Contact with friends [Pst Mth]"
        # "Household Income $0-$20K" -> "Household Income"
        
        # Look for pattern with brackets followed by hyphen
        if ' - ' in desc:
            parts = desc.split(' - ')
            base_pattern = parts[0].strip()
        else:
            # For other patterns, take first few words or up to certain length
            words = desc.split()
            if len(words) > 3:
                base_pattern = ' '.join(words[:3])
            else:
                base_pattern = desc
        
        result['_base_pattern'] = base_pattern
        
        # Group by base pattern AND similar scores
        score = round(result.get('score', 0), 1)  # Round to nearest 0.1
        group_key = f"{base_pattern}:::{score}"
        base_pattern_groups[group_key].append(result)
    
    # Step 2: Filter within each base pattern group
    filtered_results = []
    processed_indices = set()
    
    # Process groups with most items first (to handle the worst offenders)
    sorted_groups = sorted(base_pattern_groups.items(), 
                         key=lambda x: len(x[1]), reverse=True)
    
    for group_key, group_results in sorted_groups:
        if not group_results:
            continue
        
        # If group is small enough, keep all
        if len(group_results) <= max_similar_per_group:
            filtered_results.extend(group_results)
            for r in group_results:
                processed_indices.add(r['_index'])
            continue
        
        # For larger groups, apply similarity filtering with more aggressive threshold
        group_filtered = []
        group_processed = set()
        
        # Use more aggressive threshold for base pattern groups
        group_threshold = min(similarity_threshold, 0.75)
        
        # Sort by score and description length (prefer more complete descriptions)
        group_results.sort(key=lambda x: (
            -x.get('score', 0),  # Higher score first
            -len(x.get('description', '')),  # Longer descriptions (more specific)
            x.get('description', '')  # Then alphabetically
        ))
        
        for result in group_results:
            idx = result['_index']
            if idx in group_processed:
                continue
            
            # Check similarity with already selected items in this group
            is_too_similar = False
            desc1 = result.get('description', '')
            
            for selected in group_filtered:
                desc2 = selected.get('description', '')
                similarity = jaro_winkler_similarity(desc1, desc2)
                
                if similarity >= group_threshold:
                    is_too_similar = True
                    break
            
            if not is_too_similar:
                group_filtered.append(result)
                group_processed.add(idx)
                
                # Stop if we have enough representatives
                if len(group_filtered) >= max_similar_per_group:
                    break
        
        # Add filtered group results
        filtered_results.extend(group_filtered)
        for r in group_results:
            processed_indices.add(r['_index'])
        
        # Log if we filtered a lot
        if len(group_results) > len(group_filtered):
            base_pattern = group_key.split(':::')[0]
            logger.debug(f"Filtered base pattern '{base_pattern[:50]}...': {len(group_results)} -> {len(group_filtered)}")
    
    # Step 3: Add any results not in base pattern groups (edge cases)
    unprocessed_count = 0
    for i, result in enumerate(results):
        if i not in processed_indices:
            filtered_results.append(result)
            unprocessed_count += 1
    
    if unprocessed_count > 0:
        logger.warning(f"⚠️ Added {unprocessed_count} unprocessed results back to filtered results")
    
    # Clean up temporary fields
    for result in filtered_results:
        result.pop('_index', None)
        result.pop('_base_pattern', None)
    
    # Sort by original score
    filtered_results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    logger.info(f"Similarity filtering: {len(results)} -> {len(filtered_results)} results")
    
    # Final verification
    contact_count = sum(1 for r in filtered_results if 'Contact with friends' in r.get('description', ''))
    if contact_count > 0:
        logger.info(f"🎯 Contact with friends in filtered results: {contact_count}")
    
    return filtered_results