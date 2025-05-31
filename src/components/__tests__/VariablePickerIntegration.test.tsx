import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { EnhancedNLAudienceBuilder } from '../EnhancedNLAudienceBuilder';
import '@testing-library/jest-dom';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div data-testid="mock-router">{children}</div>,
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/', search: '', hash: '', state: null }),
  useParams: () => ({}),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, whileTap, whileHover, initial, animate, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, whileTap, whileHover, initial, animate, ...props }: any) => <button {...props}>{children}</button>,
  },
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Send: () => <span>Send</span>,
  Loader2: ({ className }: any) => <span className={className}>Loading</span>,
  Brain: ({ className }: any) => <span className={className} data-testid="brain-icon">Brain</span>,
  Sparkles: () => <span>Sparkles</span>,
  Database: () => <span>Database</span>,
  Cloud: () => <span>Cloud</span>,
  Shield: () => <span>Shield</span>,
  Info: () => <span>Info</span>,
  BarChart3: () => <span>BarChart3</span>,
  Users: () => <span>Users</span>,
  CheckCircle: () => <span>CheckCircle</span>,
  TrendingUp: () => <span>TrendingUp</span>,
  Download: () => <span>Download</span>,
  Check: () => <span>Check</span>,
}));

// Mock recharts
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  BarChart: () => <div>BarChart</div>,
  Bar: () => <div>Bar</div>,
  PieChart: () => <div>PieChart</div>,
  Pie: () => <div>Pie</div>,
  Cell: () => <div>Cell</div>,
  ScatterChart: () => <div>ScatterChart</div>,
  Scatter: () => <div>Scatter</div>,
  XAxis: () => <div>XAxis</div>,
  YAxis: () => <div>YAxis</div>,
  CartesianGrid: () => <div>CartesianGrid</div>,
  Tooltip: () => <div>Tooltip</div>,
}));

