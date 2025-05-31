"""
Variable Catalog for Audience Builder
Maps variable codes to their metadata based on Environics/PRIZM data
"""

# Sample variable catalog based on the synthetic data
# In production, this would be loaded from metadata files
VARIABLE_CATALOG = {
    # Geographic/Demographic Variables
    "PRIZM_SEGMENT": {
        "type": "demographic",
        "description": "PRIZM consumer segmentation cluster",
        "data_type": "categorical",
        "values": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
    },
    
    # Sample Q-code variables (based on typical Environics/PRIZM patterns)
    "Q470010C01": {
        "type": "demographic",
        "description": "Age range - 18-24 years",
        "data_type": "numeric"
    },
    "Q470010C02": {
        "type": "demographic",
        "description": "Age range - 25-34 years",
        "data_type": "numeric"
    },
    "Q470010C03": {
        "type": "demographic",
        "description": "Age range - 35-44 years",
        "data_type": "numeric"
    },
    "Q470010C04": {
        "type": "demographic",
        "description": "Age range - 45-54 years",
        "data_type": "numeric"
    },
    "Q470010C05": {
        "type": "demographic",
        "description": "Age range - 55+ years",
        "data_type": "numeric"
    },
    
    # Income-related variables
    "Q470030C01": {
        "type": "financial",
        "description": "Household income - Under $30,000",
        "data_type": "numeric"
    },
    "Q470030C02": {
        "type": "financial",
        "description": "Household income - $30,000-$49,999",
        "data_type": "numeric"
    },
    "Q470030C03": {
        "type": "financial",
        "description": "Household income - $50,000-$74,999",
        "data_type": "numeric"
    },
    "Q470030C04": {
        "type": "financial",
        "description": "Household income - $75,000-$99,999",
        "data_type": "numeric"
    },
    "Q470030C05": {
        "type": "financial",
        "description": "Household income - $100,000-$149,999",
        "data_type": "numeric"
    },
    "Q470030C06": {
        "type": "financial",
        "description": "Household income - $150,000+",
        "data_type": "numeric"
    },
    
    # Behavioral variables
    "Q471010C01": {
        "type": "behavioral",
        "description": "Online shopping frequency - Daily",
        "data_type": "numeric"
    },
    "Q471010C02": {
        "type": "behavioral",
        "description": "Online shopping frequency - Weekly",
        "data_type": "numeric"
    },
    "Q471010C04": {
        "type": "behavioral",
        "description": "Online shopping frequency - Monthly",
        "data_type": "numeric"
    },
    
    # Psychographic variables
    "Q4810401K1": {
        "type": "psychographic",
        "description": "Environmental consciousness - Very important",
        "data_type": "numeric"
    },
    "Q4810402K1": {
        "type": "psychographic",
        "description": "Health consciousness - Very important",
        "data_type": "numeric"
    },
    "Q4810403K1": {
        "type": "psychographic",
        "description": "Technology adoption - Early adopter",
        "data_type": "numeric"
    },
    
    # Location type
    "Q470020C01": {
        "type": "demographic",
        "description": "Urban residence",
        "data_type": "numeric"
    },
    "Q470020C03": {
        "type": "demographic",
        "description": "Suburban residence",
        "data_type": "numeric"
    },
    "Q470020C04": {
        "type": "demographic",
        "description": "Rural residence",
        "data_type": "numeric"
    },
    
    # Additional behavioral variables
    "Q5200101C1": {
        "type": "behavioral",
        "description": "Green product purchases - Frequent",
        "data_type": "numeric"
    },
    "Q5200102C1": {
        "type": "behavioral",
        "description": "Organic food purchases - Frequent",
        "data_type": "numeric"
    },
    
    # Financial behavior
    "Q530070C01": {
        "type": "financial",
        "description": "Disposable income level - High",
        "data_type": "numeric"
    },
    "Q530070C02": {
        "type": "financial",
        "description": "Disposable income level - Medium",
        "data_type": "numeric"
    },
    
    # Media consumption
    "Q2100101C1": {
        "type": "behavioral",
        "description": "Social media usage - Heavy user",
        "data_type": "numeric"
    },
    "Q2100102C1": {
        "type": "behavioral",
        "description": "Digital media consumption - High",
        "data_type": "numeric"
    },
    
    # Purchase intent
    "Q2300101C1": {
        "type": "behavioral",
        "description": "Sustainable product interest - High",
        "data_type": "numeric"
    },
    "Q2300102C1": {
        "type": "behavioral",
        "description": "Premium brand preference",
        "data_type": "numeric"
    }
}


def get_full_catalog():
    """
    Get the complete variable catalog
    This would normally load from metadata files
    """
    return VARIABLE_CATALOG


def get_variables_by_type(var_type: str):
    """
    Get all variables of a specific type
    
    Args:
        var_type: One of 'demographic', 'behavioral', 'financial', 'psychographic'
    
    Returns:
        Dict of variables matching the type
    """
    return {
        code: info 
        for code, info in VARIABLE_CATALOG.items() 
        if info.get('type') == var_type
    }


def search_variables(search_term: str):
    """
    Search for variables by description
    
    Args:
        search_term: Term to search for in variable descriptions
    
    Returns:
        Dict of matching variables
    """
    search_lower = search_term.lower()
    return {
        code: info 
        for code, info in VARIABLE_CATALOG.items() 
        if search_lower in info.get('description', '').lower()
    }