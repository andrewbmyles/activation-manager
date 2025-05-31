# Privacy Proxy Implementation Guide

## Quick Start Implementation

This guide provides a practical implementation of a Privacy Proxy for the Activation Manager to protect business intent in search queries.

---

## Core Implementation

### 1. Privacy Proxy Class

```python
# activation_manager/core/privacy_proxy.py

import re
import hashlib
import random
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PrivacyProxy:
    """
    Protects business intent by sanitizing queries before sending to external APIs
    """
    
    def __init__(self, privacy_level: str = 'medium'):
        self.privacy_level = privacy_level
        self.cache = {}
        self.audit_log = []
        
        # Business-specific terms to remove/generalize
        self.sensitive_terms = {
            # Temporal markers
            r'\bQ[1-4]\s*202[4-9]\b': 'future period',
            r'\bnext\s+(quarter|month|year)\b': 'future period',
            r'\b202[4-9]\b': 'future',
            
            # Business events
            r'\bIPO\b': 'business event',
            r'\bacquisition\b': 'business change',
            r'\bmerger\b': 'business change',
            r'\blaunch\b': 'new initiative',
            r'\bcampaign\b': 'initiative',
            
            # Company/competitor names (customize these)
            r'\b(CompanyA|CompanyB|OurBrand)\b': '[brand]',
            
            # Specific products/services
            r'\b(ProductX|ServiceY)\b': '[product]',
        }
        
        # Generic replacements for common terms
        self.generalizations = {
            'wealthy': 'high income',
            'rich': 'high income',
            'affluent': 'high income',
            'millionaire': 'high net worth',
            'premium': 'high value',
            'luxury': 'high end',
            'exclusive': 'selective',
        }
    
    def sanitize_query(self, query: str) -> str:
        """
        Remove or generalize sensitive business information from query
        """
        sanitized = query.lower()
        
        # Apply regex replacements for sensitive patterns
        for pattern, replacement in self.sensitive_terms.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        # Apply simple generalizations
        if self.privacy_level in ['medium', 'high']:
            for specific, general in self.generalizations.items():
                sanitized = sanitized.replace(specific, general)
        
        # Remove multiple spaces and trim
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def fragment_query(self, query: str) -> List[str]:
        """
        Break query into generic fragments for high privacy mode
        """
        # Simple word-based fragmentation
        words = query.lower().split()
        
        # Group related concepts
        fragments = []
        current_fragment = []
        
        for word in words:
            current_fragment.append(word)
            if len(current_fragment) >= 3:  # Max 3 words per fragment
                fragments.append(' '.join(current_fragment))
                current_fragment = []
        
        if current_fragment:
            fragments.append(' '.join(current_fragment))
        
        return fragments
    
    def add_noise_queries(self, query: str, num_decoys: int = 2) -> List[str]:
        """
        Generate plausible decoy queries to obscure the real intent
        """
        decoy_templates = [
            "young adults interested in {topic}",
            "seniors looking for {topic}",
            "families with {topic} needs",
            "professionals seeking {topic}",
            "students interested in {topic}",
        ]
        
        # Extract a topic from the query
        words = query.split()
        topic_words = [w for w in words if len(w) > 4]  # Simple heuristic
        topic = random.choice(topic_words) if topic_words else "services"
        
        decoys = []
        for _ in range(num_decoys):
            template = random.choice(decoy_templates)
            decoy = template.format(topic=topic)
            decoys.append(decoy)
        
        return decoys
    
    def process_query(self, query: str, user_id: str = None) -> Tuple[str, Dict]:
        """
        Process query according to privacy level
        """
        # Log original query (internal only)
        self._audit_log(query, user_id)
        
        # Check cache first
        cache_key = self._get_cache_key(query)
        if cache_key in self.cache:
            logger.info("Privacy proxy cache hit")
            return self.cache[cache_key]
        
        metadata = {
            'original_query': query,
            'privacy_level': self.privacy_level,
            'timestamp': datetime.now().isoformat(),
            'techniques_applied': []
        }
        
        # Apply privacy techniques based on level
        if self.privacy_level == 'low':
            processed = self.sanitize_query(query)
            metadata['techniques_applied'].append('basic_sanitization')
            
        elif self.privacy_level == 'medium':
            processed = self.sanitize_query(query)
            metadata['techniques_applied'].extend(['sanitization', 'generalization'])
            
        elif self.privacy_level == 'high':
            # Full privacy protection
            processed = self.sanitize_query(query)
            metadata['techniques_applied'].extend(['sanitization', 'generalization'])
            
            # Add noise if query is particularly sensitive
            if self._is_sensitive_query(query):
                decoys = self.add_noise_queries(processed)
                metadata['decoy_queries'] = decoys
                metadata['techniques_applied'].append('noise_injection')
        
        else:
            processed = query  # No processing
        
        # Calculate information retention score
        metadata['info_retention_score'] = self._calculate_retention_score(query, processed)
        
        # Cache the result
        self.cache[cache_key] = (processed, metadata)
        
        return processed, metadata
    
    def _is_sensitive_query(self, query: str) -> bool:
        """
        Determine if query contains particularly sensitive information
        """
        sensitive_indicators = [
            'competitor', 'acquisition', 'merger', 'ipo', 'launch',
            'confidential', 'strategic', 'q1', 'q2', 'q3', 'q4'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in sensitive_indicators)
    
    def _calculate_retention_score(self, original: str, processed: str) -> float:
        """
        Calculate how much information is retained after processing
        """
        if not original or not processed:
            return 0.0
        
        # Simple character-based retention score
        original_words = set(original.lower().split())
        processed_words = set(processed.lower().split())
        
        if not original_words:
            return 0.0
        
        retained = len(processed_words.intersection(original_words))
        total = len(original_words)
        
        return retained / total
    
    def _get_cache_key(self, query: str) -> str:
        """
        Generate cache key for query
        """
        return hashlib.md5(query.encode()).hexdigest()
    
    def _audit_log(self, query: str, user_id: str = None):
        """
        Log queries for internal audit (never sent externally)
        """
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id or 'anonymous',
            'query_hash': self._get_cache_key(query),
            'query_length': len(query),
            'word_count': len(query.split())
        })
    
    def get_audit_summary(self) -> Dict:
        """
        Get summary of privacy proxy usage
        """
        if not self.audit_log:
            return {'total_queries': 0}
        
        return {
            'total_queries': len(self.audit_log),
            'unique_users': len(set(log['user_id'] for log in self.audit_log)),
            'cache_size': len(self.cache),
            'avg_query_length': sum(log['query_length'] for log in self.audit_log) / len(self.audit_log),
            'time_range': {
                'start': self.audit_log[0]['timestamp'],
                'end': self.audit_log[-1]['timestamp']
            }
        }
```

