"""
Unit tests for Advanced Query Processor
Tests concept extraction, relationship identification, and query expansion
"""

import pytest
from activation_manager.core.advanced_query_processor import (
    AdvancedQueryProcessor, QueryConcept, ConceptRelationship
)


class TestAdvancedQueryProcessor:
    """Test suite for Advanced Query Processor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = AdvancedQueryProcessor()
    
    def test_basic_concept_extraction(self):
        """Test extraction of basic concepts from simple queries"""
        query = "millennials with high income"
        context = self.processor.expand_query_semantically(query)
        
        # Check that concepts were extracted
        assert len(context['concepts']) >= 2
        
        # Check for expected concept types
        concept_types = [c['type'] for c in context['concepts']]
        assert 'demographic' in concept_types
        assert 'financial' in concept_types
        
        # Check for specific concepts
        concept_texts = [c['text'] for c in context['concepts']]
        assert 'millennials' in concept_texts
        assert 'high income' in concept_texts
    
    def test_complex_query_extraction(self):
        """Test extraction from complex multi-faceted query"""
        query = "Find environmentally conscious millennials with high disposable income in urban areas"
        context = self.processor.expand_query_semantically(query)
        
        # Should extract multiple concepts
        assert len(context['concepts']) >= 4
        
        # Check for all expected concept types
        concept_types = [c['type'] for c in context['concepts']]
        assert 'demographic' in concept_types
        assert 'financial' in concept_types
        assert 'behavioral' in concept_types
        assert 'geographic' in concept_types
        
        # Check confidence scores
        for concept in context['concepts']:
            assert 0 < concept['confidence'] <= 1.0
    
    def test_synonym_extraction(self):
        """Test synonym generation for concepts"""
        query = "wealthy families"
        context = self.processor.expand_query_semantically(query)
        
        # Find the wealthy concept
        wealthy_concept = None
        for concept in context['concepts']:
            if concept['text'] == 'wealthy':
                wealthy_concept = concept
                break
        
        assert wealthy_concept is not None
        assert len(wealthy_concept['synonyms']) > 0
        
        # Check for expected synonyms
        expected_synonyms = ['affluent', 'rich', 'prosperous']
        assert any(syn in wealthy_concept['synonyms'] for syn in expected_synonyms)
    
    def test_modifier_extraction(self):
        """Test extraction of concept modifiers"""
        query = "very high income young families"
        context = self.processor.expand_query_semantically(query)
        
        # Find income concept
        income_concept = None
        for concept in context['concepts']:
            if 'income' in concept['text']:
                income_concept = concept
                break
        
        assert income_concept is not None
        assert 'very' in income_concept['modifiers'] or 'high' in income_concept['modifiers']
    
    def test_concept_relationships(self):
        """Test identification of relationships between concepts"""
        query = "millennials with children interested in sustainable products"
        context = self.processor.expand_query_semantically(query)
        
        # Should identify relationships
        assert 'relationships' in context
        assert len(context['relationships']) > 0
        
        # Check relationship types
        rel_types = [r['type'] for r in context['relationships']]
        assert any(t in ['has', 'interested_in', 'with'] for t in rel_types)
    
    def test_query_interpretation(self):
        """Test overall query interpretation"""
        query = "urban professionals without children who travel frequently"
        context = self.processor.expand_query_semantically(query)
        
        # Should have an interpretation
        assert 'query_interpretation' in context
        assert isinstance(context['query_interpretation'], str)
        assert len(context['query_interpretation']) > 0
    
    def test_variable_pattern_generation(self):
        """Test generation of variable patterns"""
        query = "tech-savvy seniors"
        context = self.processor.expand_query_semantically(query)
        
        # Should suggest variable patterns
        assert 'variable_patterns' in context
        assert len(context['variable_patterns']) > 0
        
        # Patterns should relate to the query
        patterns_text = ' '.join(context['variable_patterns']).lower()
        assert 'tech' in patterns_text or 'senior' in patterns_text or 'age' in patterns_text
    
    def test_empty_query_handling(self):
        """Test handling of empty or very short queries"""
        # Empty query
        context = self.processor.expand_query_semantically("")
        assert context['concepts'] == []
        
        # Single word query
        context = self.processor.expand_query_semantically("income")
        assert len(context['concepts']) >= 1
    
    def test_special_character_handling(self):
        """Test handling of queries with special characters"""
        query = "income $100k+ & urban"
        context = self.processor.expand_query_semantically(query)
        
        # Should still extract concepts
        assert len(context['concepts']) >= 2
        concept_types = [c['type'] for c in context['concepts']]
        assert 'financial' in concept_types
        assert 'geographic' in concept_types
    
    def test_concept_confidence_scores(self):
        """Test that confidence scores are reasonable"""
        query = "probably millennials maybe with high income"
        context = self.processor.expand_query_semantically(query)
        
        # Concepts with uncertainty modifiers should have lower confidence
        for concept in context['concepts']:
            if concept['text'] == 'millennials':
                # Should have lower confidence due to "probably"
                assert concept['confidence'] < 0.9
    
    def test_expanded_terms_generation(self):
        """Test generation of expanded search terms"""
        query = "eco-friendly millennials"
        context = self.processor.expand_query_semantically(query)
        
        # Should have expanded terms
        assert 'expanded_terms' in context
        assert len(context['expanded_terms']) > 2  # More than just the original terms
        
        # Should include original terms
        expanded_lower = [t.lower() for t in context['expanded_terms']]
        assert 'eco-friendly' in expanded_lower or 'eco' in expanded_lower
        assert 'millennials' in expanded_lower
    
    def test_domain_specific_mappings(self):
        """Test domain-specific concept mappings"""
        query = "gen z with student debt"
        context = self.processor.expand_query_semantically(query)
        
        # Should recognize gen z as demographic
        gen_z_found = False
        for concept in context['concepts']:
            if concept['text'].lower() == 'gen z':
                assert concept['type'] == 'demographic'
                gen_z_found = True
                # Should have metadata about age ranges
                assert 'metadata' in concept or 'attributes' in concept
        
        assert gen_z_found, "Gen Z concept not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])