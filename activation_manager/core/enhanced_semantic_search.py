"""
Enhanced Semantic Search for Variable Selection
Implements the comprehensive semantic search plan with 50-result capability
"""

import re
import json
import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Set
from pathlib import Path
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)


# Domain-specific configuration
DOMAIN_CONFIGS = {
    'automotive': {
        'prefix_patterns': ['VIO', 'EXPV', 'VAU', 'VBM', 'VCA'],
        'weight_boost': 1.0,
        'synonyms': {
            'car': ['automobile', 'vehicle', 'sedan', 'auto'],
            'suv': ['sport utility vehicle', 'crossover', 'cuv'],
            'truck': ['pickup', 'lorry'],
            'luxury': ['premium', 'high-end', 'upscale', 'exotic'],
            'import': ['foreign', 'imported', 'international'],
            'domestic': ['american', 'us', 'local', 'north american']
        }
    },
    'demographic': {
        'prefix_patterns': ['EHYBAS', 'AGE', 'EDU', 'CL', 'HHPOP'],
        'weight_boost': 1.1,
        'synonyms': {
            'young': ['youth', 'gen z', 'millennial', '18-24', '25-34'],
            'senior': ['elderly', 'retired', '65+', 'older', 'aging'],
            'family': ['household', 'children', 'parents'],
            'urban': ['city', 'metropolitan', 'downtown'],
            'rural': ['country', 'farm', 'remote']
        }
    },
    'financial': {
        'prefix_patterns': ['FV', 'HS', 'INCOME', 'SPEND', 'WEALTH'],
        'weight_boost': 1.2,
        'synonyms': {
            'wealthy': ['affluent', 'high income', 'rich', 'prosperous', '100k+'],
            'poor': ['low income', 'vulnerable', 'struggling', 'poverty'],
            'middle class': ['average income', 'median', '50k-100k'],
            'spending': ['expenditure', 'consumption', 'purchases'],
            'savings': ['investments', 'assets', 'wealth']
        }
    },
    'health': {
        'prefix_patterns': ['HH', 'FR', 'HEALTH', 'MED', 'CARE'],
        'weight_boost': 1.1,
        'synonyms': {
            'disabled': ['disability', 'impaired', 'handicapped', 'special needs'],
            'healthy': ['wellness', 'fit', 'active', 'good health'],
            'elderly': ['frail', 'senior', 'aging', 'geriatric'],
            'medical': ['healthcare', 'doctor', 'hospital', 'treatment']
        }
    },
    'immigration': {
        'prefix_patterns': ['NC', 'IMM', 'CITIZEN', 'PR'],
        'weight_boost': 1.15,
        'synonyms': {
            'immigrant': ['newcomer', 'foreign-born', 'expat'],
            'permanent resident': ['pr', 'landed immigrant'],
            'temporary': ['visitor', 'student', 'work permit'],
            'citizenship': ['nationality', 'country of origin']
        }
    }
}


@dataclass
class SearchConfig:
    """Configuration for enhanced search"""
    # Hybrid search weights
    hybrid_weight_semantic: float = 0.7
    hybrid_weight_keyword: float = 0.3
    
    # BM25 parameters
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    
    # Special handling
    negative_keyword_penalty: float = 0.5
    exact_match_boost: float = 2.0
    prefix_match_boost: float = 1.5
    
    # Performance
    max_results: int = 100
    default_top_k: int = 50  # Changed from 10 to 50
    
    # Caching
    cache_size: int = 1000
    cache_ttl: int = 3600  # 1 hour