### 2. Integration with Enhanced Variable Picker

```python
# activation_manager/api/enhanced_variable_picker_api.py

def search_variables_with_privacy(
    self,
    query: str,
    top_k: int = 50,
    privacy_level: str = 'medium',
    user_id: str = None
) -> Dict[str, Any]:
    """
    Search variables with privacy protection
    """
    # Initialize privacy proxy
    privacy_proxy = PrivacyProxy(privacy_level=privacy_level)
    
    # Process query through privacy proxy
    sanitized_query, metadata = privacy_proxy.process_query(query, user_id)
    
    logger.info(f"Privacy proxy: '{query}' -> '{sanitized_query}'")
    
    # Perform search with sanitized query
    results = self.search_variables(
        query=sanitized_query,
        top_k=top_k,
        use_semantic=True,
        use_keyword=True
    )
    
    # Add privacy metadata to results
    results['privacy_metadata'] = metadata
    
    # If noise injection was used, execute decoy queries
    if 'decoy_queries' in metadata:
        for decoy in metadata['decoy_queries']:
            # Execute but discard results
            _ = self.search_variables(query=decoy, top_k=5)
    
    return results
```

### 3. Configuration

```python
# activation_manager/config/privacy_config.py

import os

class PrivacyConfig:
    """Privacy configuration for the application"""
    
    # Privacy level: 'none', 'low', 'medium', 'high'
    PRIVACY_LEVEL = os.environ.get('PRIVACY_LEVEL', 'medium')
    
    # Cache settings
    CACHE_PRIVACY_RESULTS = os.environ.get('CACHE_PRIVACY_RESULTS', 'true').lower() == 'true'
    CACHE_TTL_HOURS = int(os.environ.get('PRIVACY_CACHE_TTL_HOURS', '24'))
    
    # Audit settings
    ENABLE_PRIVACY_AUDIT = os.environ.get('ENABLE_PRIVACY_AUDIT', 'true').lower() == 'true'
    AUDIT_RETENTION_DAYS = int(os.environ.get('AUDIT_RETENTION_DAYS', '30'))
    
    # Feature flags
    ENABLE_QUERY_SANITIZATION = os.environ.get('ENABLE_QUERY_SANITIZATION', 'true').lower() == 'true'
    ENABLE_NOISE_INJECTION = os.environ.get('ENABLE_NOISE_INJECTION', 'false').lower() == 'true'
    ENABLE_QUERY_FRAGMENTATION = os.environ.get('ENABLE_QUERY_FRAGMENTATION', 'false').lower() == 'true'
    
    # Local-first search
    PREFER_LOCAL_SEARCH = os.environ.get('PREFER_LOCAL_SEARCH', 'true').lower() == 'true'
    MIN_LOCAL_RESULTS = int(os.environ.get('MIN_LOCAL_RESULTS', '10'))
```

