"""
Unit tests for Enhanced Semantic Search V2
Tests concept-aware scoring, re-ranking, and complex query handling
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from activation_manager.core.enhanced_semantic_search_v2 import (
    EnhancedSemanticSearchV2, ConceptAwareScorer, create_enhanced_search_v2
)
from activation_manager.core.enhanced_semantic_search import SearchConfig, EnhancedVariable
from activation_manager.core.advanced_query_processor import QueryConcept


class TestConceptAwareScorer:
    """Test suite for Concept Aware Scorer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = SearchConfig()
        self.domain_configs = {}
        self.concept_weights = {
            'demographic': 1.0,
            'financial': 0.9,
            'behavioral': 0.85,
            'geographic': 0.8
        }
        self.scorer = ConceptAwareScorer(self.config, self.domain_configs, self.concept_weights)
    
    def test_single_concept_scoring(self):
        """Test scoring with single concept match"""
        # Create test variable
        var = EnhancedVariable(
            code="MILL_HIGH_INC",
            description="Millennials with household income $100k+",
            category="Demographics",
            theme="Income",
            product="",
            domain="demographic"
        )
        
        # Create test concept
        concept = QueryConcept(
            text="millennials",
            type="demographic",
            confidence=0.9,
            synonyms=["gen y", "echo boomers"],
            related_terms=["young adults"],
            modifiers=[]
        )
        
        # Calculate score
        base_score = 0.5
        new_score = self.scorer.calculate_concept_aware_score(
            base_score, var, [concept], {}
        )
        
        # Score should be boosted
        assert new_score > base_score
    
    def test_multi_concept_bonus(self):
        """Test bonus scoring for multiple concept matches"""
        # Create test variable that matches multiple concepts
        var = EnhancedVariable(
            code="URBAN_MILL_HIGH_INC",
            description="Urban millennials with high income",
            category="Demographics",
            theme="Income",
            product="",
            domain="demographic"
        )
        
        # Create multiple concepts
        concepts = [
            QueryConcept(
                text="urban",
                type="geographic",
                confidence=0.85,
                synonyms=["city", "metropolitan"],
                related_terms=["downtown"],
                modifiers=[]
            ),
            QueryConcept(
                text="millennials",
                type="demographic",
                confidence=0.9,
                synonyms=["gen y"],
                related_terms=["young adults"],
                modifiers=[]
            ),
            QueryConcept(
                text="high income",
                type="financial",
                confidence=0.9,
                synonyms=["affluent", "wealthy"],
                related_terms=["rich"],
                modifiers=["high"]
            )
        ]
        
        # Calculate score
        base_score = 0.5
        new_score = self.scorer.calculate_concept_aware_score(
            base_score, var, concepts, {}
        )
        
        # Should have significant boost for matching 3 concepts
        assert new_score > base_score * 1.4  # At least 40% boost
    
    def test_important_concept_penalty(self):
        """Test penalty for missing important concepts"""
        # Variable that only matches one of two important concepts
        var = EnhancedVariable(
            code="HIGH_INC",
            description="High income households",
            category="Financial",
            theme="Income",
            product="",
            domain="financial"
        )
        
        # Important concepts (demographic and financial)
        concepts = [
            QueryConcept(
                text="millennials",
                type="demographic",  # Important type
                confidence=0.9,
                synonyms=[],
                related_terms=[],
                modifiers=[]
            ),
            QueryConcept(
                text="high income",
                type="financial",  # Important type
                confidence=0.9,
                synonyms=["affluent"],
                related_terms=[],
                modifiers=["high"]
            )
        ]
        
        # Calculate score
        base_score = 0.8
        new_score = self.scorer.calculate_concept_aware_score(
            base_score, var, concepts, {}
        )
        
        # Should have penalty for missing important demographic concept
        # But still boosted for matching financial concept
        assert new_score < base_score * 1.5  # Limited boost due to penalty
        assert new_score > base_score * 0.5   # Not too harsh penalty
    
    def test_synonym_matching(self):
        """Test concept matching via synonyms"""
        var = EnhancedVariable(
            code="AFFLUENT_FAM",
            description="Affluent families",
            category="Demographics",
            theme="Income",
            product="",
            domain="demographic"
        )
        
        # Concept with synonym that matches
        concept = QueryConcept(
            text="wealthy",
            type="financial",
            confidence=0.85,
            synonyms=["affluent", "rich", "prosperous"],
            related_terms=["high income"],
            modifiers=[]
        )
        
        # Should match via synonym
        assert self.scorer._variable_matches_concept(var, concept)
    
    def test_age_range_matching(self):
        """Test special handling for age-based demographics"""
        var = EnhancedVariable(
            code="AGE_25_34",
            description="Age 25-34 years",
            category="Demographics",
            theme="Age",
            product="",
            domain="demographic"
        )
        
        # Millennial concept
        concept = QueryConcept(
            text="millennial",
            type="demographic",
            confidence=0.9,
            synonyms=["gen y"],
            related_terms=[],
            modifiers=[]
        )
        
        # Should match based on age range
        assert self.scorer._variable_matches_concept(var, concept)


