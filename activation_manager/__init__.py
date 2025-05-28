"""
Activation Manager - Advanced Audience Segmentation System
"""

__version__ = "1.0.0"
__author__ = "Myles"

from .core.audience_builder import AudienceBuilder, DataRetriever, ConstrainedKMedians
from .core.enhanced_variable_selector_v2 import EnhancedVariableSelectorV2
from .core.enhanced_variable_selector_v3 import EnhancedVariableSelectorV3
from .core.enhanced_variable_selector_v4 import EnhancedVariableSelectorV4
from .core.prizm_analyzer import PRIZMAnalyzer

__all__ = [
    'AudienceBuilder',
    'DataRetriever', 
    'ConstrainedKMedians',
    'EnhancedVariableSelectorV2',
    'EnhancedVariableSelectorV3',
    'EnhancedVariableSelectorV4',
    'PRIZMAnalyzer'
]