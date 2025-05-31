"""
Domain-specific configurations for search optimization
Extracted from enhanced_semantic_search.py to centralize configuration
"""

# Domain-specific search configurations
DOMAIN_CONFIGS = {
    'automotive': {
        'name': 'Automotive',
        'prefix_patterns': ['VIO', 'AUTO', 'VEHICLE', 'CAR', 'TRUCK'],
        'weight_boost': 1.2,
        'priority_terms': ['car', 'vehicle', 'auto', 'drive', 'automotive'],
        'synonyms': {
            'vehicle': ['car', 'automobile', 'auto', 'ride'],
            'suv': ['sport utility vehicle', '4x4', 'crossover'],
            'truck': ['pickup', 'lorry', 'commercial vehicle'],
            'luxury': ['premium', 'high-end', 'expensive', 'luxury brand'],
            'economy': ['budget', 'affordable', 'cheap', 'value']
        },
        'boosts': {
            'exact_match': 2.0,
            'prefix_match': 1.5,
            'semantic': 1.3
        }
    },
    'demographic': {
        'name': 'Demographic',
        'prefix_patterns': ['DEMO', 'AGE', 'POP', 'MARITAL', 'HHLD'],
        'weight_boost': 1.1,
        'priority_terms': ['age', 'demographic', 'population', 'household'],
        'synonyms': {
            'age': ['years old', 'age group', 'generation'],
            'senior': ['elderly', 'retiree', '65+', 'older adult'],
            'youth': ['young', 'teen', 'adolescent', 'youngster'],
            'family': ['household', 'home', 'relatives', 'dependents'],
            'single': ['unmarried', 'bachelor', 'divorced', 'separated']
        }
    },
    'financial': {
        'name': 'Financial',
        'prefix_patterns': ['FIN', 'INC', 'WEALTH', 'SPEND', 'HH'],
        'weight_boost': 1.15,
        'priority_terms': ['income', 'financial', 'spending', 'wealth'],
        'synonyms': {
            'income': ['earnings', 'salary', 'revenue', 'wages'],
            'wealthy': ['affluent', 'high income', 'rich', 'prosperous', '100k+'],
            'poor': ['low income', 'vulnerable', 'struggling', 'poverty'],
            'middle class': ['average income', 'median', '50k-100k'],
            'spending': ['expenditure', 'consumption', 'purchases'],
            'savings': ['investments', 'assets', 'wealth']
        }
    },
    'health': {
        'name': 'Health',
        'prefix_patterns': ['HH', 'FR', 'HEALTH', 'MED', 'CARE'],
        'weight_boost': 1.1,
        'priority_terms': ['health', 'medical', 'disability', 'care'],
        'synonyms': {
            'disabled': ['disability', 'impaired', 'handicapped', 'special needs'],
            'healthy': ['wellness', 'fit', 'active', 'good health'],
            'elderly': ['frail', 'senior', 'aging', 'geriatric'],
            'medical': ['healthcare', 'doctor', 'hospital', 'treatment']
        }
    },
    'immigration': {
        'name': 'Immigration',
        'prefix_patterns': ['NC', 'IMM', 'CITIZEN', 'PR'],
        'weight_boost': 1.15,
        'priority_terms': ['immigrant', 'citizenship', 'permanent resident'],
        'synonyms': {
            'immigrant': ['newcomer', 'foreign-born', 'expat'],
            'permanent resident': ['pr', 'landed immigrant'],
            'temporary': ['visitor', 'student', 'work permit'],
            'citizenship': ['nationality', 'country of origin']
        }
    },
    'general': {
        'name': 'General',
        'prefix_patterns': [],
        'weight_boost': 1.0,
        'priority_terms': [],
        'synonyms': {},
        'boosts': {
            'exact_match': 1.5,
            'prefix_match': 1.2,
            'semantic': 1.0
        }
    }
}

def get_domain_config(domain: str) -> dict:
    """Get configuration for a specific domain"""
    return DOMAIN_CONFIGS.get(domain, DOMAIN_CONFIGS['general'])

def get_all_synonyms() -> dict:
    """Get all synonyms across domains"""
    all_synonyms = {}
    for domain_config in DOMAIN_CONFIGS.values():
        all_synonyms.update(domain_config.get('synonyms', {}))
    return all_synonyms

def get_domain_by_prefix(prefix: str) -> str:
    """Identify domain by variable prefix"""
    prefix_upper = prefix.upper()
    for domain, config in DOMAIN_CONFIGS.items():
        if prefix_upper in config.get('prefix_patterns', []):
            return domain
    return 'general'

def get_domain_by_product(product: str) -> str:
    """Map product name to domain"""
    domain_mapping = {
        'AutoView TVIO': 'automotive',
        'DemoStats': 'demographic',
        'Financial Vulnerability Index': 'financial',
        'CommunityHealth': 'health',
        'HouseholdSpend': 'financial',
        'NewToCanada': 'immigration'
    }
    return domain_mapping.get(product, 'general')