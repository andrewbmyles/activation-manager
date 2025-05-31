"""
Advanced Query Processor for Complex Semantic Search
Handles multi-faceted queries with concept extraction and relationship mapping
"""

import re
from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Try to import spacy, but it's optional
try:
    import os
    
    # Allow complete disabling of spaCy via environment variable
    if os.environ.get('DISABLE_SPACY', 'true').lower() == 'true':
        logger.info("📌 spaCy disabled by DISABLE_SPACY environment variable")
        spacy = None
        nlp = None
    else:
        logger.info("🔄 Checking for spaCy...")
        import spacy
        logger.info("  ✅ spaCy imported")
        try:
            # Add timeout and better error handling
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("spaCy model loading timed out")
            
            # Only try to load model in non-production environments
            if os.environ.get('GAE_ENV', '').startswith('standard'):
                logger.info("  📌 Skipping spaCy model load in production")
                nlp = None
            else:
                # Set a 5-second timeout for model loading
                if hasattr(signal, 'SIGALRM'):
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(5)
                    try:
                        logger.info("  🔄 Loading spaCy model...")
                        nlp = spacy.load("en_core_web_sm")
                        logger.info("  ✅ spaCy model loaded")
                    finally:
                        signal.alarm(0)
                else:
                    # Windows doesn't support SIGALRM
                    logger.info("  🔄 Loading spaCy model (no timeout)...")
                    nlp = spacy.load("en_core_web_sm")
                    logger.info("  ✅ spaCy model loaded")
        except Exception as e:
            logger.warning(f"  ⚠️ spaCy model not loaded: {type(e).__name__}: {str(e)[:100]}")
            logger.info("  💡 To install: python -m spacy download en_core_web_sm")
            nlp = None
except ImportError:
    logger.info("📌 spaCy not installed. Advanced NLP features will be limited.")
    spacy = None
    nlp = None


@dataclass
class QueryConcept:
    """Represents a concept extracted from the query"""
    text: str
    type: str  # demographic, financial, geographic, behavioral, temporal
    modifiers: List[str]  # high, low, conscious, etc.
    synonyms: List[str]
    related_terms: List[str]
    confidence: float


@dataclass
class ConceptRelationship:
    """Represents relationships between concepts"""
    concept1: QueryConcept
    concept2: QueryConcept
    relationship_type: str  # AND, OR, WITH, EXCLUDE
    strength: float