class EnhancedVariable:
    """Enhanced variable class with all derived fields"""
    
    def __init__(self, row: Dict[str, Any]):
        # Core fields from CSV
        self.code = row.get('VarId', row.get('code', ''))
        self.description = row.get('Description', row.get('description', ''))
        self.category = row.get('Category', row.get('category', ''))
        self.theme = row.get('Theme', row.get('theme', ''))
        self.product = row.get('ProductName', row.get('product', ''))
        self.context = row.get('Context', row.get('context', ''))
        self.consumption_flag = row.get('Consumption Flag', row.get('consumption_flag', ''))
        self.sort_order = row.get('SortOrder', row.get('sort_order', 0))
        self.vintage = row.get('Product Vintage', row.get('vintage', ''))
        
        # Derived fields for better search
        self.var_prefix = self._extract_prefix()
        self.domain = self._identify_domain()
        self.numeric_values = self._extract_numeric_values()
        self.processed_code = self._process_code()
        self.enriched_keywords = self._generate_keywords()
        self.embedding_text = self._create_embedding_text()
    
    def _extract_prefix(self) -> str:
        """Extract variable prefix (e.g., 'VIO' from 'VIOPCAR_T')"""
        match = re.match(r'^([A-Z]+)', self.code)
        return match.group(1) if match else ''
    
    def _identify_domain(self) -> str:
        """Map product/theme to search domain"""
        domain_mapping = {
            'AutoView TVIO': 'automotive',
            'DemoStats': 'demographic',
            'Financial Vulnerability Index': 'financial',
            'CommunityHealth': 'health',
            'HouseholdSpend': 'financial',
            'NewToCanada': 'immigration'
        }
        return domain_mapping.get(self.product, 'general')
    
    def _extract_numeric_values(self) -> Dict[str, List]:
        """Extract numeric patterns from description"""
        patterns = {
            'age_range': r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)',
            'dollar_amount': r'\$?([\d,]+)k?\+?',
            'percentage': r'(\d+)%',
            'year': r'20\d{2}'
        }
        extracted = {}
        for pattern_type, pattern in patterns.items():
            matches = re.findall(pattern, self.description or '')
            if matches:
                extracted[pattern_type] = matches
        return extracted
    
    def _process_code(self) -> str:
        """Convert VarId to searchable text"""
        processed = self.code.lower()
        processed = re.sub(r'_', ' ', processed)
        processed = re.sub(r'(\d+)', r' \1 ', processed)
        
        # Expand known abbreviations
        abbreviations = {
            'vio': 'vehicles in operation',
            'pcar': 'passenger car',
            'hhd': 'household',
            'pop': 'population',
            'fv': 'financial vulnerability',
            'hs': 'household spending'
        }
        
        for abbr, expansion in abbreviations.items():
            processed = processed.replace(abbr, expansion)
        
        return ' '.join(processed.split())
    
    def _generate_keywords(self) -> List[str]:
        """Generate comprehensive keywords for variable"""
        keywords = set()
        
        # Add processed code
        keywords.update(self.processed_code.split())
        
        # Add description words
        if self.description:
            desc_words = re.sub(r'[^\w\s]', ' ', self.description.lower()).split()
            keywords.update(desc_words)
        
        # Add category words
        if self.category:
            cat_words = re.sub(r'[^\w\s]', ' ', self.category.lower()).split()
            keywords.update(cat_words)
        
        # Add domain-specific synonyms
        if self.domain in DOMAIN_CONFIGS:
            domain_syns = DOMAIN_CONFIGS[self.domain]['synonyms']
            for base, syns in domain_syns.items():
                if base in ' '.join(keywords):
                    keywords.update(syns[:3])  # Limit synonyms
        
        return list(keywords)
    
    def _create_embedding_text(self) -> str:
        """Create rich text representation for embedding generation"""
        components = []
        
        # Theme and product context
        components.append(f"theme:{self.theme.lower()}")
        components.append(f"product:{self.product.lower()}")
        
        # Processed variable code
        if self.processed_code:
            components.append(f"code:{self.processed_code}")
        
        # Main description
        if self.description:
            components.append(self.description.lower())
        
        # Category
        if self.category:
            cat_clean = re.sub(r'[^\w\s]', ' ', self.category)
            components.append(f"category:{cat_clean.lower()}")
        
        # Context
        if self.context:
            components.append(f"context:{self.context.lower()}")
        
        # All enriched keywords
        if self.enriched_keywords:
            components.append(' '.join(self.enriched_keywords))
        
        return ' '.join(components)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'code': self.code,
            'description': self.description,
            'category': self.category,
            'theme': self.theme,
            'product': self.product,
            'context': self.context,
            'consumption_flag': self.consumption_flag,
            'domain': self.domain,
            'var_prefix': self.var_prefix,
            'enriched_keywords': self.enriched_keywords,
            'embedding_text': self.embedding_text
        }