class TestEnhancedSemanticSearchV2:
    """Test suite for Enhanced Semantic Search V2"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create test variables
        self.test_variables = [
            {
                "code": "URBAN_MILL_HIGH_INC",
                "description": "Urban millennials with high disposable income",
                "category": "Demographics",
                "theme": "Income",
                "product": "Premium",
                "domain": "demographic"
            },
            {
                "code": "ECO_CONSCIOUS_FAM",
                "description": "Environmentally conscious families",
                "category": "Lifestyle",
                "theme": "Environment",
                "product": "Green",
                "domain": "behavioral"
            },
            {
                "code": "AGE_25_34_CITY",
                "description": "Age 25-34 living in major cities",
                "category": "Demographics",
                "theme": "Age",
                "product": "Urban",
                "domain": "demographic"
            }
        ]
        
        # Create search instance without OpenAI key (will use keyword only)
        self.search = EnhancedSemanticSearchV2(
            variables=self.test_variables,
            embeddings=None,
            openai_api_key=None
        )
    
    def test_basic_search_functionality(self):
        """Test that basic search still works"""
        results = self.search.search(
            query="urban millennials",
            top_k=10,
            use_semantic=False,
            use_keyword=True,
            use_advanced_processing=False
        )
        
        assert 'results' in results
        assert len(results['results']) > 0
        
        # Should find the urban millennial variable
        found_codes = [r['code'] for r in results['results']]
        assert 'URBAN_MILL_HIGH_INC' in found_codes
    
    @patch('activation_manager.core.enhanced_semantic_search_v2.AdvancedQueryProcessor')
    def test_advanced_processing_integration(self, mock_processor_class):
        """Test integration with advanced query processor"""
        # Mock the processor
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        # Mock the expansion response
        mock_processor.expand_query_semantically.return_value = {
            'expanded_terms': ['urban', 'millennials', 'city', 'young', 'adults'],
            'concepts': [
                {
                    'text': 'urban',
                    'type': 'geographic',
                    'confidence': 0.85,
                    'synonyms': ['city', 'metropolitan'],
                    'related_terms': ['downtown'],
                    'modifiers': []
                },
                {
                    'text': 'millennials',
                    'type': 'demographic',
                    'confidence': 0.9,
                    'synonyms': ['gen y'],
                    'related_terms': ['young adults'],
                    'modifiers': []
                }
            ],
            'query_interpretation': 'Looking for millennials in urban areas',
            'relationships': []
        }
        
        # Create new search instance to use mocked processor
        search = EnhancedSemanticSearchV2(
            variables=self.test_variables,
            embeddings=None,
            openai_api_key=None
        )
        
        # Perform search with advanced processing
        results = search.search(
            query="urban millennials",
            top_k=10,
            use_semantic=False,
            use_keyword=True,
            use_advanced_processing=True
        )
        
        # Should have called the processor
        mock_processor.expand_query_semantically.assert_called_once()
        
        # Should have advanced context in results
        assert 'advanced_context' in results
        assert 'query_interpretation' in results
    
    def test_concept_suggestions(self):
        """Test concept-based variable suggestions"""
        # This should work even without advanced processing mocked
        suggestions = self.search.get_concept_suggestions(
            "environmentally conscious urban families"
        )
        
        assert 'by_concept' in suggestions
        assert 'combinations' in suggestions
        assert 'missing_concepts' in suggestions
    
    def test_result_enhancement(self):
        """Test that results are enhanced with concept information"""
        # Create a simple result to enhance
        test_results = [
            {
                'code': 'URBAN_MILL_HIGH_INC',
                'description': 'Urban millennials with high disposable income',
                'score': 0.8
            }
        ]
        
        # Create test concepts
        concepts = [
            QueryConcept(
                text="urban",
                type="geographic",
                confidence=0.85,
                synonyms=["city"],
                related_terms=["metropolitan"],
                modifiers=[]
            ),
            QueryConcept(
                text="millennials",
                type="demographic",
                confidence=0.9,
                synonyms=["gen y"],
                related_terms=["young adults"],
                modifiers=[]
            )
        ]
        
        # Enhance results
        enhanced = self.search._enhance_results_with_concepts(
            test_results,
            concepts,
            {'query_interpretation': 'test'}
        )
        
        # Check enhancements
        assert len(enhanced) == 1
        result = enhanced[0]
        
        assert 'matched_concepts' in result
        assert 'concept_coverage' in result
        assert 'coverage_score' in result
        assert 'relevance_explanation' in result
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        results = self.search.search(
            query="",
            top_k=10,
            use_advanced_processing=True
        )
        
        assert 'results' in results
        assert isinstance(results['results'], list)
    
    def test_factory_function(self):
        """Test the factory function for creating search instances"""
        search = create_enhanced_search_v2(
            variables=self.test_variables,
            embeddings=None,
            openai_api_key=None
        )
        
        assert isinstance(search, EnhancedSemanticSearchV2)
        assert len(search.variables) == len(self.test_variables)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])