"""
Enhanced Semantic Search V2 - Improved Complex Query Handling
Builds on the existing system with better understanding of multi-faceted queries
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Set
import logging
from collections import defaultdict
import re
from difflib import SequenceMatcher

from .enhanced_semantic_search import (
    EnhancedSemanticSearch, EnhancedVariable, SearchConfig, 
    DOMAIN_CONFIGS, HybridScorer
)
from .advanced_query_processor import AdvancedQueryProcessor, QueryConcept

logger = logging.getLogger(__name__)


class ConceptAwareScorer(HybridScorer):
    """Enhanced scorer that understands concept relationships"""
    
    def __init__(self, config: SearchConfig, domain_configs: Dict, concept_weights: Dict[str, float]):
        super().__init__(config, domain_configs)
        self.concept_weights = concept_weights
    
    def calculate_concept_aware_score(self, base_score: float, variable: EnhancedVariable, 
                                    concepts: List[QueryConcept], 
                                    query_context: Dict) -> float:
        """Calculate score with concept awareness"""
        # Start with base hybrid score
        score = base_score
        
        # Boost for concept matches
        concept_boost = 0.0
        matched_concepts = set()
        
        for concept in concepts:
            # Check if variable matches concept
            if self._variable_matches_concept(variable, concept):
                matched_concepts.add(concept.type)
                # Weight by concept confidence and type
                weight = self.concept_weights.get(concept.type, 0.5) * concept.confidence
                concept_boost += weight
        
        # Multi-concept bonus - reward variables that match multiple concepts
        if len(matched_concepts) > 1:
            multi_concept_bonus = 0.2 * (len(matched_concepts) - 1)
            score *= (1 + multi_concept_bonus)
        
        # Apply concept boost
        score *= (1 + concept_boost)
        
        # Penalty for missing important concepts
        important_types = {'demographic', 'financial'}
        important_concepts = [c for c in concepts if c.type in important_types]
        if important_concepts:
            matched_important = sum(1 for c in important_concepts 
                                  if self._variable_matches_concept(variable, c))
            coverage = matched_important / len(important_concepts)
            if coverage < 0.5:
                score *= (0.5 + coverage * 0.5)  # Penalty for low coverage
        
        return score
    
    def _variable_matches_concept(self, variable: EnhancedVariable, concept: QueryConcept) -> bool:
        """Check if a variable matches a concept"""
        var_text = f"{variable.description} {variable.category} {' '.join(variable.enriched_keywords)}".lower()
        
        # Check primary term
        if concept.text.lower() in var_text:
            return True
        
        # Check synonyms
        for synonym in concept.synonyms:
            if synonym.lower() in var_text:
                return True
        
        # Check related terms
        for term in concept.related_terms[:3]:  # Limit to avoid false positives
            if term.lower() in var_text:
                return True
        
        # Special handling for specific concept types
        if concept.type == 'demographic' and 'millennial' in concept.text.lower():
            # Check age ranges that correspond to millennials
            age_patterns = [r'25[\s-]?(?:to|-)[\s-]?34', r'35[\s-]?(?:to|-)[\s-]?44']
            for pattern in age_patterns:
                if re.search(pattern, variable.description, re.IGNORECASE):
                    return True
        
        elif concept.type == 'financial' and any(mod in concept.modifiers for mod in ['high', 'affluent']):
            # Check for high income indicators
            income_patterns = [r'100k\+?', r'150k\+?', r'200k\+?', r'high[\s-]?income', r'affluent']
            for pattern in income_patterns:
                if re.search(pattern, var_text, re.IGNORECASE):
                    return True
        
        return False


class EnhancedSemanticSearchV2(EnhancedSemanticSearch):
    """Enhanced semantic search with advanced query understanding"""
    
    def __init__(self, variables: List[Dict[str, Any]], 
                 embeddings: Optional[np.ndarray] = None,
                 openai_api_key: Optional[str] = None):
        """Initialize enhanced search v2"""
        logger.info("🚀 Initializing EnhancedSemanticSearchV2...")
        super().__init__(variables, embeddings, openai_api_key)
        logger.info("  ✅ Parent class initialized")
        
        # Initialize advanced query processor
        logger.info("  🔄 Creating AdvancedQueryProcessor...")
        self.query_processor_advanced = AdvancedQueryProcessor()
        logger.info("  ✅ AdvancedQueryProcessor created")
        
        # Concept importance weights
        self.concept_weights = {
            'demographic': 1.0,
            'financial': 0.9,
            'behavioral': 0.85,
            'geographic': 0.8,
            'temporal': 0.7,
            'general': 0.6
        }
        logger.info("✅ EnhancedSemanticSearchV2 initialization complete")
    
    def search(self, query: str, top_k: int = 50, use_semantic: bool = True, 
               use_keyword: bool = True, filters: Optional[Dict] = None,
               use_advanced_processing: bool = True, filter_similar: bool = False,
               similarity_threshold: float = 0.85, max_similar_per_group: int = 2) -> Dict[str, Any]:
        """
        Enhanced search with advanced query processing
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            use_semantic: Whether to use semantic search
            use_keyword: Whether to use keyword search
            filters: Optional filters
            use_advanced_processing: Whether to use advanced concept extraction
            filter_similar: Whether to filter similar variables (default False)
            similarity_threshold: Minimum similarity to consider variables as similar (0-1)
            max_similar_per_group: Maximum number of similar variables to keep per group
            
        Returns:
            Search results with enhanced metadata
        """
        # Process query with advanced processor if enabled
        if use_advanced_processing:
            advanced_context = self.query_processor_advanced.expand_query_semantically(query)
            
            # Use expanded terms for search
            expanded_query = ' '.join(advanced_context['expanded_terms'])
            
            # Get base results using parent class
            base_results = super().search(
                expanded_query, 
                top_k=top_k * 2,  # Get more candidates for re-ranking
                use_semantic=use_semantic,
                use_keyword=use_keyword,
                filters=filters
            )
            
            # Re-rank with concept awareness
            concepts = [
                QueryConcept(**concept_dict) 
                for concept_dict in advanced_context['concepts']
            ]
            
            reranked_results = self._rerank_with_concepts(
                base_results['results'],
                concepts,
                advanced_context,
                top_k
            )
            
            # Enhance results with concept matching information
            enhanced_results = self._enhance_results_with_concepts(
                reranked_results,
                concepts,
                advanced_context
            )
            
            # Apply similarity filtering if enabled
            if filter_similar:
                logger.info(f"✅ Applying similarity filtering in advanced path to {len(enhanced_results)} results")
                enhanced_results = self._filter_similar_variables(
                    enhanced_results,
                    similarity_threshold=similarity_threshold,
                    max_similar_per_group=max_similar_per_group
                )
            else:
                logger.info(f"⚠️ Filtering skipped in advanced path: filter_similar={filter_similar}")
            
            # Add advanced context to response
            base_results['results'] = enhanced_results
            base_results['total_found'] = len(enhanced_results)
            base_results['advanced_context'] = advanced_context
            base_results['query_interpretation'] = advanced_context['query_interpretation']
            
            return base_results
        else:
            # Fall back to standard search
            logger.info(f"📍 Using standard search path, filter_similar={filter_similar}")
            results = super().search(query, top_k, use_semantic, use_keyword, filters)
            
            # Apply similarity filtering if enabled
            if filter_similar and 'results' in results:
                logger.info(f"✅ Applying similarity filtering to {len(results.get('results', []))} results")
                original_count = len(results['results'])
                filtered_results = self._filter_similar_variables(
                    results['results'],
                    similarity_threshold=similarity_threshold,
                    max_similar_per_group=max_similar_per_group
                )
                results['results'] = filtered_results
                results['total_found'] = len(filtered_results)
                logger.info(f"📊 Standard path filtering: {original_count} → {len(filtered_results)} results")
            else:
                logger.info(f"⚠️ Filtering skipped: filter_similar={filter_similar}, has_results={'results' in results}")
            
            return results
    
    def _rerank_with_concepts(self, results: List[Dict], concepts: List[QueryConcept],
                            advanced_context: Dict, top_k: int) -> List[Dict]:
        """Re-rank results based on concept matching"""
        # Create concept-aware scorer
        scorer = ConceptAwareScorer(self.config, DOMAIN_CONFIGS, self.concept_weights)
        
        # Re-score all results
        for result in results:
            # Get the variable object
            var = self.variable_lookup.get(result['code'])
            if var:
                # Calculate concept-aware score
                base_score = result.get('score', 0)
                new_score = scorer.calculate_concept_aware_score(
                    base_score, var, concepts, advanced_context
                )
                result['original_score'] = base_score
                result['score'] = new_score
        
        # Sort by new scores
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def _enhance_results_with_concepts(self, results: List[Dict], 
                                     concepts: List[QueryConcept],
                                     advanced_context: Dict) -> List[Dict]:
        """Add concept matching information to results"""
        for result in results:
            var = self.variable_lookup.get(result['code'])
            if var:
                # Track which concepts this variable matches
                matched_concepts = []
                concept_coverage = {}
                
                for concept in concepts:
                    if self._check_concept_match(var, concept):
                        matched_concepts.append({
                            'concept': concept.text,
                            'type': concept.type,
                            'confidence': concept.confidence,
                            'match_reason': self._get_match_reason(var, concept)
                        })
                        
                        if concept.type not in concept_coverage:
                            concept_coverage[concept.type] = 0
                        concept_coverage[concept.type] += 1
                
                # Calculate coverage score
                total_concept_types = len(set(c.type for c in concepts))
                covered_types = len(concept_coverage)
                coverage_score = covered_types / total_concept_types if total_concept_types > 0 else 0
                
                # Add enhanced metadata
                result['matched_concepts'] = matched_concepts
                result['concept_coverage'] = concept_coverage
                result['coverage_score'] = coverage_score
                result['relevance_explanation'] = self._generate_relevance_explanation(
                    var, matched_concepts, advanced_context
                )
        
        return results
    
    def _check_concept_match(self, variable: EnhancedVariable, concept: QueryConcept) -> bool:
        """Check if variable matches a concept"""
        scorer = ConceptAwareScorer(self.config, DOMAIN_CONFIGS, self.concept_weights)
        return scorer._variable_matches_concept(variable, concept)
    
    def _get_match_reason(self, variable: EnhancedVariable, concept: QueryConcept) -> str:
        """Get explanation for why variable matches concept"""
        var_text = f"{variable.description} {variable.category}".lower()
        
        if concept.text.lower() in var_text:
            return f"Direct match: '{concept.text}'"
        
        for synonym in concept.synonyms:
            if synonym.lower() in var_text:
                return f"Synonym match: '{synonym}'"
        
        for term in concept.related_terms:
            if term.lower() in var_text:
                return f"Related term: '{term}'"
        
        # Special cases
        if concept.type == 'demographic' and 'age' in var_text:
            return "Age-based demographic match"
        elif concept.type == 'financial' and any(ind in var_text for ind in ['income', 'spending']):
            return "Financial indicator match"
        
        return "Semantic similarity"
    
    def _generate_relevance_explanation(self, variable: EnhancedVariable, 
                                      matched_concepts: List[Dict],
                                      context: Dict) -> str:
        """Generate detailed relevance explanation"""
        if not matched_concepts:
            return "Keyword match only"
        
        explanations = []
        
        # Group by concept type
        by_type = defaultdict(list)
        for match in matched_concepts:
            by_type[match['type']].append(match)
        
        # Generate explanations by type
        if 'demographic' in by_type:
            demo_concepts = [m['concept'] for m in by_type['demographic']]
            explanations.append(f"Matches demographic criteria: {', '.join(demo_concepts)}")
        
        if 'financial' in by_type:
            fin_concepts = [m['concept'] for m in by_type['financial']]
            explanations.append(f"Matches financial profile: {', '.join(fin_concepts)}")
        
        if 'behavioral' in by_type:
            beh_concepts = [m['concept'] for m in by_type['behavioral']]
            explanations.append(f"Indicates behaviors: {', '.join(beh_concepts)}")
        
        if 'geographic' in by_type:
            geo_concepts = [m['concept'] for m in by_type['geographic']]
            explanations.append(f"Geographic match: {', '.join(geo_concepts)}")
        
        return " | ".join(explanations)
    
    def get_concept_suggestions(self, query: str) -> Dict[str, Any]:
        """Get concept-based variable suggestions"""
        # Extract concepts
        advanced_context = self.query_processor_advanced.expand_query_semantically(query)
        concepts = [QueryConcept(**c) for c in advanced_context['concepts']]
        
        # Group variables by concept match
        suggestions = {
            'by_concept': defaultdict(list),
            'combinations': [],
            'missing_concepts': []
        }
        
        # Find variables for each concept
        for concept in concepts:
            concept_vars = []
            for var in self.variables[:100]:  # Sample for performance
                if self._check_concept_match(var, concept):
                    concept_vars.append({
                        'code': var.code,
                        'description': var.description,
                        'match_reason': self._get_match_reason(var, concept)
                    })
            
            suggestions['by_concept'][concept.text] = concept_vars[:10]
            
            if not concept_vars:
                suggestions['missing_concepts'].append({
                    'concept': concept.text,
                    'type': concept.type,
                    'alternatives': concept.synonyms[:3]
                })
        
        # Suggest combinations
        if len(concepts) >= 2:
            # Find variables that match multiple concepts
            multi_match_vars = []
            for var in self.variables[:200]:  # Sample
                matched_concepts = [c for c in concepts if self._check_concept_match(var, c)]
                if len(matched_concepts) >= 2:
                    multi_match_vars.append({
                        'code': var.code,
                        'description': var.description,
                        'matched_concepts': [c.text for c in matched_concepts],
                        'match_count': len(matched_concepts)
                    })
            
            # Sort by number of matched concepts
            multi_match_vars.sort(key=lambda x: x['match_count'], reverse=True)
            suggestions['combinations'] = multi_match_vars[:10]
        
        return suggestions
    
    def _jaro_winkler_similarity(self, s1: str, s2: str, p: float = 0.1) -> float:
        """
        Calculate Jaro-Winkler similarity between two strings
        
        Args:
            s1: First string
            s2: Second string
            p: Scaling factor (default 0.1, should not exceed 0.25)
            
        Returns:
            Similarity score between 0 and 1
        """
        # Convert to lowercase for comparison
        s1, s2 = s1.lower(), s2.lower()
        
        len_s1, len_s2 = len(s1), len(s2)
        
        # If either string is empty
        if len_s1 == 0 or len_s2 == 0:
            # Both empty strings are considered identical
            return 1.0 if len_s1 == 0 and len_s2 == 0 else 0.0
        
        # If strings are identical
        if s1 == s2:
            return 1.0
        
        # Calculate the match window
        match_window = max(len_s1, len_s2) // 2 - 1
        if match_window < 1:
            match_window = 1
        
        # Initialize the matched arrays
        s1_matches = [False] * len_s1
        s2_matches = [False] * len_s2
        
        matches = 0
        transpositions = 0
        
        # Find matches
        for i in range(len_s1):
            start = max(0, i - match_window)
            end = min(i + match_window + 1, len_s2)
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Find transpositions
        k = 0
        for i in range(len_s1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        
        # Calculate Jaro similarity
        jaro = (matches / len_s1 + matches / len_s2 + 
                (matches - transpositions / 2) / matches) / 3.0
        
        # Calculate common prefix length (up to 4 chars)
        common_prefix = 0
        for i in range(min(len_s1, len_s2, 4)):
            if s1[i] == s2[i]:
                common_prefix += 1
            else:
                break
        
        # Calculate Jaro-Winkler similarity
        jaro_winkler = jaro + common_prefix * p * (1 - jaro)
        
        return jaro_winkler
    
    def _filter_similar_variables(self, results: List[Dict], 
                                similarity_threshold: float = 0.85,
                                max_similar_per_group: int = 2) -> List[Dict]:
        """
        Filter out similar variables to reduce redundancy
        Enhanced to handle base pattern grouping for cases like "Contact with friends [Pst Mth] - ..."
        
        Args:
            results: List of search results
            similarity_threshold: Minimum similarity to consider variables as similar (0-1)
            max_similar_per_group: Maximum number of similar variables to keep per group
            
        Returns:
            Filtered list of results
        """
        logger.info(f"🔍 _filter_similar_variables called with {len(results)} results, threshold={similarity_threshold}, max_per_group={max_similar_per_group}")
        
        if not results:
            return results
        
        # Step 1: Extract base patterns and group by them
        from collections import defaultdict
        base_pattern_groups = defaultdict(list)
        
        for i, result in enumerate(results):
            desc = result.get('description', '').strip()
            
            # Always store index, even for empty descriptions
            result['_index'] = i
            
            if not desc:
                # Empty description - use a special key
                result['_base_pattern'] = '__empty__'
                base_pattern_groups['__empty__'].append(result)
                continue
            
            # Extract base pattern (text before first hyphen or bracket pattern)
            # Examples: 
            # "Contact with friends [Pst Mth] - Similar income - All" -> "Contact with friends [Pst Mth]"
            # "Household Income $0-$20K" -> "Household Income"
            
            # Look for pattern with brackets followed by hyphen
            if ' - ' in desc:
                parts = desc.split(' - ')
                base_pattern = parts[0].strip()
            else:
                # For other patterns, take first few words or up to certain length
                words = desc.split()
                if len(words) > 3:
                    base_pattern = ' '.join(words[:3])
                else:
                    base_pattern = desc
            
            # Base pattern was already set above
            result['_base_pattern'] = base_pattern
            
            # Group by base pattern AND similar scores
            score = round(result.get('score', 0), 1)  # Round to nearest 0.1
            group_key = f"{base_pattern}:::{score}"
            base_pattern_groups[group_key].append(result)
        
        # Step 2: Filter within each base pattern group
        filtered_results = []
        processed_indices = set()
        
        # Process groups with most items first (to handle the worst offenders)
        sorted_groups = sorted(base_pattern_groups.items(), 
                             key=lambda x: len(x[1]), reverse=True)
        
        for group_key, group_results in sorted_groups:
            if not group_results:
                continue
            
            # If group is small enough, keep all
            if len(group_results) <= max_similar_per_group:
                filtered_results.extend(group_results)
                for r in group_results:
                    processed_indices.add(r['_index'])
                continue
            
            # For larger groups, apply similarity filtering with more aggressive threshold
            group_filtered = []
            group_processed = set()
            
            # Use more aggressive threshold for base pattern groups
            group_threshold = min(similarity_threshold, 0.75)
            
            # Sort by score and description length (prefer more complete descriptions)
            group_results.sort(key=lambda x: (
                -x.get('score', 0),  # Higher score first
                -len(x.get('description', '')),  # Longer descriptions (more specific)
                x.get('description', '')  # Then alphabetically
            ))
            
            for result in group_results:
                idx = result['_index']
                if idx in group_processed:
                    continue
                
                # Check similarity with already selected items in this group
                is_too_similar = False
                desc1 = result.get('description', '')
                
                for selected in group_filtered:
                    desc2 = selected.get('description', '')
                    similarity = self._jaro_winkler_similarity(desc1, desc2)
                    
                    if similarity >= group_threshold:
                        is_too_similar = True
                        break
                
                if not is_too_similar:
                    group_filtered.append(result)
                    group_processed.add(idx)
                    
                    # Stop if we have enough representatives
                    if len(group_filtered) >= max_similar_per_group:
                        break
            
            # Add filtered group results
            filtered_results.extend(group_filtered)
            for r in group_results:
                processed_indices.add(r['_index'])
            
            # Log if we filtered a lot
            if len(group_results) > len(group_filtered):
                base_pattern = group_key.split(':::')[0]
                logger.debug(f"Filtered base pattern '{base_pattern[:50]}...': {len(group_results)} -> {len(group_filtered)}")
        
        # Step 3: Add any results not in base pattern groups (edge cases)
        unprocessed_count = 0
        for i, result in enumerate(results):
            if i not in processed_indices:
                filtered_results.append(result)
                unprocessed_count += 1
        
        if unprocessed_count > 0:
            logger.warning(f"⚠️ Added {unprocessed_count} unprocessed results back to filtered results")
        
        # Clean up temporary fields
        for result in filtered_results:
            result.pop('_index', None)
            result.pop('_base_pattern', None)
        
        # Sort by original score
        filtered_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Similarity filtering: {len(results)} -> {len(filtered_results)} results")
        
        # Final verification
        contact_count = sum(1 for r in filtered_results if 'Contact with friends' in r.get('description', ''))
        if contact_count > 0:
            logger.info(f"🎯 Contact with friends in filtered results: {contact_count}")
        
        return filtered_results


def create_enhanced_search_v2(variables: List[Dict[str, Any]], 
                             embeddings: Optional[np.ndarray] = None,
                             openai_api_key: Optional[str] = None) -> EnhancedSemanticSearchV2:
    """Factory function to create enhanced search v2 instance"""
    return EnhancedSemanticSearchV2(variables, embeddings, openai_api_key)