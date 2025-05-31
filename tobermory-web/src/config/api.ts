// API configuration for Tobermory AI platform

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

export const API_ENDPOINTS = {
  // Natural Language Processing
  nlStartSession: () => `${API_BASE_URL}/api/start_session`,
  nlProcess: () => `${API_BASE_URL}/api/nl/process`,
  
  // Audience Management
  createAudience: () => `${API_BASE_URL}/api/audiences`,
  getAudience: (id: string) => `${API_BASE_URL}/api/audiences/${id}`,
  export: (audienceId: string) => `${API_BASE_URL}/api/export/${audienceId}`,
  
  // Variable Picker
  variablePicker: () => `${API_BASE_URL}/api/variable_picker/search`,
  
  // Embeddings
  embeddingsStatus: () => `${API_BASE_URL}/api/embeddings/status`,
  
  // Distribution
  distribute: (audienceId: string) => `${API_BASE_URL}/api/audiences/${audienceId}/distribute`,
  distributionStatus: (audienceId: string, distributionId: string) => 
    `${API_BASE_URL}/api/audiences/${audienceId}/distributions/${distributionId}`,
  
  // Platform Integration
  platforms: () => `${API_BASE_URL}/api/platforms`,
  platformConnect: (platformId: string) => `${API_BASE_URL}/api/platforms/${platformId}/connect`,
  platformStatus: (platformId: string) => `${API_BASE_URL}/api/platforms/${platformId}/status`,
  
  // Health Check
  health: () => `${API_BASE_URL}/health`,
};