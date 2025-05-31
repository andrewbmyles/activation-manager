"""
Unit tests for Enhanced Semantic Search
Tests the comprehensive semantic search implementation with domain-specific features
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import json

from activation_manager.core.enhanced_semantic_search import (
    EnhancedVariable, QueryProcessor, HybridScorer, EnhancedSemanticSearch,
    SearchConfig, DOMAIN_CONFIGS
)


class TestEnhancedVariable(unittest.TestCase):
    """Test the EnhancedVariable class"""
    
    def setUp(self):
        """Create sample variable data"""
        self.sample_var = {
            'VarId': 'VIOPCAR_T',
            'Description': 'Total Passenger Cars - Age 25 to 34',
            'Category': 'Vehicle Ownership',
            'Theme': 'Behavioural',
            'ProductName': 'AutoView TVIO',
            'Context': 'Total Industry',
            'Consumption Flag': 'Incidence',
            'SortOrder': 1,
            'Product Vintage': '2022'
        }
    
    def test_initialization(self):
        """Test EnhancedVariable initialization"""
        var = EnhancedVariable(self.sample_var)
        
        self.assertEqual(var.code, 'VIOPCAR_T')
        self.assertEqual(var.description, 'Total Passenger Cars - Age 25 to 34')
        self.assertEqual(var.theme, 'Behavioural')
        self.assertEqual(var.domain, 'automotive')
    
    def test_prefix_extraction(self):
        """Test variable prefix extraction"""
        test_cases = [
            ('VIOPCAR_T', 'VIOPCAR'),  # Fixed: prefix is before underscore
            ('EXPVBASHHD', 'EXPVBASHHD'),
            ('FV_INDEX_01', 'FV'),
            ('123ABC', ''),
        ]
        
        for code, expected in test_cases:
            var_data = {**self.sample_var, 'VarId': code}
            var = EnhancedVariable(var_data)
            self.assertEqual(var.var_prefix, expected)
    
    def test_domain_identification(self):
        """Test domain mapping"""
        test_cases = [
            ('AutoView TVIO', 'automotive'),
            ('DemoStats', 'demographic'),
            ('Financial Vulnerability Index', 'financial'),
            ('CommunityHealth', 'health'),
            ('NewToCanada', 'immigration'),
            ('Unknown Product', 'general')
        ]
        
        for product, expected_domain in test_cases:
            var_data = {**self.sample_var, 'ProductName': product}
            var = EnhancedVariable(var_data)
            self.assertEqual(var.domain, expected_domain)
    
    def test_numeric_extraction(self):
        """Test numeric value extraction"""
        test_descriptions = [
            ('Age 25 to 34 years', {'age_range': [('25', '34')]}),
            ('Income $50k to $100k', {'dollar_amount': ['50', '100']}),
            ('Top 10%', {'percentage': ['10']}),
            ('Year 2022', {'year': ['2022']}),
        ]
        
        for desc, expected in test_descriptions:
            var_data = {**self.sample_var, 'Description': desc}
            var = EnhancedVariable(var_data)
            for key, value in expected.items():
                self.assertIn(key, var.numeric_values)
                self.assertEqual(var.numeric_values[key], value)
    
    def test_keyword_generation(self):
        """Test keyword generation"""
        var = EnhancedVariable(self.sample_var)
        keywords = var.enriched_keywords
        
        # Should include words from description
        self.assertIn('total', keywords)
        self.assertIn('passenger', keywords)
        self.assertIn('cars', keywords)
        
        # Should include processed code words
        self.assertIn('vehicles', keywords)
        # Check that some code-related words are present
        self.assertTrue(any('operation' in kw for kw in keywords))
    
    def test_embedding_text_creation(self):
        """Test embedding text generation"""
        var = EnhancedVariable(self.sample_var)
        embedding_text = var.embedding_text
        
        self.assertIn('theme:behavioural', embedding_text)
        self.assertIn('product:autoview tvio', embedding_text)
        self.assertIn('total passenger cars', embedding_text.lower())


class TestQueryProcessor(unittest.TestCase):
    """Test the QueryProcessor class"""
    
    def setUp(self):
        """Initialize query processor"""
        self.processor = QueryProcessor(DOMAIN_CONFIGS)
    
    def test_numeric_parsing(self):
        """Test numeric pattern extraction"""
        test_queries = [
            ('age 25 to 34', {'age_range': ('25', '34')}),
            ('income $50k to $100k', {'income_range': ('50', '100')}),
            ('year 2020 to 2022', {'year_range': ('2020', '2022')}),
            ('top 25%', {'percentage': ('25',)}),
            ('over 65', {'single_value': ('65',)}),
        ]
        
        for query, expected in test_queries:
            result = self.processor._parse_numeric(query)
            self.assertTrue(any(
                pattern_type in result['numeric_components'] 
                for pattern_type in expected
            ))
    
    def test_intent_classification(self):
        """Test query intent classification"""
        test_queries = [
            ('age families with children', 'demographic'),  # Must have 'age' for demographic
            ('car vehicle owners', 'automotive'),  # Must have 'car' or 'vehicle'
            ('income households spending', 'financial'),  # Must have 'income' or 'spending'
            ('health medical issues', 'health'),  # Must have 'health' or 'medical'
            ('immigrant newcomer resident', 'immigration'),  # Must have immigrant keywords
        ]
        
        for query, expected_intent in test_queries:
            intent = self.processor._classify_intent(query)
            self.assertEqual(intent['primary_intent'], expected_intent)
    
    def test_synonym_expansion(self):
        """Test synonym expansion"""
        # Test automotive synonyms
        expanded = self.processor._expand_synonyms('luxury car', ['automotive'])
        self.assertIn('vehicle', expanded)
        self.assertIn('premium', expanded)
        
        # Test demographic synonyms
        expanded = self.processor._expand_synonyms('senior citizens', ['demographic'])
        self.assertIn('elderly', expanded)
        self.assertIn('65+', expanded)
    
    def test_complete_processing(self):
        """Test complete query processing pipeline"""
        query = 'wealthy seniors age 65 to 75 with luxury cars'
        result = self.processor.process_query(query)
        
        self.assertEqual(result['original_query'], query)
        self.assertIn('age_range', result['numeric_components'])
        # Check that expanded terms contains the key words
        self.assertTrue(any(term in result['expanded_terms'] for term in ['wealthy', 'seniors', 'luxury', 'cars']))
        self.assertIsNotNone(result['intent'])


class TestHybridScorer(unittest.TestCase):
    """Test the HybridScorer class"""
    
    def setUp(self):
        """Initialize hybrid scorer"""
        self.config = SearchConfig()
        self.scorer = HybridScorer(self.config, DOMAIN_CONFIGS)
        
        # Create test variable
        self.test_var = EnhancedVariable({
            'VarId': 'VIOPCAR_LUX',
            'Description': 'Luxury Passenger Cars',
            'Theme': 'Behavioural',
            'ProductName': 'AutoView TVIO',
            'Category': 'Vehicles',
            'Context': 'Premium Segment',
            'Consumption Flag': 'Incidence'
        })
    
    def test_score_normalization(self):
        """Test score normalization through hybrid scoring"""
        # Create test context
        query_context = {
            'original_query': 'test',
            'numeric_components': {},
            'intent': {'primary_intent': 'general'}
        }
        
        # Test that hybrid scoring works with different score values
        score1 = self.scorer.calculate_hybrid_score(0, 0, self.test_var, query_context)
        score2 = self.scorer.calculate_hybrid_score(10, 1, self.test_var, query_context)
        
        # Higher input scores should result in higher hybrid scores
        self.assertGreater(score2, score1)
        self.assertGreaterEqual(score1, 0)  # All scores should be non-negative
    
    def test_exact_match_detection(self):
        """Test exact match detection"""
        # Exact code match
        self.assertTrue(self.scorer._check_exact_match('VIOPCAR_LUX', self.test_var))
        
        # Partial code match
        self.assertTrue(self.scorer._check_exact_match('viopcar', self.test_var))
        
        # Description match
        self.assertTrue(self.scorer._check_exact_match('luxury passenger', self.test_var))
        
        # No match
        self.assertFalse(self.scorer._check_exact_match('xyz', self.test_var))
    
    def test_hybrid_scoring(self):
        """Test hybrid score calculation"""
        query_context = {
            'original_query': 'luxury cars',
            'numeric_components': {},
            'intent': {'primary_intent': 'automotive'}
        }
        
        # Test with various score combinations
        score = self.scorer.calculate_hybrid_score(5.0, 0.8, self.test_var, query_context)
        self.assertGreater(score, 0)
        
        # Exact match should boost score
        query_context['original_query'] = 'VIOPCAR_LUX'
        score_with_exact = self.scorer.calculate_hybrid_score(5.0, 0.8, self.test_var, query_context)
        self.assertGreater(score_with_exact, score)


class TestEnhancedSemanticSearch(unittest.TestCase):
    """Test the main EnhancedSemanticSearch class"""
    
    def setUp(self):
        """Set up test data and mocks"""
        self.test_variables = [
            {
                'VarId': 'VAR001',
                'Description': 'Young Adults Age 18-24',
                'Theme': 'Demographic',
                'ProductName': 'DemoStats',
                'Category': 'Age',
                'Context': 'Census',
                'Consumption Flag': 'Incidence'
            },
            {
                'VarId': 'VAR002',
                'Description': 'High Income Over 150k',
                'Theme': 'Financial',
                'ProductName': 'Financial Index',
                'Category': 'Income',
                'Context': 'Tax Data',
                'Consumption Flag': 'Incidence'
            },
            {
                'VarId': 'VAR003',
                'Description': 'Luxury Vehicle Owners',
                'Theme': 'Behavioural',
                'ProductName': 'AutoView TVIO',
                'Category': 'Vehicles',
                'Context': 'Registration',
                'Consumption Flag': 'Incidence'
            }
        ]
    
    @patch('activation_manager.core.enhanced_semantic_search.faiss')
    def test_initialization(self, mock_faiss):
        """Test search engine initialization"""
        search = EnhancedSemanticSearch(self.test_variables)
        
        self.assertEqual(len(search.variables), 3)
        self.assertIsNotNone(search.query_processor)
        self.assertIsNotNone(search.hybrid_scorer)
        self.assertIsNotNone(search.tfidf_vectorizer)
    
    def test_keyword_search(self):
        """Test keyword-based search"""
        search = EnhancedSemanticSearch(self.test_variables)
        
        # Mock TF-IDF search
        with patch.object(search, '_keyword_search') as mock_search:
            mock_search.return_value = [
                (search.variables[0], 0.8, 'keyword'),
                (search.variables[1], 0.6, 'keyword')
            ]
            
            results = search.search('young adults', top_k=10, use_semantic=False)
            
            self.assertIn('results', results)
            self.assertGreater(len(results['results']), 0)
            mock_search.assert_called_once()
    
    def test_search_with_filters(self):
        """Test search with filters"""
        search = EnhancedSemanticSearch(self.test_variables)
        
        # Test theme filter
        with patch.object(search, '_keyword_search') as mock_search:
            mock_search.return_value = [
                (var, 0.7, 'keyword') for var in search.variables
            ]
            
            results = search.search(
                'test query',
                top_k=10,
                use_semantic=False,
                filters={'theme': 'Demographic'}
            )
            
            # Should only return demographic variables
            for result in results['results']:
                self.assertEqual(result['theme'], 'Demographic')
    
    def test_result_grouping(self):
        """Test result grouping functionality"""
        search = EnhancedSemanticSearch(self.test_variables)
        
        with patch.object(search, '_keyword_search') as mock_search:
            mock_search.return_value = [
                (var, 0.7, 'keyword') for var in search.variables
            ]
            
            results = search.search('all variables', top_k=10, use_semantic=False)
            
            self.assertIn('grouped', results)
            self.assertIn('by_theme', results['grouped'])
            self.assertIn('by_domain', results['grouped'])
            
            # Check grouping correctness
            themes = results['grouped']['by_theme']
            self.assertIn('Demographic', themes)
            self.assertIn('Financial', themes)
            self.assertEqual(len(themes['Demographic']), 1)
    
    @patch('openai.OpenAI')
    def test_semantic_search_integration(self, mock_openai):
        """Test semantic search with mocked OpenAI"""
        # Mock OpenAI embedding response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=np.random.rand(1536).tolist())]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create search with mocked embeddings
        mock_embeddings = np.random.rand(3, 1536).astype('float32')
        search = EnhancedSemanticSearch(
            self.test_variables,
            embeddings=mock_embeddings,
            openai_api_key='test-key'
        )
        
        # Should initialize with semantic search
        self.assertIsNotNone(search.openai_client)
        self.assertTrue(hasattr(search, 'faiss_index'))


class TestSearchConfig(unittest.TestCase):
    """Test SearchConfig settings"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SearchConfig()
        
        self.assertEqual(config.default_top_k, 50)
        self.assertEqual(config.hybrid_weight_semantic, 0.7)
        self.assertEqual(config.hybrid_weight_keyword, 0.3)
        self.assertEqual(config.exact_match_boost, 2.0)
        self.assertEqual(config.cache_size, 1000)


if __name__ == '__main__':
    unittest.main()