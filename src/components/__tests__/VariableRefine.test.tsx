import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { EnhancedNLAudienceBuilder } from '../EnhancedNLAudienceBuilder';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div data-testid="mock-router">{children}</div>,
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/', search: '', hash: '', state: null }),
  useParams: () => ({}),
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, whileTap, whileHover, initial, animate, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, whileTap, whileHover, initial, animate, ...props }: any) => <button {...props}>{children}</button>,
  },
}));

// Mock recharts to avoid rendering issues
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

// Mock the API module
jest.mock('../../config/api', () => ({
  API_ENDPOINTS: {
    nlweb: {
      startSession: jest.fn(),
      processWorkflow: jest.fn(),
      exportAudience: jest.fn()
    }
  }
}));

// Create a wrapper component with all necessary providers
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

describe('EnhancedNLAudienceBuilder - Refine Functionality', () => {
  let mockStartSession: any;
  let mockProcessWorkflow: any;
  
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup API mocks
    const { API_ENDPOINTS } = require('../../config/api');
    mockStartSession = API_ENDPOINTS.nlweb.startSession = jest.fn();
    mockProcessWorkflow = API_ENDPOINTS.nlweb.processWorkflow = jest.fn();
    
    // Mock successful session start
    mockStartSession.mockResolvedValue({ session_id: 'test-session-123' });
  });

  describe('Step 4 - Variable Refinement', () => {
    it('should enable input field during step 4', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Wait for session to initialize
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      // Select data type (step 1)
      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      // Enter initial query (step 2)
      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Find millennials interested in sustainability');
      
      // Mock the workflow response with variables
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { code: 'AGE_RANGE', description: 'Age Range', type: 'demographic', relevance_score: 0.9 },
          { code: 'ECO_CONSCIOUS', description: 'Eco Conscious', type: 'lifestyle', relevance_score: 0.85 }
        ],
        segments: []
      });

      // Submit the query
      const submitButton = screen.getByRole('button', { name: /send/i });
      fireEvent.click(submitButton);

      // Wait for step 4
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type to refine your search...')).toBeInTheDocument();
      });

      // Check that input is enabled in step 4
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      expect(refineInput).not.toBeDisabled();
    });

    it('should show refine button during step 4', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Wait for session
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      // Navigate to step 4
      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Test query');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [{ code: 'TEST_VAR', description: 'Test Variable', type: 'test', relevance_score: 0.8 }],
        segments: []
      });

      const submitButton = screen.getByRole('button', { name: /send/i });
      fireEvent.click(submitButton);

      // Wait for refine button to appear
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /refine/i })).toBeInTheDocument();
      });

      const refineButton = screen.getByRole('button', { name: /refine/i });
      expect(refineButton).toBeInTheDocument();
      expect(refineButton).toHaveClass('bg-purple-500');
    });

    it('should trigger dynamic search on typing with debounce', async () => {
      jest.useFakeTimers();
      
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Setup and navigate to step 4
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Initial query');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [{ code: 'VAR1', description: 'Variable 1', type: 'type1', relevance_score: 0.9 }],
        segments: []
      });

      const submitButton = screen.getByRole('button', { name: /send/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type to refine your search...')).toBeInTheDocument();
      });

      // Clear previous calls
      mockProcessWorkflow.mockClear();

      // Type in refine input
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      
      act(() => {
        fireEvent.change(refineInput, { target: { value: 'urban' } });
      });

      // Should not call immediately
      expect(mockProcessWorkflow).not.toHaveBeenCalled();

      // Fast-forward 500ms (debounce time)
      act(() => {
        jest.advanceTimersByTime(500);
      });

      // Now it should have been called
      await waitFor(() => {
        expect(mockProcessWorkflow).toHaveBeenCalledWith({
          action: 'process',
          payload: { input: 'urban' }
        });
      });

      jest.useRealTimers();
    });

    it('should show loading state while refining', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Navigate to step 4
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Test');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [{ code: 'VAR1', description: 'Variable 1', type: 'type1', relevance_score: 0.9 }],
        segments: []
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type to refine your search...')).toBeInTheDocument();
      });

      // Setup slow response for refine
      mockProcessWorkflow.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({
        variables: [{ code: 'VAR2', description: 'Variable 2', type: 'type2', relevance_score: 0.8 }]
      }), 1000)));

      // Type to trigger refine
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      fireEvent.change(refineInput, { target: { value: 'new search' } });

      // Click refine button
      const refineButton = screen.getByRole('button', { name: /refine/i });
      fireEvent.click(refineButton);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText('Refining search...')).toBeInTheDocument();
      });
    });

    it('should update variables list after refinement', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Navigate to step 4
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Initial search');
      
      // Initial variables
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { code: 'VAR1', description: 'Initial Variable 1', type: 'type1', relevance_score: 0.9 },
          { code: 'VAR2', description: 'Initial Variable 2', type: 'type2', relevance_score: 0.8 }
        ],
        segments: []
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByText('Initial Variable 1')).toBeInTheDocument();
        expect(screen.getByText('Initial Variable 2')).toBeInTheDocument();
      });

      // Refine with new search
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { code: 'VAR3', description: 'Refined Variable 1', type: 'type1', relevance_score: 0.95 },
          { code: 'VAR4', description: 'Refined Variable 2', type: 'type3', relevance_score: 0.85 }
        ]
      });

      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      await userEvent.clear(refineInput);
      await userEvent.type(refineInput, 'refined search');
      
      fireEvent.click(screen.getByRole('button', { name: /refine/i }));

      // Check that variables are updated
      await waitFor(() => {
        expect(screen.getByText('Refined Variable 1')).toBeInTheDocument();
        expect(screen.getByText('Refined Variable 2')).toBeInTheDocument();
      });

      // Original variables should be gone
      expect(screen.queryByText('Initial Variable 1')).not.toBeInTheDocument();
      expect(screen.queryByText('Initial Variable 2')).not.toBeInTheDocument();
    });

    it('should disable refine button when input is empty', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Navigate to step 4
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Test');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [{ code: 'VAR1', description: 'Variable 1', type: 'type1', relevance_score: 0.9 }],
        segments: []
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /refine/i })).toBeInTheDocument();
      });

      // Clear the input
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      await userEvent.clear(refineInput);

      // Refine button should be disabled
      const refineButton = screen.getByRole('button', { name: /refine/i });
      expect(refineButton).toBeDisabled();
    });

    it('should maintain selected variables during refinement', async () => {
      render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });
      
      // Navigate to step 4
      await waitFor(() => {
        expect(mockStartSession).toHaveBeenCalled();
      });

      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      const input = screen.getByPlaceholderText('Describe your target audience...');
      await userEvent.type(input, 'Test');
      
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { code: 'VAR1', description: 'Variable 1', type: 'type1', relevance_score: 0.9, id: 'VAR1' },
          { code: 'VAR2', description: 'Variable 2', type: 'type2', relevance_score: 0.8, id: 'VAR2' }
        ],
        segments: []
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByText('Variable 1')).toBeInTheDocument();
      });

      // Select first variable
      const checkbox1 = screen.getByRole('checkbox', { name: /variable 1/i });
      fireEvent.click(checkbox1);
      expect(checkbox1).toBeChecked();

      // Refine search
      mockProcessWorkflow.mockResolvedValue({
        variables: [
          { code: 'VAR1', description: 'Variable 1', type: 'type1', relevance_score: 0.95, id: 'VAR1' },
          { code: 'VAR3', description: 'Variable 3', type: 'type3', relevance_score: 0.9, id: 'VAR3' }
        ]
      });

      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      await userEvent.type(refineInput, ' refined');
      fireEvent.click(screen.getByRole('button', { name: /refine/i }));

      await waitFor(() => {
        expect(screen.getByText('Variable 3')).toBeInTheDocument();
      });

      // Check that VAR1 is still selected
      const updatedCheckbox1 = screen.getByRole('checkbox', { name: /variable 1/i });
      expect(updatedCheckbox1).toBeChecked();
    });
  });
});