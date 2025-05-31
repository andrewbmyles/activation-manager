import { getApiUrl, API_ENDPOINTS } from '../api';

describe('API Configuration', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
    // Clear API URL for each test
    delete process.env.REACT_APP_API_URL;
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe('getApiUrl', () => {
    test('returns relative URL when no API_BASE_URL is set', () => {
      expect(getApiUrl('/api/test')).toBe('/api/test');
      expect(getApiUrl('api/test')).toBe('/api/test');
    });

    test('returns full URL when API_BASE_URL is set', () => {
      process.env.REACT_APP_API_URL = 'https://api.tobermory.ai';
      expect(getApiUrl('/api/test')).toBe('https://api.tobermory.ai/api/test');
      expect(getApiUrl('api/test')).toBe('https://api.tobermory.ai/api/test');
    });

    test('handles custom API URL from environment variable', () => {
      process.env.REACT_APP_API_URL = 'https://custom-api.example.com';
      expect(getApiUrl('/api/test')).toBe('https://custom-api.example.com/api/test');
    });
  });

  describe('API_ENDPOINTS', () => {
    test('contains all required endpoints', () => {
      const requiredEndpoints = [
        'health',
        'audiences',
        'export',
        'nlProcess',
        'nlStartSession'
      ];

      requiredEndpoints.forEach(endpoint => {
        expect(API_ENDPOINTS).toHaveProperty(endpoint);
      });
    });

    test('endpoints are functions that return correct paths', () => {
      expect(API_ENDPOINTS.health()).toBe('/health');
      expect(API_ENDPOINTS.audiences()).toBe('/api/audiences');
      expect(API_ENDPOINTS.nlProcess()).toBe('/api/nl/process');
      expect(API_ENDPOINTS.nlStartSession()).toBe('/api/nl/start_session');
    });

    test('export is a function that returns correct path', () => {
      const audienceId = 'test-audience-123';
      expect(API_ENDPOINTS.export(audienceId)).toBe('/api/export/test-audience-123');
    });

    test('export handles special characters in ID', () => {
      const audienceId = 'test-audience-@#$';
      expect(API_ENDPOINTS.export(audienceId)).toBe('/api/export/test-audience-@#$');
    });
  });

  describe('API Integration', () => {
    test('endpoints work with relative URLs', () => {
      delete process.env.REACT_APP_API_URL;
      expect(API_ENDPOINTS.health()).toBe('/health');
      expect(API_ENDPOINTS.nlProcess()).toBe('/api/nl/process');
    });

    test('endpoints work with absolute base URL', () => {
      process.env.REACT_APP_API_URL = 'https://api.tobermory.ai';
      expect(API_ENDPOINTS.health()).toBe('https://api.tobermory.ai/health');
      expect(API_ENDPOINTS.nlProcess()).toBe('https://api.tobermory.ai/api/nl/process');
    });
  });
});