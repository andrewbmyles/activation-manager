// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// Helper function to build API URLs
export const getApiUrl = (endpoint: string) => {
  // If no API_BASE_URL is set, use relative URLs (for Vercel Functions)
  if (!API_BASE_URL) {
    return endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  }
  
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// API Endpoints
export const API_ENDPOINTS = {
  // Natural Language API
  nlStartSession: () => getApiUrl('api/nl/start_session'),
  nlProcess: () => getApiUrl('api/nl/process'),
  
  // Export API
  export: (audienceId: string) => getApiUrl(`api/export/${audienceId}`),
  
  // Audiences API
  audiences: () => getApiUrl('api/audiences'),
  
  // Health check
  health: () => getApiUrl('health'),
  
  // Enhanced Variable Picker API
  enhancedVariableSearch: () => getApiUrl('api/enhanced-variable-picker/search'),
  enhancedVariableStats: () => getApiUrl('api/enhanced-variable-picker/stats'),
};