class AdvancedQueryProcessor:
    """Enhanced query processor that understands complex multi-faceted queries"""
    
    def __init__(self):
        self.concept_mappings = self._build_concept_mappings()
        self.generation_mappings = self._build_generation_mappings()
        self.behavioral_mappings = self._build_behavioral_mappings()
        self.geographic_mappings = self._build_geographic_mappings()
        self.financial_mappings = self._build_financial_mappings()
        
    def _build_concept_mappings(self) -> Dict[str, Dict]:
        """Build comprehensive concept mappings"""
        return {
            'environmental_consciousness': {
                'primary_terms': ['environmentally conscious', 'eco-friendly', 'green', 'sustainable'],
                'related_concepts': ['organic', 'renewable', 'carbon neutral', 'eco-aware'],
                'behavioral_indicators': ['recycling', 'hybrid vehicles', 'solar panels', 'composting'],
                'value_indicators': ['environmental protection', 'climate change awareness', 'conservation'],
                'product_preferences': ['organic food', 'electric vehicles', 'renewable energy', 'sustainable products']
            },
            'high_disposable_income': {
                'primary_terms': ['high disposable income', 'affluent', 'wealthy', 'high earners'],
                'income_ranges': ['100k+', '150k+', '200k+', 'top 10%', 'top 5%'],
                'spending_indicators': ['luxury', 'premium', 'discretionary spending', 'investments'],
                'lifestyle_markers': ['frequent travel', 'dining out', 'entertainment', 'savings']
            },
            'urban_lifestyle': {
                'primary_terms': ['urban', 'city', 'metropolitan', 'downtown'],
                'related_concepts': ['cosmopolitan', 'city center', 'high density', 'walkable'],
                'characteristics': ['public transit', 'apartment living', 'cultural activities', 'nightlife'],
                'opposites': ['rural', 'suburban', 'small town', 'countryside']
            }
        }
    
    def _build_generation_mappings(self) -> Dict[str, Dict]:
        """Build generation-specific mappings"""
        return {
            'millennials': {
                'birth_years': (1981, 1996),
                'age_range_2024': (28, 43),
                'characteristics': ['digital natives', 'tech-savvy', 'social media', 'work-life balance'],
                'values': ['experiences over possessions', 'diversity', 'sustainability', 'authenticity'],
                'life_stage': ['young professionals', 'new parents', 'first-time homebuyers'],
                'alternative_names': ['gen y', 'echo boomers', 'digital generation']
            },
            'gen_z': {
                'birth_years': (1997, 2012),
                'age_range_2024': (12, 27),
                'characteristics': ['mobile-first', 'social justice', 'entrepreneurial', 'pragmatic'],
                'values': ['inclusivity', 'mental health awareness', 'climate action', 'financial security']
            },
            'gen_x': {
                'birth_years': (1965, 1980),
                'age_range_2024': (44, 59),
                'characteristics': ['independent', 'resourceful', 'work-focused', 'skeptical'],
                'life_stage': ['established careers', 'teenage children', 'sandwich generation']
            },
            'boomers': {
                'birth_years': (1946, 1964),
                'age_range_2024': (60, 78),
                'characteristics': ['traditional media', 'brand loyal', 'retirement planning'],
                'alternative_names': ['baby boomers', 'seniors', 'retirees']
            }
        }
    
    def _build_behavioral_mappings(self) -> Dict[str, Dict]:
        """Build behavioral and psychographic mappings"""
        return {
            'environmentally_conscious': {
                'behaviors': ['recycling', 'composting', 'sustainable shopping', 'energy conservation'],
                'purchases': ['hybrid/electric vehicles', 'organic products', 'renewable energy', 'eco-friendly brands'],
                'values': ['environmental protection', 'future generations', 'corporate responsibility'],
                'media': ['environmental documentaries', 'sustainability blogs', 'green living magazines']
            },
            'health_conscious': {
                'behaviors': ['regular exercise', 'healthy eating', 'preventive care', 'wellness activities'],
                'purchases': ['organic food', 'fitness equipment', 'health supplements', 'wellness services'],
                'values': ['longevity', 'quality of life', 'holistic health', 'mindfulness']
            },
            'tech_savvy': {
                'behaviors': ['early adoption', 'online shopping', 'streaming services', 'smart home'],
                'purchases': ['latest gadgets', 'premium subscriptions', 'tech accessories', 'online services'],
                'values': ['innovation', 'connectivity', 'efficiency', 'convenience']
            }
        }
    
    def _build_geographic_mappings(self) -> Dict[str, Dict]:
        """Build geographic and location-based mappings"""
        return {
            'urban': {
                'characteristics': ['high density', 'public transit', 'walkable', 'diverse'],
                'lifestyle': ['apartment living', 'dining out', 'cultural events', 'nightlife'],
                'services': ['delivery services', 'ride-sharing', 'coworking spaces'],
                'challenges': ['higher cost of living', 'limited space', 'traffic', 'noise']
            },
            'suburban': {
                'characteristics': ['single-family homes', 'car-dependent', 'family-oriented', 'quieter'],
                'lifestyle': ['yard/garden', 'schools', 'shopping centers', 'commuting'],
                'values': ['space', 'safety', 'community', 'good schools']
            }
        }
    
    def _build_financial_mappings(self) -> Dict[str, Dict]:
        """Build financial and income-related mappings"""
        return {
            'high_income': {
                'indicators': ['six figures', '100k+', 'top quintile', 'affluent'],
                'behaviors': ['investing', 'luxury purchases', 'multiple properties', 'premium services'],
                'concerns': ['wealth management', 'tax optimization', 'estate planning']
            },
            'disposable_income': {
                'indicators': ['discretionary spending', 'savings', 'entertainment budget', 'travel budget'],
                'behaviors': ['frequent dining', 'premium brands', 'experiences', 'hobbies']
            }
        }
    
    def extract_concepts(self, query: str) -> List[QueryConcept]:
        """Extract semantic concepts from complex query"""
        concepts = []
        query_lower = query.lower()
        
        # 1. Extract generation/demographic concepts
        for gen, data in self.generation_mappings.items():
            if gen in query_lower or any(alt in query_lower for alt in data.get('alternative_names', [])):
                concepts.append(QueryConcept(
                    text=gen,
                    type='demographic',
                    modifiers=[],
                    synonyms=data.get('alternative_names', []),
                    related_terms=data.get('characteristics', []),
                    confidence=0.9
                ))
        
        # 2. Extract behavioral concepts
        for behavior, data in self.behavioral_mappings.items():
            if any(term in query_lower for term in [behavior] + data.get('behaviors', [])):
                concepts.append(QueryConcept(
                    text=behavior,
                    type='behavioral',
                    modifiers=self._extract_modifiers(query, behavior),
                    synonyms=data.get('behaviors', []),
                    related_terms=data.get('values', []),
                    confidence=0.85
                ))
        
        # 3. Extract financial concepts
        if any(term in query_lower for term in ['income', 'disposable', 'affluent', 'wealthy']):
            modifiers = self._extract_modifiers(query, 'income')
            concepts.append(QueryConcept(
                text='income level',
                type='financial',
                modifiers=modifiers,
                synonyms=self.financial_mappings['high_income']['indicators'],
                related_terms=self.financial_mappings['high_income']['behaviors'],
                confidence=0.9
            ))
        
        # 4. Extract geographic concepts
        for geo_type, data in self.geographic_mappings.items():
            if geo_type in query_lower or any(char in query_lower for char in data['characteristics']):
                concepts.append(QueryConcept(
                    text=geo_type,
                    type='geographic',
                    modifiers=[],
                    synonyms=data['characteristics'],
                    related_terms=data['lifestyle'],
                    confidence=0.85
                ))
        
        # 5. Use NLP for additional concept extraction if available
        if nlp and concepts:
            concepts.extend(self._extract_concepts_with_nlp(query))
        
        return concepts
    
    def _extract_modifiers(self, query: str, concept: str) -> List[str]:
        """Extract modifiers for a concept (e.g., 'high' income, 'very' conscious)"""
        modifiers = []
        modifier_words = ['high', 'low', 'very', 'extremely', 'moderate', 'strong', 'weak']
        
        words = query.lower().split()
        for i, word in enumerate(words):
            if concept in word or concept in ' '.join(words[max(0, i-2):i+3]):
                # Check surrounding words for modifiers
                for j in range(max(0, i-2), min(len(words), i+2)):
                    if words[j] in modifier_words:
                        modifiers.append(words[j])
        
        return modifiers
    
    def _extract_concepts_with_nlp(self, query: str) -> List[QueryConcept]:
        """Use spaCy NLP to extract additional concepts"""
        concepts = []
        doc = nlp(query)
        
        # Extract noun phrases that might be concepts
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ in ['NOUN', 'PROPN'] and len(chunk.text) > 3:
                # Classify the concept type based on its semantic similarity
                concept_type = self._classify_concept_type(chunk.text)
                if concept_type:
                    concepts.append(QueryConcept(
                        text=chunk.text,
                        type=concept_type,
                        modifiers=[token.text for token in chunk if token.pos_ == 'ADJ'],
                        synonyms=[],
                        related_terms=[],
                        confidence=0.7
                    ))
        
        return concepts
    
    def _classify_concept_type(self, text: str) -> str:
        """Classify concept type based on keywords"""
        text_lower = text.lower()
        
        if any(demo in text_lower for demo in ['age', 'generation', 'gender', 'family']):
            return 'demographic'
        elif any(fin in text_lower for fin in ['income', 'money', 'spending', 'wealth']):
            return 'financial'
        elif any(geo in text_lower for geo in ['city', 'urban', 'rural', 'area', 'region']):
            return 'geographic'
        elif any(beh in text_lower for beh in ['conscious', 'aware', 'focused', 'oriented']):
            return 'behavioral'
        else:
            return 'general'
    
    def identify_relationships(self, concepts: List[QueryConcept], query: str) -> List[ConceptRelationship]:
        """Identify relationships between extracted concepts"""
        relationships = []
        
        # Simple relationship detection based on query structure
        connectors = {
            'with': 'WITH',
            'and': 'AND',
            'or': 'OR',
            'but not': 'EXCLUDE',
            'except': 'EXCLUDE',
            'who are': 'WITH',
            'that have': 'WITH'
        }
        
        query_lower = query.lower()
        
        # Find relationships between adjacent concepts
        for i in range(len(concepts) - 1):
            for j in range(i + 1, len(concepts)):
                concept1 = concepts[i]
                concept2 = concepts[j]
                
                # Check for connecting words between concepts
                text_between = query_lower[
                    query_lower.find(concept1.text.lower()):
                    query_lower.find(concept2.text.lower())
                ]
                
                relationship_type = 'AND'  # Default
                strength = 0.5
                
                for connector, rel_type in connectors.items():
                    if connector in text_between:
                        relationship_type = rel_type
                        strength = 0.8
                        break
                
                relationships.append(ConceptRelationship(
                    concept1=concept1,
                    concept2=concept2,
                    relationship_type=relationship_type,
                    strength=strength
                ))
        
        return relationships
    
    def expand_query_semantically(self, query: str) -> Dict[str, Any]:
        """
        Expand query to capture full semantic meaning
        
        Returns a structured representation of the query with:
        - Extracted concepts
        - Relationships between concepts
        - Expanded search terms
        - Variable suggestions
        """
        # Extract concepts
        concepts = self.extract_concepts(query)
        
        # Identify relationships
        relationships = self.identify_relationships(concepts, query)
        
        # Build expanded search terms
        expanded_terms = set()
        variable_patterns = []
        
        for concept in concepts:
            # Add primary term and synonyms
            expanded_terms.add(concept.text)
            expanded_terms.update(concept.synonyms)
            expanded_terms.update(concept.related_terms)
            
            # Generate variable patterns based on concept type
            if concept.type == 'demographic':
                if 'millennial' in concept.text.lower():
                    variable_patterns.extend([
                        'AGE_25_34', 'AGE_35_44',  # Age ranges for millennials
                        'GENERATION_Y', 'MILLENNIALS'
                    ])
            
            elif concept.type == 'financial':
                if any(mod in concept.modifiers for mod in ['high', 'affluent']):
                    variable_patterns.extend([
                        'INCOME_100K_PLUS', 'INCOME_150K_PLUS',
                        'HIGH_DISPOSABLE_INCOME', 'AFFLUENT_HOUSEHOLDS'
                    ])
            
            elif concept.type == 'behavioral':
                if 'environmental' in concept.text:
                    variable_patterns.extend([
                        'GREEN_CONSUMERS', 'ECO_FRIENDLY',
                        'SUSTAINABLE_LIFESTYLE', 'ENVIRONMENTAL_VALUES'
                    ])
            
            elif concept.type == 'geographic':
                if 'urban' in concept.text:
                    variable_patterns.extend([
                        'URBAN_CORE', 'CITY_DWELLERS',
                        'METROPOLITAN_AREA', 'HIGH_DENSITY'
                    ])
        
        # Build search strategies
        search_strategies = self._build_search_strategies(concepts, relationships)
        
        return {
            'original_query': query,
            'concepts': [self._concept_to_dict(c) for c in concepts],
            'relationships': [self._relationship_to_dict(r) for r in relationships],
            'expanded_terms': list(expanded_terms),
            'variable_patterns': variable_patterns,
            'search_strategies': search_strategies,
            'query_interpretation': self._generate_interpretation(concepts, relationships)
        }
    
    def _concept_to_dict(self, concept: QueryConcept) -> Dict:
        """Convert concept to dictionary"""
        return {
            'text': concept.text,
            'type': concept.type,
            'modifiers': concept.modifiers,
            'synonyms': concept.synonyms,
            'related_terms': concept.related_terms,
            'confidence': concept.confidence
        }
    
    def _relationship_to_dict(self, relationship: ConceptRelationship) -> Dict:
        """Convert relationship to dictionary"""
        return {
            'concept1': relationship.concept1.text,
            'concept2': relationship.concept2.text,
            'type': relationship.relationship_type,
            'strength': relationship.strength
        }
    
    def _build_search_strategies(self, concepts: List[QueryConcept], 
                                relationships: List[ConceptRelationship]) -> List[Dict]:
        """Build specific search strategies based on concepts and relationships"""
        strategies = []
        
        # Strategy 1: Intersection of all concepts
        if len(concepts) > 1:
            strategies.append({
                'name': 'intersection_search',
                'description': 'Find variables that match ALL concepts',
                'weight': 0.8,
                'concept_weights': {c.text: c.confidence for c in concepts}
            })
        
        # Strategy 2: Weighted by concept type
        type_weights = {
            'demographic': 1.0,
            'financial': 0.9,
            'behavioral': 0.8,
            'geographic': 0.7
        }
        
        strategies.append({
            'name': 'weighted_type_search',
            'description': 'Prioritize by concept type importance',
            'weight': 0.7,
            'type_weights': {
                c.text: type_weights.get(c.type, 0.5) * c.confidence 
                for c in concepts
            }
        })
        
        # Strategy 3: Relationship-aware search
        if relationships:
            strategies.append({
                'name': 'relationship_search',
                'description': 'Consider relationships between concepts',
                'weight': 0.6,
                'relationships': [
                    {
                        'concepts': [r.concept1.text, r.concept2.text],
                        'type': r.relationship_type,
                        'strength': r.strength
                    }
                    for r in relationships
                ]
            })
        
        return strategies
    
    def _generate_interpretation(self, concepts: List[QueryConcept], 
                               relationships: List[ConceptRelationship]) -> str:
        """Generate human-readable interpretation of the query"""
        if not concepts:
            return "No specific concepts identified"
        
        interpretation = "Looking for "
        
        # Build description from concepts
        concept_descriptions = []
        for concept in concepts:
            desc = concept.text
            if concept.modifiers:
                desc = f"{' '.join(concept.modifiers)} {desc}"
            concept_descriptions.append(desc)
        
        # Join with relationships
        if len(concept_descriptions) == 1:
            interpretation += concept_descriptions[0]
        elif len(concept_descriptions) == 2:
            interpretation += f"{concept_descriptions[0]} with {concept_descriptions[1]}"
        else:
            interpretation += ', '.join(concept_descriptions[:-1])
            interpretation += f" and {concept_descriptions[-1]}"
        
        return interpretation


