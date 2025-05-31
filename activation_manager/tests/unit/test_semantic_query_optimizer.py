"""
Unit tests for Semantic Query Optimizer
Tests query segmentation, optimization, and reformulation strategies
"""

import pytest
from activation_manager.core.semantic_query_optimizer import (
    SemanticQueryOptimizer, QuerySegment
)


class TestSemanticQueryOptimizer:
    """Test suite for Semantic Query Optimizer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.optimizer = SemanticQueryOptimizer()
    
    def test_basic_query_optimization(self):
        """Test optimization of a basic query"""
        query = "millennials with high income"
        result = self.optimizer.optimize_query(query)
        
        # Check structure
        assert 'original_query' in result
        assert 'segments' in result
        assert 'entities' in result
        assert 'modifiers' in result
        assert 'reformulations' in result
        assert 'strategies' in result
        assert 'variations' in result
        assert 'optimization_score' in result
        
        # Should identify segments
        assert len(result['segments']) > 0
        
        # Should extract entities
        assert len(result['entities']) > 0
        entity_types = [e.split(':')[0] for e in result['entities']]
        assert 'demographic' in entity_types
        assert 'financial' in entity_types
    
    def test_complex_query_segmentation(self):
        """Test segmentation of complex queries"""
        query = "Find environmentally conscious millennials with high disposable income in urban areas"
        result = self.optimizer.optimize_query(query)
        
        # Should identify multiple segments
        segments = result['segments']
        assert len(segments) >= 2
        
        # Check for different intent types
        intents = [s['intent'] for s in segments]
        assert 'filter' in intents  # "with high disposable income"
        
        # Check segment weights
        for segment in segments:
            assert 0 <= segment['weight'] <= 1.0
    
    def test_intent_detection(self):
        """Test detection of different query intents"""
        # Filter intent
        query = "users with high income"
        result = self.optimizer.optimize_query(query)
        assert any(s['intent'] == 'filter' for s in result['segments'])
        
        # Exclude intent
        query = "millennials not living in rural areas"
        result = self.optimizer.optimize_query(query)
        assert any(s['intent'] == 'exclude' for s in result['segments'])
        
        # Expand intent
        query = "products similar to organic food"
        result = self.optimizer.optimize_query(query)
        assert any(s['intent'] == 'expand' for s in result['segments'])
        
        # Combine intent
        query = "urban and suburban families"
        result = self.optimizer.optimize_query(query)
        assert any(s['intent'] == 'combine' for s in result['segments'])
    
    def test_entity_extraction(self):
        """Test extraction of different entity types"""
        query = "wealthy urban millennials interested in sustainability"
        result = self.optimizer.optimize_query(query)
        
        entities = result['entities']
        assert len(entities) >= 3
        
        # Check entity types
        entity_dict = {}
        for entity in entities:
            entity_type, entity_value = entity.split(':', 1)
            if entity_type not in entity_dict:
                entity_dict[entity_type] = []
            entity_dict[entity_type].append(entity_value)
        
        assert 'demographic' in entity_dict  # millennials
        assert 'financial' in entity_dict    # wealthy
        assert 'geographic' in entity_dict   # urban
        assert 'behavioral' in entity_dict   # interested
    
    def test_modifier_extraction(self):
        """Test extraction of query modifiers"""
        query = "very high income extremely urban areas"
        result = self.optimizer.optimize_query(query)
        
        modifiers = result['modifiers']
        assert len(modifiers) > 0
        
        # Check for intensity modifiers
        modifier_types = [m.split(':')[0] for m in modifiers]
        assert 'intensity' in modifier_types
    
    def test_query_reformulations(self):
        """Test generation of query reformulations"""
        query = "environmentally conscious high income urban millennials"
        result = self.optimizer.optimize_query(query)
        
        reformulations = result['reformulations']
        assert len(reformulations) > 0
        
        # Check reformulation strategies
        strategies_used = [r['strategy'] for r in reformulations]
        
        # Should have at least one reformulation
        assert len(strategies_used) > 0
        
        # Check that reformulations are different from original
        for reform in reformulations:
            assert reform['query'] != query
            assert 'description' in reform
    
    def test_search_strategies(self):
        """Test generation of search strategies"""
        # Multi-dimensional query
        query = "urban millennials with high income interested in green technology"
        result = self.optimizer.optimize_query(query)
        
        strategies = result['strategies']
        assert len(strategies) > 0
        
        # Should suggest multi-dimensional search
        strategy_names = [s['name'] for s in strategies]
        assert 'multi_dimensional_search' in strategy_names
        
        # Check strategy structure
        for strategy in strategies:
            assert 'name' in strategy
            assert 'description' in strategy
            assert 'approach' in strategy
    
    def test_query_variations(self):
        """Test generation of query variations"""
        query = "very wealthy suburban families with multiple children"
        result = self.optimizer.optimize_query(query)
        
        variations = result['variations']
        assert len(variations) > 1  # At least original + 1 variation
        
        # Original should be included
        assert query in variations
        
        # Should have simplified version (without modifiers)
        simplified_found = False
        for var in variations:
            if 'very' not in var and 'wealthy' in var:
                simplified_found = True
                break
        assert simplified_found
    
    def test_optimization_score(self):
        """Test calculation of optimization scores"""
        # Simple query - lower score
        simple_query = "income"
        simple_result = self.optimizer.optimize_query(simple_query)
        simple_score = simple_result['optimization_score']
        
        # Complex query - higher score
        complex_query = "environmentally conscious millennials with high disposable income excluding rural areas"
        complex_result = self.optimizer.optimize_query(complex_query)
        complex_score = complex_result['optimization_score']
        
        # Complex query should have higher optimization potential
        assert complex_score > simple_score
        assert 0 <= simple_score <= 1
        assert 0 <= complex_score <= 1
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        result = self.optimizer.optimize_query("")
        
        assert result['original_query'] == ""
        assert len(result['segments']) == 0
        assert result['optimization_score'] == 0.0
    
    def test_special_patterns(self):
        """Test handling of special query patterns"""
        # Exclusion pattern
        query = "all demographics except seniors"
        result = self.optimizer.optimize_query(query)
        
        # Should identify exclusion
        assert any(s['intent'] == 'exclude' for s in result['segments'])
        
        # Should include exclusion in strategies
        strategies = result['strategies']
        strategy_names = [s['name'] for s in strategies]
        assert 'exclusion_search' in strategy_names
    
    def test_synonym_expansion_reformulation(self):
        """Test synonym expansion in reformulations"""
        query = "environmentally conscious consumers"
        result = self.optimizer.optimize_query(query)
        
        # Find synonym expansion reformulation
        synonym_reform = None
        for reform in result['reformulations']:
            if reform['strategy'] == 'synonym_expansion':
                synonym_reform = reform
                break
        
        if synonym_reform:
            # Should include synonyms
            expanded = synonym_reform['query'].lower()
            assert any(term in expanded for term in ['aware', 'mindful', 'green'])
    
    def test_segment_priority_ordering(self):
        """Test that segments can be reordered by priority"""
        query = "similar to organic buyers with high income not in rural areas"
        result = self.optimizer.optimize_query(query)
        
        # Find restructure reformulation
        restructured = None
        for reform in result['reformulations']:
            if reform['strategy'] == 'restructure':
                restructured = reform
                break
        
        if restructured:
            # Should reorder segments logically
            assert restructured['query'] != query


if __name__ == "__main__":
    pytest.main([__file__, "-v"])