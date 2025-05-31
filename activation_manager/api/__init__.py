"""
API modules for Activation Manager
"""

# Import API modules
try:
    from .enhanced_variable_picker_api import EnhancedVariablePickerAPI
except ImportError:
    EnhancedVariablePickerAPI = None

try:
    from .variable_picker_api import VariablePickerAPI
except ImportError:
    VariablePickerAPI = None

__all__ = [
    'EnhancedVariablePickerAPI',
    'VariablePickerAPI'
]