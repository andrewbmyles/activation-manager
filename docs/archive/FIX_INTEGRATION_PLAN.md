# Real Fix for Enhanced Picker Integration

## Root Cause Identified

The hang occurs in `EnhancedSemanticSearch.__init__()` at line 453-454 when initializing the OpenAI client:

```python
from openai import OpenAI
self.openai_client = OpenAI(api_key=openai_api_key)
```

### Issues:
1. The import happens inside __init__ (bad practice)
2. OpenAI client initialization may be blocking/hanging
3. No proper error handling or timeout
4. The openai_api_key is likely None in our case

## Proper Fix Implementation

### 1. Fix the OpenAI Client Initialization

```python
# In enhanced_semantic_search.py, line 451-456
# OpenAI client for query embeddings
self.openai_client = None
if openai_api_key:
    try:
        from openai import OpenAI
        self.openai_client = OpenAI(api_key=openai_api_key)
        logger.info("✅ OpenAI client initialized")
    except Exception as e:
        logger.warning(f"OpenAI client initialization failed: {e}")
        self.openai_client = None
else:
    logger.info("📌 OpenAI client disabled (no API key)")
```

### 2. Move Imports to Top of File

```python
# At top of enhanced_semantic_search.py
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None
```

### 3. Add Initialization Timeout

```python
# In enhanced_variable_picker_api.py
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError("Initialization timed out")
    
    # Set the signal handler and alarm
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)  # Disable the alarm

# Use in _ensure_initialized
with timeout(10):  # 10 second timeout
    self.enhanced_search = EnhancedSemanticSearchV2(
        variables=variables_list,
        embeddings=embeddings,
        openai_api_key=self.openai_api_key
    )
```

### 4. Pre-initialize at Startup (Optional)

```python
# In main.py, after variable loader initialization
if not Config.IS_PRODUCTION:
    logger.info("Pre-initializing Enhanced Variable Picker...")
    try:
        from activation_manager.api.enhanced_variable_picker_api import EnhancedVariablePickerAPI
        enhanced_picker = EnhancedVariablePickerAPI.get_instance()
        # Don't force initialization here, let it happen lazily
        logger.info("✅ Enhanced Variable Picker instance created")
    except Exception as e:
        logger.warning(f"Enhanced Variable Picker pre-init failed: {e}")
        enhanced_picker = None
```

## Implementation Steps

1. **First**: Fix the OpenAI client initialization issue
2. **Second**: Add proper error handling and timeouts
3. **Third**: Test thoroughly
4. **Fourth**: Deploy with confidence

## Testing Plan

1. Test without OpenAI API key (most common case)
2. Test with invalid OpenAI API key
3. Test with valid OpenAI API key
4. Test concurrent requests
5. Test with Flask debug mode off

This is the real fix that preserves full functionality while solving the integration issue.