### 4. API Integration Example

```python
# In main.py, update the enhanced search endpoint

@app.route('/api/enhanced-variable-picker/search', methods=['POST'])
def enhanced_variable_search():
    """Enhanced semantic variable search with privacy protection"""
    try:
        data = request.json or {}
        query = data.get('query', '')
        top_k = data.get('top_k', 50)
        
        # Privacy settings
        privacy_level = data.get('privacy_level', PrivacyConfig.PRIVACY_LEVEL)
        user_id = request.headers.get('X-User-ID')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Use enhanced picker with privacy
        picker = get_enhanced_picker()
        if picker and hasattr(picker, 'search_variables_with_privacy'):
            results = picker.search_variables_with_privacy(
                query=query,
                top_k=top_k,
                privacy_level=privacy_level,
                user_id=user_id
            )
        else:
            # Fallback with basic privacy
            privacy_proxy = PrivacyProxy(privacy_level=privacy_level)
            sanitized_query, metadata = privacy_proxy.process_query(query, user_id)
            
            results = search_variables(sanitized_query, top_k)
            results = {
                'results': results,
                'total_found': len(results),
                'privacy_metadata': metadata
            }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Enhanced variable search error: {e}")
        return jsonify({'error': str(e)}), 500
```

---

## Testing the Privacy Proxy

```python
# test_privacy_proxy.py

def test_privacy_levels():
    """Test different privacy levels"""
    
    test_queries = [
        "high income millennials for Q3 2024 product launch",
        "wealthy tech executives interested in our new IPO",
        "CompanyA customers switching to CompanyB",
        "luxury car owners in California for acquisition campaign"
    ]
    
    for level in ['none', 'low', 'medium', 'high']:
        print(f"\n=== Privacy Level: {level} ===")
        proxy = PrivacyProxy(privacy_level=level)
        
        for query in test_queries:
            sanitized, metadata = proxy.process_query(query)
            print(f"Original: {query}")
            print(f"Sanitized: {sanitized}")
            print(f"Retention: {metadata['info_retention_score']:.2%}")
            print(f"Techniques: {', '.join(metadata['techniques_applied'])}")
            print()

if __name__ == "__main__":
    test_privacy_levels()
```

---

## Deployment Checklist

1. **Environment Variables**
   ```bash
   export PRIVACY_LEVEL=medium
   export ENABLE_QUERY_SANITIZATION=true
   export PREFER_LOCAL_SEARCH=true
   export MIN_LOCAL_RESULTS=10
   ```

2. **Monitor Impact**
   - Track search quality metrics
   - Monitor API costs
   - Review sanitization effectiveness

3. **Customize Sensitive Terms**
   - Add company-specific terms
   - Include industry jargon
   - Update competitor names

4. **Test Thoroughly**
   - Verify search quality maintained
   - Check privacy effectiveness
   - Monitor performance impact

---

## Next Steps

1. Start with 'low' privacy level
2. Monitor search quality
3. Gradually increase privacy based on needs
4. Customize sensitive terms for your business
5. Add industry-specific generalizations