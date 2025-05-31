# Business Intent Protection Guide

## Executive Summary

Protecting business intent in search queries is crucial for maintaining competitive advantage. This guide provides strategies to minimize information leakage through external API calls while maintaining search effectiveness.

---

## The Challenge

When users search for audiences like "high income millennials planning IPO in biotech", they reveal:
- Target demographics
- Business initiatives  
- Market strategies
- Timing information
- Industry focus

This information could be valuable to competitors or used for pattern analysis.

---

## Protection Strategies

### 1. Query Generalization

**Concept**: Strip business-specific details before sending to external APIs.

```python
def generalize_query(query: str) -> str:
    """Remove business-specific terms while preserving search intent"""
    
    # Remove company/brand names
    query = remove_company_terms(query)
    
    # Remove temporal markers
    query = re.sub(r'Q[1-4]|2024|2025|next quarter', '', query)
    
    # Remove campaign identifiers
    query = re.sub(r'campaign|launch|initiative', '', query)
    
    # Generalize business terms
    replacements = {
        'IPO': 'business event',
        'acquisition': 'business change',
        'merger': 'organizational change',
        'product launch': 'new offering'
    }
    
    for specific, general in replacements.items():
        query = query.replace(specific, general)
    
    return query.strip()

# Example:
# Input: "tech executives planning Q3 2024 IPO for biotech subsidiary"
# Output: "tech executives business event biotech"
```

### 2. Local-First Processing

**Concept**: Maximize use of pre-computed embeddings before calling external APIs.

```python
class LocalFirstSearch:
    def __init__(self):
        self.local_embeddings = load_49k_embeddings()
        self.cache = SearchCache()
    
    def search(self, query: str) -> List[Variable]:
        # 1. Check cache first
        if cached := self.cache.get(query):
            return cached
        
        # 2. Try local embeddings
        local_results = self.local_embeddings.search(query)
        
        # 3. Only call external API if needed
        if len(local_results) < MIN_RESULTS:
            external_results = self.external_search(
                self.generalize_query(query)
            )
            local_results.extend(external_results)
        
        return local_results
```

### 3. Query Fragmentation

**Concept**: Break complex queries into generic components.

```python
def fragment_query(query: str) -> List[str]:
    """Break query into generic, non-revealing fragments"""
    
    # Parse query into concepts
    concepts = extract_concepts(query)
    
    fragments = []
    for concept in concepts:
        # Create generic version
        if concept.type == 'demographic':
            fragments.append(f"{concept.age_range} {concept.gender}")
        elif concept.type == 'financial':
            fragments.append(f"income {concept.level}")
        elif concept.type == 'interest':
            fragments.append(concept.category)
    
    return fragments

# Example:
# Input: "wealthy tech executives interested in luxury EVs for Q4 campaign"
# Fragments: ["high income", "technology executive", "luxury vehicle", "electric"]
```

### 4. Noise Injection

**Concept**: Add decoy queries to obscure patterns.

```python
class PrivacyProtectedSearch:
    def __init__(self):
        self.decoy_generator = DecoyQueryGenerator()
    
    def search_with_privacy(self, real_query: str) -> Results:
        # Generate plausible decoy queries
        decoys = self.decoy_generator.generate(
            num_decoys=3,
            similar_to=real_query
        )
        
        # Mix real and decoy queries
        all_queries = [real_query] + decoys
        random.shuffle(all_queries)
        
        # Execute all queries
        results = {}
        for query in all_queries:
            results[query] = self.execute_search(query)
        
        # Return only real results
        return results[real_query]
```

### 5. Semantic Abstraction

**Concept**: Convert specific queries to semantic concepts.

```python
def abstract_query(query: str) -> str:
    """Convert specific terms to semantic abstractions"""
    
    abstractions = {
        # Demographics
        'millennials': 'age_group_2',
        'gen z': 'age_group_1',
        'boomers': 'age_group_4',
        
        # Financial
        'high income': 'income_tier_4',
        'affluent': 'wealth_level_high',
        
        # Behaviors
        'early adopter': 'innovation_index_high',
        'luxury buyer': 'purchase_tier_premium'
    }
    
    abstracted = query.lower()
    for term, abstract in abstractions.items():
        abstracted = abstracted.replace(term, abstract)
    
    return abstracted
```

### 6. Time-Delayed Batching