class QueryExpansionEngine:
    """Engine for expanding queries with semantic understanding"""
    
    def __init__(self, variable_metadata: Dict[str, Any]):
        self.variable_metadata = variable_metadata
        self.concept_to_variables = self._build_concept_mappings()
    
    def _build_concept_mappings(self) -> Dict[str, List[str]]:
        """Build mappings from concepts to relevant variables"""
        mappings = defaultdict(list)
        
        # This would be populated from your actual variable metadata
        # Example mappings:
        mappings['millennials'].extend([
            'AGE_25_34', 'AGE_35_44', 'GENERATION_Y'
        ])
        
        mappings['environmental_consciousness'].extend([
            'GREEN_LIFESTYLE', 'ORGANIC_BUYERS', 'HYBRID_OWNERS',
            'RENEWABLE_ENERGY_USERS', 'RECYCLING_BEHAVIOR'
        ])
        
        mappings['high_income'].extend([
            'INCOME_100K_149K', 'INCOME_150K_PLUS', 'TOP_10_PERCENT',
            'AFFLUENT_HOUSEHOLDS', 'HIGH_NET_WORTH'
        ])
        
        mappings['urban'].extend([
            'URBAN_CORE', 'CITY_CENTER', 'METROPOLITAN',
            'HIGH_DENSITY_AREA', 'TRANSIT_USERS'
        ])
        
        return dict(mappings)
    
    def suggest_variables_for_concepts(self, concepts: List[str]) -> List[Dict[str, Any]]:
        """Suggest specific variables based on extracted concepts"""
        suggestions = []
        seen_variables = set()
        
        for concept in concepts:
            if concept in self.concept_to_variables:
                for var_code in self.concept_to_variables[concept]:
                    if var_code not in seen_variables:
                        seen_variables.add(var_code)
                        suggestions.append({
                            'code': var_code,
                            'concept': concept,
                            'relevance': 0.9
                        })
        
        return suggestions