class QueryProcessor:
    """Handles query preprocessing and enhancement"""
    
    def __init__(self, domain_configs: Dict):
        self.domain_configs = domain_configs
        self.numeric_patterns = {
            'age_range': r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?|old)?',
            'income_range': r'\$?([\d,]+)k?\s*(?:to|-)\s*\$?([\d,]+)k?',
            'year_range': r'(20\d{2})\s*(?:to|-)\s*(20\d{2})',
            'percentage': r'(\d+)%?\s*(?:percent|pct)?',
            'single_value': r'(\d+)k?\+|over\s*(\d+)|under\s*(\d+)'
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Complete query preprocessing pipeline"""
        context = {'original_query': query}
        
        # Extract numeric components
        numeric_parsed = self._parse_numeric(query)
        context['numeric_components'] = numeric_parsed['numeric_components']
        context['text_query'] = numeric_parsed['remaining_text']
        
        # Detect intent
        context['intent'] = self._classify_intent(query)
        
        # Expand synonyms
        context['expanded_terms'] = self._expand_synonyms(
            context['text_query'],
            context['intent']['domains']
        )
        
        # Final processed query
        context['processed_query'] = ' '.join(context['expanded_terms'])
        
        return context
    
    def _parse_numeric(self, query: str) -> Dict[str, Any]:
        """Extract numeric patterns from query"""
        extracted = {
            'original_query': query,
            'numeric_components': {},
            'remaining_text': query
        }
        
        for pattern_type, pattern in self.numeric_patterns.items():
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                extracted['numeric_components'][pattern_type] = match.groups()
                extracted['remaining_text'] = extracted['remaining_text'].replace(
                    match.group(0), ' '
                )
        
        extracted['remaining_text'] = ' '.join(extracted['remaining_text'].split())
        return extracted
    
    def _classify_intent(self, query: str) -> Dict[str, Any]:
        """Classify query intent"""
        query_lower = query.lower()
        intent_keywords = {
            'demographic': ['age', 'gender', 'household', 'family', 'population'],
            'financial': ['income', 'spending', 'wealth', 'money', 'affluent'],
            'automotive': ['car', 'vehicle', 'auto', 'truck', 'suv'],
            'health': ['health', 'medical', 'disability', 'wellness'],
            'immigration': ['immigrant', 'newcomer', 'citizen', 'resident']
        }
        
        scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[intent] = score
        
        if scores:
            primary_intent = max(scores, key=scores.get)
            return {
                'primary_intent': primary_intent,
                'domains': [primary_intent],
                'confidence': scores[primary_intent] / len(query_lower.split())
            }
        
        return {
            'primary_intent': 'general',
            'domains': [],
            'confidence': 0.0
        }
    
    def _expand_synonyms(self, query: str, domains: List[str]) -> List[str]:
        """Expand query with relevant synonyms"""
        words = query.lower().split()
        expanded_terms = set(words)
        
        for domain in domains:
            if domain in self.domain_configs:
                domain_syns = self.domain_configs[domain]['synonyms']
                for base, synonyms in domain_syns.items():
                    if base in words:
                        expanded_terms.update(synonyms[:3])
        
        return list(expanded_terms)


class HybridScorer:
    """Calculate sophisticated hybrid scores"""
    
    def __init__(self, config: SearchConfig, domain_configs: Dict):
        self.config = config
        self.domain_configs = domain_configs
    
    def calculate_hybrid_score(self, keyword_score: float, semantic_score: float, 
                             variable: EnhancedVariable, query_context: Dict) -> float:
        """Calculate sophisticated hybrid score"""
        # Normalize scores to [0, 1]
        norm_keyword = min(keyword_score / 10.0, 1.0)  # BM25 scores typically 0-10
        norm_semantic = (semantic_score + 1) / 2  # Cosine similarity [-1, 1] to [0, 1]
        
        # Base hybrid score
        base_score = (
            self.config.hybrid_weight_keyword * norm_keyword +
            self.config.hybrid_weight_semantic * norm_semantic
        )
        
        # Apply boosts
        score = base_score
        
        # Domain boost
        if variable.domain in self.domain_configs:
            score *= self.domain_configs[variable.domain]['weight_boost']
        
        # Exact match boost
        if self._check_exact_match(query_context['original_query'], variable):
            score *= self.config.exact_match_boost
        
        # Prefix match boost
        if self._check_prefix_match(query_context['original_query'], variable):
            score *= self.config.prefix_match_boost
        
        # Numeric alignment bonus
        if query_context.get('numeric_components') and variable.numeric_values:
            numeric_bonus = self._calculate_numeric_alignment(
                query_context['numeric_components'],
                variable.numeric_values
            )
            score *= (1 + numeric_bonus)
        
        return score
    
    def _check_exact_match(self, query: str, variable: EnhancedVariable) -> bool:
        """Check for exact matches in code or description"""
        query_lower = query.lower()
        return (
            query_lower == variable.code.lower() or
            query_lower in variable.code.lower() or
            query_lower in variable.description.lower()
        )
    
    def _check_prefix_match(self, query: str, variable: EnhancedVariable) -> bool:
        """Check if query matches variable prefix"""
        query_upper = query.upper()
        return variable.var_prefix and query_upper.startswith(variable.var_prefix)
    
    def _calculate_numeric_alignment(self, query_numeric: Dict, var_numeric: Dict) -> float:
        """Calculate bonus for numeric pattern matches"""
        bonus = 0.0
        for pattern_type in query_numeric:
            if pattern_type in var_numeric:
                bonus += 0.3
        return min(bonus, 0.6)  # Cap at 60% bonus


class EnhancedSemanticSearch:
    """Main enhanced semantic search implementation"""
    
    def __init__(self, variables: List[Dict[str, Any]], 
                 embeddings: Optional[np.ndarray] = None,
                 openai_api_key: Optional[str] = None):
        """Initialize enhanced semantic search"""
        self.config = SearchConfig()
        self.variables = []
        self.variable_lookup = {}
        
        # Convert to EnhancedVariable objects
        for var_data in variables:
            enhanced_var = EnhancedVariable(var_data)
            self.variables.append(enhanced_var)
            self.variable_lookup[enhanced_var.code] = enhanced_var
        
        # Initialize components
        self.query_processor = QueryProcessor(DOMAIN_CONFIGS)
        self.hybrid_scorer = HybridScorer(self.config, DOMAIN_CONFIGS)
        
        # Setup search indices
        self._setup_tfidf()
        if embeddings is not None:
            self._setup_faiss(embeddings)
        
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
        
        logger.info(f"✅ Enhanced search initialized with {len(self.variables)} variables")
    
    def _setup_tfidf(self):
        """Setup TF-IDF for keyword search"""
        # Create documents from variables
        documents = []
        for var in self.variables:
            doc = ' '.join([
                var.processed_code,
                var.description or '',
                var.category or '',
                ' '.join(var.enriched_keywords)
            ])
            documents.append(doc.lower())
        
        # Initialize TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        logger.info("✅ TF-IDF index created")
    
    def _setup_faiss(self, embeddings: np.ndarray):
        """Setup FAISS index for semantic search"""
        logger.info(f"🔄 Setting up FAISS with {len(embeddings)} embeddings of shape {embeddings.shape}")
        try:
            self.embeddings = embeddings.astype('float32')
            logger.info("  Converting to float32...")
            faiss.normalize_L2(self.embeddings)
            logger.info("  Normalizing embeddings...")
            
            self.faiss_index = faiss.IndexFlatIP(self.embeddings.shape[1])
            logger.info(f"  Created FAISS index with dimension {self.embeddings.shape[1]}")
            self.faiss_index.add(self.embeddings)
            logger.info(f"✅ FAISS index created with {len(embeddings)} vectors")
        except Exception as e:
            logger.error(f"❌ FAISS setup failed: {e}")
            raise
    
    def search(self, query: str, top_k: int = 50, use_semantic: bool = True, 
               use_keyword: bool = True, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enhanced search with 50 results default
        
        Args:
            query: Natural language search query
            top_k: Number of results to return (default 50)
            use_semantic: Whether to use semantic search
            use_keyword: Whether to use keyword search
            filters: Optional filters (e.g., {'theme': 'Demographic'})
            
        Returns:
            Dictionary with results and metadata
        """
        # Process query
        query_context = self.query_processor.process_query(query)
        
        # Get candidates from both methods
        all_candidates = []
        
        # Keyword search
        if use_keyword:
            keyword_results = self._keyword_search(
                query_context['processed_query'], 
                top_k * 2  # Get more candidates
            )
            all_candidates.extend(keyword_results)
        
        # Semantic search
        if use_semantic and hasattr(self, 'faiss_index') and self.openai_client:
            semantic_results = self._semantic_search(
                query_context['processed_query'],
                top_k * 2
            )
            all_candidates.extend(semantic_results)
        
        # Apply filters if provided
        if filters:
            all_candidates = self._apply_filters(all_candidates, filters)
        
        # Merge and rank with hybrid scoring
        final_results = self._merge_and_rank(all_candidates, query_context, top_k)
        
        # Group results
        grouped_results = self._group_results(final_results)
        
        return {
            'results': final_results[:top_k],
            'total_found': len(final_results),
            'query_context': query_context,
            'grouped': grouped_results,
            'search_methods': {
                'keyword': use_keyword,
                'semantic': use_semantic and hasattr(self, 'faiss_index')
            }
        }
    
    def _keyword_search(self, query: str, top_k: int) -> List[Tuple[EnhancedVariable, float, str]]:
        """Perform keyword-based search using TF-IDF"""
        query_vec = self.tfidf_vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                var = self.variables[idx]
                results.append((var, float(similarities[idx]), 'keyword'))
        
        return results
    
    def _semantic_search(self, query: str, top_k: int) -> List[Tuple[EnhancedVariable, float, str]]:
        """Perform semantic search using embeddings"""
        try:
            # Get query embedding
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
            query_embedding = np.array(response.data[0].embedding).astype('float32')
            query_embedding = query_embedding.reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS
            distances, indices = self.faiss_index.search(query_embedding, top_k)
            
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.variables):
                    var = self.variables[idx]
                    results.append((var, float(dist), 'semantic'))
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []
    
    def _apply_filters(self, candidates: List[Tuple], filters: Dict) -> List[Tuple]:
        """Apply filters to candidates"""
        filtered = []
        for candidate in candidates:
            var = candidate[0]
            match = True
            
            for key, value in filters.items():
                if key == 'theme' and var.theme != value:
                    match = False
                elif key == 'product' and var.product != value:
                    match = False
                elif key == 'domain' and var.domain != value:
                    match = False
            
            if match:
                filtered.append(candidate)
        
        return filtered
    
    def _merge_and_rank(self, candidates: List[Tuple], query_context: Dict, 
                       top_k: int) -> List[Dict[str, Any]]:
        """Merge results and apply hybrid scoring"""
        # Group by variable code
        var_scores = defaultdict(lambda: {'keyword': 0.0, 'semantic': 0.0})
        
        for var, score, method in candidates:
            var_scores[var.code][method] = max(var_scores[var.code][method], score)
        
        # Calculate hybrid scores
        final_results = []
        for var_code, scores in var_scores.items():
            var = self.variable_lookup[var_code]
            
            hybrid_score = self.hybrid_scorer.calculate_hybrid_score(
                scores['keyword'],
                scores['semantic'],
                var,
                query_context
            )
            
            result = var.to_dict()
            result['score'] = hybrid_score
            result['match_types'] = []
            if scores['keyword'] > 0:
                result['match_types'].append('keyword')
            if scores['semantic'] > 0:
                result['match_types'].append('semantic')
            
            final_results.append(result)
        
        # Sort by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        return final_results
    
    def _group_results(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """Group results by various criteria"""
        grouped = {
            'by_theme': defaultdict(list),
            'by_product': defaultdict(list),
            'by_domain': defaultdict(list)
        }
        
        for result in results[:50]:  # Group top 50
            grouped['by_theme'][result['theme']].append(result)
            grouped['by_product'][result['product']].append(result)
            grouped['by_domain'][result['domain']].append(result)
        
        # Convert defaultdict to dict
        return {
            'by_theme': dict(grouped['by_theme']),
            'by_product': dict(grouped['by_product']),
            'by_domain': dict(grouped['by_domain'])
        }