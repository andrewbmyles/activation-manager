"""
Activation Manager - Advanced Audience Segmentation System
"""

__version__ = "1.0.0"
__author__ = "Myles"

from .core.audience_builder import AudienceBuilder, DataRetriever, ConstrainedKMedians
from .core.prizm_analyzer import PRIZMAnalyzer
from .core.csv_variable_loader import CSVVariableLoader

# Import variable selectors if available
try:
    from .core.variable_selector import VariableSelector
except ImportError:
    VariableSelector = None

__all__ = [
    'AudienceBuilder',
    'DataRetriever', 
    'ConstrainedKMedians',
    'PRIZMAnalyzer',
    'CSVVariableLoader',
    'VariableSelector'
]