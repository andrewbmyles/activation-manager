"""
Shared utilities for search functionality
"""

from .domain_configs import (
    DOMAIN_CONFIGS,
    get_domain_config,
    get_all_synonyms,
    get_domain_by_prefix,
    get_domain_by_product
)
from .numeric_patterns import extract_numeric_patterns, parse_age_range, parse_income_range

__all__ = [
    'DOMAIN_CONFIGS',
    'get_domain_config',
    'get_all_synonyms',
    'get_domain_by_prefix',
    'get_domain_by_product',
    'extract_numeric_patterns',
    'parse_age_range',
    'parse_income_range'
]