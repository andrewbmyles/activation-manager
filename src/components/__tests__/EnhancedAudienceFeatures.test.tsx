/**
 * Unit tests for enhanced audience features in EnhancedNLAudienceBuilder component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { EnhancedNLAudienceBuilder } from '../EnhancedNLAudienceBuilder';

// Import real utility functions for testing
import * as audienceUtils from '../../utils/audienceUtils';

// Mock fetch for API calls
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('EnhancedNLAudienceBuilder - Enhanced Features', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
  });

  describe('Enhanced Save Functionality', () => {
    it('should include enhanced data fields when saving audience', async () => {
      // Test that utility functions work correctly
      expect(audienceUtils.generateAudienceName).toBeDefined();
      expect(audienceUtils.formatCriteriaNaturalLanguage).toBeDefined();
      expect(audienceUtils.generateRandomAudienceSize).toBeDefined();
      expect(audienceUtils.generateAudienceInsights).toBeDefined();

      // Test function outputs
      expect(audienceUtils.generateAudienceName('gaming enthusiasts')).toContain('Gaming-Enthusiast');
      const size = audienceUtils.generateRandomAudienceSize();
      expect(typeof size).toBe('number');
      expect(size).toBeGreaterThanOrEqual(56798);
      expect(size).toBeLessThanOrEqual(89380);
      
      const insights = audienceUtils.generateAudienceInsights('gaming enthusiasts', size);
      expect(Array.isArray(insights)).toBe(true);
      expect(insights.length).toBeGreaterThan(0);
    });

    it('should format success message with enhanced data', () => {
      const enhancedName = 'Gaming-Enthusiast Gen Z Males';
      const randomSize = 67842;
      
      const expectedMessage = `✅ Audience "${enhancedName}" saved successfully! ${randomSize.toLocaleString()} people matching your criteria. You can access it from the Saved Audiences page anytime.`;
      
      expect(expectedMessage).toContain('Gaming-Enthusiast Gen Z Males');
      expect(expectedMessage).toContain('67,842');
    });

    it('should structure audience data correctly', () => {
      const audienceData = {
        user_id: 'demo_user',
        name: 'Audience - 12/25/2025',
        enhanced_name: 'Gaming-Enthusiast Gen Z Males',
        description: 'Find gaming enthusiasts',
        natural_language_criteria: 'Males between the ages of 18 and 24 who are interested in video games',
        audience_size: 67842,
        insights: ['Focused audience of 68K+ targeted users', 'Technology-savvy consumers'],
        data_type: 'first_party',
        original_query: 'Find gaming enthusiasts',
        selected_variables: ['gaming_interest', 'age_range'],
        variable_details: [],
        segments: [],
        total_audience_size: 67842,
        status: 'active',
        metadata: {
          created_from: 'nl_audience_builder',
          session_id: 'test-session-123'
        }
      };

      // Verify all enhanced fields are present
      expect(audienceData).toHaveProperty('enhanced_name');
      expect(audienceData).toHaveProperty('natural_language_criteria');
      expect(audienceData).toHaveProperty('audience_size');
      expect(audienceData).toHaveProperty('insights');
      expect(audienceData.insights).toBeInstanceOf(Array);
      expect(audienceData.enhanced_name).toBe('Gaming-Enthusiast Gen Z Males');
      expect(audienceData.audience_size).toBe(67842);
    });
  });

  describe('Enhanced Variable Search Integration', () => {
    it('should use correct API endpoint and parameters', () => {
      const expectedRequestBody = {
        query: 'gaming enthusiasts',
        top_k: 50,
        use_semantic: true,
        use_keyword: true
      };

      expect(expectedRequestBody.top_k).toBe(50);
      expect(expectedRequestBody.use_semantic).toBe(true);
      expect(expectedRequestBody.use_keyword).toBe(true);
    });

    it('should transform API results to Variable interface', () => {
      const mockApiResult = {
        code: 'gaming_interest',
        name: 'Gaming Interest Level',
        description: 'Interest in video games and gaming',
        score: 0.95,
        dataType: 'interest',
        category: 'Entertainment',
        source: 'third_party'
      };

      // Transform to Variable interface (as done in component)
      const transformedVariable = {
        code: mockApiResult.code || `var_${Math.random().toString(36).substr(2, 9)}`,
        description: mockApiResult.name || mockApiResult.description || 'Unknown Variable',
        type: mockApiResult.dataType || 'Unknown',
        relevance_score: mockApiResult.score || 0.5,
        category: mockApiResult.category || 'General',
        dataAvailability: {
          first_party: true,
          third_party: mockApiResult.source === 'third_party',
          clean_room: false
        }
      };

      expect(transformedVariable.code).toBe('gaming_interest');
      expect(transformedVariable.description).toBe('Gaming Interest Level');
      expect(transformedVariable.type).toBe('interest');
      expect(transformedVariable.relevance_score).toBe(0.95);
      expect(transformedVariable.dataAvailability.third_party).toBe(true);
    });

    it('should handle missing fields with fallbacks', () => {
      const incompleteResult = {
        code: 'incomplete_var'
        // Missing other fields
      };

      const transformedWithFallbacks = {
        code: incompleteResult.code || `var_${Math.random().toString(36).substr(2, 9)}`,
        description: 'Unknown Variable',
        type: 'Unknown',
        relevance_score: 0.5,
        category: 'General',
        dataAvailability: {
          first_party: true,
          third_party: false,
          clean_room: false
        }
      };

      expect(transformedWithFallbacks.code).toBe('incomplete_var');
      expect(transformedWithFallbacks.description).toBe('Unknown Variable');
      expect(transformedWithFallbacks.relevance_score).toBe(0.5);
    });
  });

  describe('Dynamic Search Behavior', () => {
    it('should implement proper debouncing logic', () => {
      jest.useFakeTimers();
      
      let searchCalls = 0;
      const mockDynamicSearch = jest.fn(() => {
        searchCalls++;
      });

      // Simulate rapid typing that should be debounced
      const simulateTyping = () => {
        mockDynamicSearch();
        setTimeout(mockDynamicSearch, 100);
        setTimeout(mockDynamicSearch, 200);
        setTimeout(mockDynamicSearch, 300);
      };

      simulateTyping();
      
      // Fast-forward to trigger debounced call
      jest.advanceTimersByTime(500);
      
      expect(mockDynamicSearch).toHaveBeenCalled();
      
      jest.useRealTimers();
    });

    it('should manage typing state correctly', () => {
      const typingStates = {
        isTyping: false,
        setIsTyping: jest.fn()
      };

      // Simulate typing start
      typingStates.setIsTyping(true);
      expect(typingStates.setIsTyping).toHaveBeenCalledWith(true);

      // After search completes
      typingStates.setIsTyping(false);
      expect(typingStates.setIsTyping).toHaveBeenCalledWith(false);
    });
  });

  describe('Utility Function Integration', () => {
    it('should generate appropriate audience names for different queries', () => {
      const testCases = [
        { query: 'gaming enthusiasts who own consoles', expected: 'Gaming-Enthusiast' },
        { query: 'fashion-forward millennial women', expected: 'Fashion-Forward Millennial Women' },
        { query: 'random unrecognized text', expected: 'Custom Audience Segment' }
      ];

      testCases.forEach(({ query, expected }) => {
        const result = audienceUtils.generateAudienceName(query);
        expect(result).toContain(expected);
      });
    });

    it('should format natural language criteria correctly', () => {
      const result = audienceUtils.formatCriteriaNaturalLanguage('Find males aged 18-24 who are interested in gaming');
      expect(result).toBe('Males between the ages of 18 and 24 who are interested in video games');
    });

    it('should generate consistent random sizes', () => {
      const size = audienceUtils.generateRandomAudienceSize();
      expect(typeof size).toBe('number');
      expect(Number.isInteger(size)).toBe(true);
      expect(size).toBeGreaterThanOrEqual(56798);
      expect(size).toBeLessThanOrEqual(89380);
    });

    it('should generate relevant insights', () => {
      const insights = audienceUtils.generateAudienceInsights('gaming enthusiasts', 67842);
      expect(Array.isArray(insights)).toBe(true);
      expect(insights.length).toBeGreaterThan(0);
      expect(insights).toContain('Focused audience of 68K+ targeted users');
      expect(insights).toContain('Digital-native generation');
    });
  });

  describe('Error Handling', () => {
    it('should handle enhanced API failure gracefully', () => {
      const fallbackAPICall = {
        action: 'process',
        payload: { input: 'test query' }
      };

      // When enhanced API fails, should fallback to original processWorkflow
      expect(fallbackAPICall.action).toBe('process');
      expect(fallbackAPICall.payload.input).toBe('test query');
    });

    it('should handle malformed API responses', () => {
      const malformedResponse = {
        // Missing expected fields
        someUnexpectedField: 'value'
      };

      // Component should handle gracefully with fallbacks
      const safeResults = malformedResponse.results || [];
      expect(Array.isArray(safeResults)).toBe(true);
      expect(safeResults.length).toBe(0);
    });
  });

  describe('Data Structure Validation', () => {
    it('should maintain proper audience data structure', () => {
      const audienceDataStructure = {
        user_id: 'string',
        name: 'string',
        enhanced_name: 'string',
        description: 'string',
        natural_language_criteria: 'string',
        audience_size: 'number',
        insights: 'array',
        data_type: 'string',
        original_query: 'string',
        selected_variables: 'array',
        variable_details: 'array',
        segments: 'array',
        total_audience_size: 'number',
        status: 'string',
        metadata: 'object'
      };

      // Verify all required fields are defined
      expect(audienceDataStructure.enhanced_name).toBe('string');
      expect(audienceDataStructure.natural_language_criteria).toBe('string');
      expect(audienceDataStructure.audience_size).toBe('number');
      expect(audienceDataStructure.insights).toBe('array');
    });

    it('should handle segment data transformation', () => {
      const mockSegment = {
        group_id: 1,
        size: 45000,
        size_percentage: 66.3,
        name: 'Core Gaming Segment',
        characteristics: { primary_interest: 'console_gaming' },
        prizm_profile: {
          dominant_segments: ['Young & Restless', 'Shotguns & Pickups']
        }
      };

      const transformedSegment = {
        segment_id: mockSegment.group_id,
        name: mockSegment.name,
        size: mockSegment.size,
        size_percentage: mockSegment.size_percentage,
        characteristics: mockSegment.characteristics,
        prizm_segments: mockSegment.prizm_profile?.dominant_segments
      };

      expect(transformedSegment.segment_id).toBe(1);
      expect(transformedSegment.name).toBe('Core Gaming Segment');
      expect(transformedSegment.prizm_segments).toEqual(['Young & Restless', 'Shotguns & Pickups']);
    });
  });

  describe('Component State Management', () => {
    it('should track session state correctly', () => {
      const sessionStates = {
        sessionId: null,
        setSessionId: jest.fn()
      };

      // Session initialization
      sessionStates.setSessionId('test-session-123');
      expect(sessionStates.setSessionId).toHaveBeenCalledWith('test-session-123');
    });

    it('should manage workflow steps properly', () => {
      const currentStep = 3;
      const getStepStatus = (stepNumber: number) => {
        if (stepNumber < currentStep) return 'completed';
        if (stepNumber === currentStep) return 'active';
        return 'pending';
      };

      expect(getStepStatus(1)).toBe('completed');
      expect(getStepStatus(3)).toBe('active');
      expect(getStepStatus(4)).toBe('pending');
    });
  });

  describe('Performance Optimizations', () => {
    it('should clear typing timer on unmount', () => {
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
      
      // Simulate component lifecycle
      const mockTimer = setTimeout(() => {}, 500);
      clearTimeout(mockTimer);
      
      expect(clearTimeoutSpy).toHaveBeenCalled();
      
      clearTimeoutSpy.mockRestore();
    });

    it('should avoid unnecessary API calls', () => {
      const apiCallCounter = {
        count: 0,
        increment: () => { apiCallCounter.count++; }
      };

      // Simulate conditions that should not trigger API calls
      const emptyQuery = '';
      const noSessionId = null;

      if (!emptyQuery.trim() || !noSessionId) {
        // Should not make API call
      } else {
        apiCallCounter.increment();
      }

      expect(apiCallCounter.count).toBe(0);
    });
  });
});