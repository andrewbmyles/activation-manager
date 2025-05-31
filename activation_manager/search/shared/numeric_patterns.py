"""
Numeric pattern extraction utilities
Extracted from enhanced_semantic_search.py for reuse
"""
import re
from typing import List, Tuple, Optional, Dict


def extract_numeric_patterns(text: str) -> Dict[str, List[Tuple[float, float]]]:
    """
    Extract numeric patterns from text
    
    Returns dict with keys: 'age_ranges', 'income_ranges', 'percentages', 'years'
    """
    patterns = {
        'age_ranges': [],
        'income_ranges': [],
        'percentages': [],
        'years': []
    }
    
    # Age ranges (e.g., "25-34", "age 25 to 34", "25 to 34 years")
    age_patterns = [
        r'(?:age[s]?\s+)?(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years?|yrs?)?',
        r'(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years?\s+old|yo)',
        r'(?:aged?\s+)?(\d+)\s*(?:-|to)\s*(\d+)'
    ]
    
    for pattern in age_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                low = float(match.group(1))
                high = float(match.group(2))
                if 0 <= low <= 120 and 0 <= high <= 120 and low < high:
                    patterns['age_ranges'].append((low, high))
            except:
                pass
    
    # Income ranges (e.g., "$50k-$100k", "50000 to 100000", "income over 100k")
    income_patterns = [
        r'\$?\s*(\d+)k?\s*(?:-|to)\s*\$?\s*(\d+)k?',
        r'income\s+(?:over|above|below|under)\s+\$?\s*(\d+)k?',
        r'\$(\d{1,3}),?(\d{3})\s*(?:-|to)\s*\$(\d{1,3}),?(\d{3})'
    ]
    
    for match in re.finditer(income_patterns[0], text, re.IGNORECASE):
        try:
            low = float(match.group(1))
            high = float(match.group(2))
            # Convert 'k' notation to thousands
            if 'k' in match.group(0).lower():
                low *= 1000
                high *= 1000
            patterns['income_ranges'].append((low, high))
        except:
            pass
    
    # Handle "income over/under X" patterns
    for match in re.finditer(income_patterns[1], text, re.IGNORECASE):
        try:
            value = float(match.group(1))
            if 'k' in match.group(0).lower():
                value *= 1000
            
            if 'over' in match.group(0) or 'above' in match.group(0):
                patterns['income_ranges'].append((value, float('inf')))
            else:  # below/under
                patterns['income_ranges'].append((0, value))
        except:
            pass
    
    # Percentages (e.g., "25%", "25 percent")
    percent_pattern = r'(\d+(?:\.\d+)?)\s*(?:%|percent)'
    for match in re.finditer(percent_pattern, text, re.IGNORECASE):
        try:
            value = float(match.group(1))
            if 0 <= value <= 100:
                patterns['percentages'].append((value, value))
        except:
            pass
    
    # Years (e.g., "2020", "2020-2025")
    year_pattern = r'(?:19|20)\d{2}'
    for match in re.finditer(year_pattern, text):
        try:
            year = int(match.group(0))
            if 1900 <= year <= 2100:
                patterns['years'].append((year, year))
        except:
            pass
    
    return patterns


def parse_age_range(text: str) -> Optional[Tuple[int, int]]:
    """Parse age range from text like '25-34 years' or 'age 25 to 34'"""
    patterns = extract_numeric_patterns(text)
    if patterns['age_ranges']:
        return tuple(map(int, patterns['age_ranges'][0]))
    return None


def parse_income_range(text: str) -> Optional[Tuple[float, float]]:
    """Parse income range from text like '$50k-$100k' or 'income over 100k'"""
    patterns = extract_numeric_patterns(text)
    if patterns['income_ranges']:
        return patterns['income_ranges'][0]
    return None


def normalize_numeric_value(value: float, value_type: str = 'general') -> float:
    """Normalize numeric values for comparison"""
    if value_type == 'age':
        # Normalize age to 0-1 scale (0-100 years)
        return min(value / 100.0, 1.0)
    elif value_type == 'income':
        # Normalize income to 0-1 scale (0-500k)
        return min(value / 500000.0, 1.0)
    elif value_type == 'percentage':
        # Already 0-100, normalize to 0-1
        return value / 100.0
    else:
        return value


def calculate_numeric_similarity(query_ranges: List[Tuple[float, float]], 
                                var_ranges: List[Tuple[float, float]],
                                value_type: str = 'general') -> float:
    """
    Calculate similarity between numeric ranges
    Returns score between 0 and 1
    """
    if not query_ranges or not var_ranges:
        return 0.0
    
    max_similarity = 0.0
    
    for q_low, q_high in query_ranges:
        for v_low, v_high in var_ranges:
            # Calculate overlap
            overlap_start = max(q_low, v_low)
            overlap_end = min(q_high, v_high)
            
            if overlap_start <= overlap_end:
                # There is overlap
                overlap = overlap_end - overlap_start
                union = max(q_high, v_high) - min(q_low, v_low)
                similarity = overlap / union if union > 0 else 0
                
                # Boost for exact matches
                if q_low == v_low and q_high == v_high:
                    similarity = 1.0
                
                max_similarity = max(max_similarity, similarity)
    
    return max_similarity