// Mock API
jest.mock('../../config/api', () => ({
  API_ENDPOINTS: {
    nlweb: {
      startSession: jest.fn(),
      processWorkflow: jest.fn(),
      exportAudience: jest.fn()
    }
  }
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Variable Picker Integration Tests', () => {
  let mockStartSession: any;
  let mockProcessWorkflow: any;
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    const { API_ENDPOINTS } = require('../../config/api');
    mockStartSession = API_ENDPOINTS.nlweb.startSession = jest.fn();
    mockProcessWorkflow = API_ENDPOINTS.nlweb.processWorkflow = jest.fn();
    
    mockStartSession.mockResolvedValue({ session_id: 'test-session-123' });
  });

  describe('Complete Variable Selection Workflow', () => {
    it('should complete full workflow from data type selection to variable refinement', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Wait for session initialization
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      // Step 1: Select data type
      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);
      
      // Verify moved to step 2
      expect(screen.getByPlaceholderText('Describe your target audience...')).toBeInTheDocument();

      // Step 2: Enter audience description
      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Find environmentally conscious millennials in urban areas');
      
      // Mock API response with variables
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { 
            code: 'AGE_MILLENIAL', 
            description: 'Millennials (Age 25-40)', 
            type: 'demographic', 
            relevance_score: 0.95,
            id: 'AGE_MILLENIAL'
          },
          { 
            code: 'ECO_CONSCIOUS', 
            description: 'Environmental Consciousness Index', 
            type: 'lifestyle', 
            relevance_score: 0.92,
            id: 'ECO_CONSCIOUS'
          },
          { 
            code: 'URBAN_DENSITY', 
            description: 'Urban Area Residents', 
            type: 'geographic', 
            relevance_score: 0.88,
            id: 'URBAN_DENSITY'
          }
        ],
        segments: []
      });

      // Submit query
      const submitButton = screen.getByRole('button', { name: /send/i });
      fireEvent.click(submitButton);

      // Wait for step 4 (variable selection)
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type to refine your search...')).toBeInTheDocument();
      });

      // Verify variables are displayed with semantic styling
      expect(screen.getByText('Millennials (Age 25-40)')).toBeInTheDocument();
      expect(screen.getByText('Environmental Consciousness Index')).toBeInTheDocument();
      expect(screen.getByText('Urban Area Residents')).toBeInTheDocument();
      
      // Check semantic labels
      const semanticLabels = screen.getAllByText('Semantic');
      expect(semanticLabels).toHaveLength(3);
      
      // Check brain icons
      const brainIcons = screen.getAllByTestId('brain-icon');
      expect(brainIcons).toHaveLength(3);
      
      // Check scores
      expect(screen.getByText('Score: 0.95')).toBeInTheDocument();
      expect(screen.getByText('Score: 0.92')).toBeInTheDocument();
      expect(screen.getByText('Score: 0.88')).toBeInTheDocument();

      // Verify refine button is present
      const refineButton = screen.getByRole('button', { name: /refine/i });
      expect(refineButton).toBeInTheDocument();
      
      // Test refinement
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      await userEvent.clear(refineInput);
      await userEvent.type(refineInput, 'focus on sustainability');
      
      // Mock refined results
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { 
            code: 'SUSTAIN_INDEX', 
            description: 'Sustainability Lifestyle Index', 
            type: 'lifestyle', 
            relevance_score: 0.98,
            id: 'SUSTAIN_INDEX'
          },
          { 
            code: 'GREEN_PURCHASE', 
            description: 'Green Product Purchase Behavior', 
            type: 'behavioral', 
            relevance_score: 0.94,
            id: 'GREEN_PURCHASE'
          }
        ]
      });
      
      fireEvent.click(refineButton);
      
      // Wait for refined results
      await waitFor(() => {
        expect(screen.getByText('Sustainability Lifestyle Index')).toBeInTheDocument();
        expect(screen.getByText('Green Product Purchase Behavior')).toBeInTheDocument();
      });
      
      // Original variables should be replaced
      expect(screen.queryByText('Millennials (Age 25-40)')).not.toBeInTheDocument();
    });

    it('should handle tooltip interactions correctly', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Quick setup to get to variable display
      await waitFor(() => expect(mockStartSession).toHaveBeenCalled());
      
      fireEvent.click(screen.getByText('First Party Data'));
      await userEvent.type(screen.getByPlaceholderText('Describe your target audience...'), 'test');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [{ 
          code: 'TEST', 
          description: 'Test Variable', 
          type: 'test', 
          relevance_score: 0.85,
          id: 'TEST'
        }]
      });
      
      fireEvent.click(screen.getByRole('button', { name: /send/i }));
      
      await waitFor(() => {
        expect(screen.getByText('Score: 0.85')).toBeInTheDocument();
      });
      
      // Check tooltip content exists (always rendered, just hidden)
      expect(screen.getByText('Relevance Score: 0.85')).toBeInTheDocument();
      expect(screen.getByText('This AI-generated score (0-1) indicates how closely this variable matches your audience description.')).toBeInTheDocument();
      expect(screen.getByText('Higher scores = stronger semantic match')).toBeInTheDocument();
    });

    it('should maintain variable selections during refinement', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Setup
      await waitFor(() => expect(mockStartSession).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));
      await userEvent.type(screen.getByPlaceholderText('Describe your target audience...'), 'test');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { code: 'VAR1', description: 'Variable 1', type: 'type1', relevance_score: 0.9, id: 'VAR1' },
          { code: 'VAR2', description: 'Variable 2', type: 'type2', relevance_score: 0.8, id: 'VAR2' }
        ]
      });
      
      fireEvent.click(screen.getByRole('button', { name: /send/i }));
      
      await waitFor(() => {
        expect(screen.getByText('Variable 1')).toBeInTheDocument();
      });
      
      // Select first variable
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);
      
      // Refine search
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      await userEvent.type(refineInput, ' refined');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { code: 'VAR1', description: 'Variable 1', type: 'type1', relevance_score: 0.95, id: 'VAR1' },
          { code: 'VAR3', description: 'Variable 3', type: 'type3', relevance_score: 0.85, id: 'VAR3' }
        ]
      });
      
      fireEvent.click(screen.getByRole('button', { name: /refine/i }));
      
      await waitFor(() => {
        expect(screen.getByText('Variable 3')).toBeInTheDocument();
      });
      
      // First variable should still be selected
      const updatedCheckboxes = screen.getAllByRole('checkbox');
      expect(updatedCheckboxes[0]).toBeChecked();
    });

    it('should show appropriate loading states during refinement', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Setup to reach refinement stage
      await waitFor(() => expect(mockStartSession).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));
      await userEvent.type(screen.getByPlaceholderText('Describe your target audience...'), 'test');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [{ code: 'TEST', description: 'Test', type: 'test', relevance_score: 0.8, id: 'TEST' }]
      });
      
      fireEvent.click(screen.getByRole('button', { name: /send/i }));
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type to refine your search...')).toBeInTheDocument();
      });
      
      // Set up slow response
      mockProcessWorkflow.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          variables: [{ code: 'NEW', description: 'New Variable', type: 'test', relevance_score: 0.9, id: 'NEW' }]
        }), 100))
      );
      
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      await userEvent.type(refineInput, 'new search');
      
      fireEvent.click(screen.getByRole('button', { name: /refine/i }));
      
      // Should show loading state
      expect(screen.getByText('Refining search...')).toBeInTheDocument();
      
      // Wait for completion
      await waitFor(() => {
        expect(screen.getByText('New Variable')).toBeInTheDocument();
      });
    });
  });
});