"""
Semantic Query Optimizer
Optimizes complex queries by understanding intent and reformulating for better results
"""

import re
from typing import List, Dict, Tuple, Set, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuerySegment:
    """Represents a semantic segment of a query"""
    text: str
    intent: str  # filter, expand, combine, exclude
    entities: List[str]
    modifiers: List[str]
    weight: float


class SemanticQueryOptimizer:
    """Optimizes queries for better semantic search results"""
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.entity_patterns = self._build_entity_patterns()
        self.modifier_mappings = self._build_modifier_mappings()
    
    def _build_intent_patterns(self) -> Dict[str, List[Tuple[str, float]]]:
        """Build patterns for detecting query intent"""
        return {
            'filter': [
                (r'\bwith\s+(?:high|low|moderate)\s+\w+', 0.9),
                (r'\bthat\s+(?:have|has|are)\b', 0.8),
                (r'\b(?:only|just|specifically)\b', 0.85),
                (r'\bwho\s+(?:are|have)\b', 0.8)
            ],
            'expand': [
                (r'\b(?:similar to|like|such as)\b', 0.9),
                (r'\b(?:related|comparable|equivalent)\b', 0.85),
                (r'\b(?:or similar|or equivalent)\b', 0.8)
            ],
            'combine': [
                (r'\b(?:and|with|plus|including)\b', 0.7),
                (r'\b(?:both|all|together with)\b', 0.8),
                (r'\b(?:as well as|along with)\b', 0.75)
            ],
            'exclude': [
                (r'\b(?:not|except|excluding|without)\b', 0.9),
                (r'\b(?:but not|other than)\b', 0.85),
                (r'\b(?:avoid|minus)\b', 0.8)
            ]
        }
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for extracting entities"""
        return {
            'demographic': [
                'millennials', 'gen z', 'boomers', 'seniors', 'youth',
                'families', 'singles', 'couples', 'parents', 'children'
            ],
            'financial': [
                'income', 'wealth', 'spending', 'disposable', 'affluent',
                'budget', 'debt', 'savings', 'investments', 'earnings'
            ],
            'behavioral': [
                'conscious', 'aware', 'focused', 'oriented', 'minded',
                'friendly', 'savvy', 'active', 'engaged', 'interested'
            ],
            'geographic': [
                'urban', 'suburban', 'rural', 'city', 'metropolitan',
                'downtown', 'residential', 'commercial', 'neighborhood'
            ],
            'psychographic': [
                'lifestyle', 'values', 'attitudes', 'interests', 'opinions',
                'preferences', 'motivations', 'aspirations', 'beliefs'
            ]
        }
    
    def _build_modifier_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Build mappings for query modifiers"""
        return {
            'intensity': {
                'high': ['very', 'extremely', 'highly', 'significantly', 'substantially'],
                'moderate': ['somewhat', 'moderately', 'fairly', 'reasonably'],
                'low': ['slightly', 'marginally', 'minimally', 'barely']
            },
            'specificity': {
                'specific': ['exactly', 'precisely', 'specifically', 'particularly'],
                'general': ['generally', 'broadly', 'overall', 'typically']
            },
            'temporal': {
                'recent': ['new', 'recent', 'current', 'latest', 'modern'],
                'established': ['traditional', 'established', 'long-term', 'historical']
            }
        }
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        """
        Optimize a complex query for better search results
        
        Returns:
            Optimized query structure with segments, reformulations, and strategies
        """
        # Segment the query
        segments = self._segment_query(query)
        
        # Extract global entities and modifiers
        global_entities = self._extract_entities(query)
        global_modifiers = self._extract_modifiers(query)
        
        # Generate query reformulations
        reformulations = self._generate_reformulations(query, segments)
        
        # Build search strategies
        strategies = self._build_search_strategies(segments, global_entities)
        
        # Generate optimized query variations
        variations = self._generate_query_variations(query, segments)
        
        return {
            'original_query': query,
            'segments': [self._segment_to_dict(s) for s in segments],
            'entities': global_entities,
            'modifiers': global_modifiers,
            'reformulations': reformulations,
            'strategies': strategies,
            'variations': variations,
            'optimization_score': self._calculate_optimization_score(segments)
        }
    
    def _segment_query(self, query: str) -> List[QuerySegment]:
        """Segment query into semantic components"""
        segments = []
        remaining_query = query.lower()
        
        # Find intent patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern, weight in patterns:
                matches = list(re.finditer(pattern, remaining_query))
                for match in matches:
                    segment_text = match.group(0)
                    
                    # Extract entities and modifiers for this segment
                    segment_entities = self._extract_entities(segment_text)
                    segment_modifiers = self._extract_modifiers(segment_text)
                    
                    segments.append(QuerySegment(
                        text=segment_text,
                        intent=intent,
                        entities=segment_entities,
                        modifiers=segment_modifiers,
                        weight=weight
                    ))
        
        # Handle remaining text as general segment
        if segments:
            # Remove found segments from query
            for segment in segments:
                remaining_query = remaining_query.replace(segment.text, ' ')
        
        remaining_text = remaining_query.strip()
        if remaining_text:
            segments.append(QuerySegment(
                text=remaining_text,
                intent='general',
                entities=self._extract_entities(remaining_text),
                modifiers=self._extract_modifiers(remaining_text),
                weight=0.5
            ))
        
        return segments
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract semantic entities from text"""
        entities = []
        text_lower = text.lower()
        
        for entity_type, entity_list in self.entity_patterns.items():
            for entity in entity_list:
                if entity in text_lower:
                    entities.append(f"{entity_type}:{entity}")
        
        return entities
    
    def _extract_modifiers(self, text: str) -> List[str]:
        """Extract modifiers from text"""
        modifiers = []
        text_lower = text.lower()
        
        for modifier_type, modifier_groups in self.modifier_mappings.items():
            for group_name, words in modifier_groups.items():
                for word in words:
                    if word in text_lower:
                        modifiers.append(f"{modifier_type}:{group_name}:{word}")
        
        return modifiers
    
    def _generate_reformulations(self, query: str, segments: List[QuerySegment]) -> List[Dict[str, Any]]:
        """Generate alternative query formulations"""
        reformulations = []
        
        # Strategy 1: Emphasize high-weight segments
        high_weight_segments = [s for s in segments if s.weight > 0.8]
        if high_weight_segments:
            emphasized_query = query
            for segment in high_weight_segments:
                # Duplicate important terms
                emphasized_query = emphasized_query.replace(
                    segment.text, 
                    f"{segment.text} {segment.text}"
                )
            reformulations.append({
                'query': emphasized_query,
                'strategy': 'emphasis',
                'description': 'Emphasize high-importance segments'
            })
        
        # Strategy 2: Expand with synonyms
        expanded_terms = []
        for segment in segments:
            if segment.intent in ['filter', 'combine']:
                # Add synonyms for key terms
                for entity in segment.entities:
                    entity_type, entity_value = entity.split(':', 1)
                    if entity_type == 'behavioral':
                        if 'conscious' in entity_value:
                            expanded_terms.extend(['aware', 'mindful', 'considerate'])
                        elif 'friendly' in entity_value:
                            expanded_terms.extend(['positive', 'supportive', 'favorable'])
        
        if expanded_terms:
            reformulations.append({
                'query': f"{query} {' '.join(expanded_terms)}",
                'strategy': 'synonym_expansion',
                'description': 'Add synonyms for key concepts'
            })
        
        # Strategy 3: Restructure for clarity
        if len(segments) > 2:
            # Reorder by intent priority
            priority_order = ['filter', 'exclude', 'combine', 'expand', 'general']
            sorted_segments = sorted(segments, 
                                   key=lambda s: priority_order.index(s.intent) 
                                   if s.intent in priority_order else 99)
            
            restructured = ' '.join(s.text for s in sorted_segments)
            reformulations.append({
                'query': restructured,
                'strategy': 'restructure',
                'description': 'Reorder segments by logical priority'
            })
        
        return reformulations
    
    def _build_search_strategies(self, segments: List[QuerySegment], 
                               entities: List[str]) -> List[Dict[str, Any]]:
        """Build specific search strategies based on query analysis"""
        strategies = []
        
        # Strategy for multi-concept queries
        entity_types = set(e.split(':')[0] for e in entities)
        if len(entity_types) >= 3:
            strategies.append({
                'name': 'multi_dimensional_search',
                'description': 'Search across multiple dimensions simultaneously',
                'approach': 'weighted_intersection',
                'weights': {
                    'demographic': 1.0,
                    'financial': 0.9,
                    'behavioral': 0.85,
                    'geographic': 0.8
                }
            })
        
        # Strategy for exclusion queries
        exclude_segments = [s for s in segments if s.intent == 'exclude']
        if exclude_segments:
            strategies.append({
                'name': 'exclusion_search',
                'description': 'Apply negative filters after initial search',
                'approach': 'post_filter',
                'exclude_terms': [e.split(':')[1] for s in exclude_segments for e in s.entities]
            })
        
        # Strategy for expansion queries
        expand_segments = [s for s in segments if s.intent == 'expand']
        if expand_segments:
            strategies.append({
                'name': 'similarity_expansion',
                'description': 'Find similar concepts and related variables',
                'approach': 'semantic_similarity',
                'expansion_depth': 2
            })
        
        return strategies
    
    def _generate_query_variations(self, query: str, segments: List[QuerySegment]) -> List[str]:
        """Generate query variations for better coverage"""
        variations = [query]  # Original query
        
        # Variation 1: Focus on entities only
        all_entities = []
        for segment in segments:
            all_entities.extend([e.split(':')[1] for e in segment.entities])
        if all_entities:
            variations.append(' '.join(set(all_entities)))
        
        # Variation 2: High-weight segments only
        high_weight_text = ' '.join(s.text for s in segments if s.weight > 0.7)
        if high_weight_text and high_weight_text != query:
            variations.append(high_weight_text)
        
        # Variation 3: Simplified query (remove modifiers)
        simplified = query
        for segment in segments:
            for modifier in segment.modifiers:
                modifier_word = modifier.split(':')[-1]
                simplified = simplified.replace(modifier_word, '')
        simplified = ' '.join(simplified.split())  # Clean up spaces
        if simplified != query:
            variations.append(simplified)
        
        return list(set(variations))  # Remove duplicates
    
    def _segment_to_dict(self, segment: QuerySegment) -> Dict[str, Any]:
        """Convert segment to dictionary"""
        return {
            'text': segment.text,
            'intent': segment.intent,
            'entities': segment.entities,
            'modifiers': segment.modifiers,
            'weight': segment.weight
        }
    
    def _calculate_optimization_score(self, segments: List[QuerySegment]) -> float:
        """Calculate how well the query can be optimized"""
        if not segments:
            return 0.0
        
        # Factors that improve optimization potential
        score = 0.0
        
        # Clear intent signals
        intent_clarity = sum(s.weight for s in segments if s.intent != 'general') / len(segments)
        score += intent_clarity * 0.4
        
        # Entity richness
        total_entities = sum(len(s.entities) for s in segments)
        entity_richness = min(total_entities / (len(segments) * 2), 1.0)
        score += entity_richness * 0.3
        
        # Modifier presence
        total_modifiers = sum(len(s.modifiers) for s in segments)
        modifier_presence = min(total_modifiers / len(segments), 1.0)
        score += modifier_presence * 0.2
        
        # Segment variety
        unique_intents = len(set(s.intent for s in segments))
        intent_variety = unique_intents / 4.0  # Max 4 intent types
        score += intent_variety * 0.1
        
        return min(score, 1.0)