**Concept**: Batch and delay queries to obscure real-time intent.

```python
class BatchedPrivacySearch:
    def __init__(self):
        self.query_queue = []
        self.batch_size = 10
        self.delay_range = (5, 30)  # seconds
    
    def add_query(self, query: str) -> Future:
        """Queue query for batch processing"""
        future = Future()
        self.query_queue.append((query, future))
        
        if len(self.query_queue) >= self.batch_size:
            self.process_batch()
        
        return future
    
    def process_batch(self):
        """Process queries with random delays"""
        batch = self.query_queue[:self.batch_size]
        self.query_queue = self.query_queue[self.batch_size:]
        
        # Randomize order
        random.shuffle(batch)
        
        # Process with delays
        for query, future in batch:
            delay = random.uniform(*self.delay_range)
            threading.Timer(delay, self._execute, args=[query, future]).start()
```

---

## Implementation Architecture

### Privacy Proxy Pattern

```python
class PrivacyProxy:
    """Intermediary between application and external APIs"""
    
    def __init__(self):
        self.query_sanitizer = QuerySanitizer()
        self.audit_logger = AuditLogger()
        self.cache = PrivacyAwareCache()
    
    def search(self, query: str, user_context: dict) -> Results:
        # 1. Log original query (internal only)
        self.audit_logger.log_query(query, user_context)
        
        # 2. Check cache
        if cached := self.cache.get(query):
            return cached
        
        # 3. Sanitize query
        sanitized = self.query_sanitizer.sanitize(query)
        
        # 4. Execute search
        results = self._external_search(sanitized)
        
        # 5. Cache results
        self.cache.store(query, results)
        
        return results
```

---

## Configuration Options

### Environment Variables
```bash
# Privacy levels
PRIVACY_LEVEL=high  # low, medium, high
ENABLE_QUERY_GENERALIZATION=true
ENABLE_NOISE_INJECTION=true
ENABLE_BATCH_DELAY=true

# Cache settings
CACHE_EXTERNAL_QUERIES=true
CACHE_TTL_HOURS=24

# Local-first settings
PREFER_LOCAL_SEARCH=true
LOCAL_SEARCH_MIN_RESULTS=10
```

### Privacy Levels

| Level | Generalization | Noise | Batching | Caching |
|-------|---------------|-------|----------|---------|
| Low | Basic | No | No | Yes |
| Medium | Full | Optional | Yes | Yes |
| High | Aggressive | Yes | Required | Extended |

---

## Monitoring & Metrics

### Track Privacy Effectiveness
```python
class PrivacyMetrics:
    def __init__(self):
        self.metrics = {
            'queries_generalized': 0,
            'external_calls_avoided': 0,
            'cache_hit_rate': 0,
            'information_leakage_score': 0
        }
    
    def calculate_leakage_score(self, original: str, sent: str) -> float:
        """Calculate how much information was revealed"""
        # Compare entropy/information content
        return information_similarity(original, sent)
```

---

## Best Practices

### 1. **Gradual Rollout**
- Start with query generalization
- Add noise injection for sensitive queries
- Implement full privacy proxy when mature

### 2. **User Experience Balance**
- Monitor search quality metrics
- A/B test privacy features
- Allow power users to opt-in to higher privacy

### 3. **Regular Audits**
- Review external API logs monthly
- Analyze query patterns for leakage
- Update sanitization rules

### 4. **Documentation**
- Document all privacy measures
- Train team on importance
- Create guidelines for new features

---

## Example Implementation

```python
# Before (Reveals Everything)
response = openai.embeddings.create(
    model="text-embedding-ada-002",
    input="high net worth individuals planning to invest in green tech startups Q3 2024"
)

# After (Privacy Protected)
privacy_proxy = PrivacyProxy(level='high')
response = privacy_proxy.get_embedding(
    "high net worth individuals planning to invest in green tech startups Q3 2024"
)
# Actually sends: "high income investment technology"
```

---

## Conclusion

Protecting business intent requires a multi-layered approach:
1. **Technical measures**: Query sanitization, caching, local-first search
2. **Architectural patterns**: Privacy proxy, batch processing
3. **Operational practices**: Monitoring, auditing, continuous improvement

The key is balancing privacy protection with search effectiveness. Start with basic protections and increase based on your risk tolerance and business sensitivity.