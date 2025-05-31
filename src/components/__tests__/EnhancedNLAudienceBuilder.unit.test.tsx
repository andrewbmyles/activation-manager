import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Create a minimal test version of the component for unit testing
const mockNavigate = jest.fn();

// Mock all external dependencies
jest.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  BrowserRouter: ({ children }: any) => <div>{children}</div>
}));

jest.mock('@tanstack/react-query', () => ({
  useMutation: () => ({
    mutate: jest.fn(),
    mutateAsync: jest.fn(),
    isPending: false,
    isError: false,
    failureCount: 0
  }),
  QueryClient: jest.fn(),
  QueryClientProvider: ({ children }: any) => <div>{children}</div>
}));

jest.mock('lucide-react', () => ({
  Send: () => <div>Send Icon</div>,
  Loader2: () => <div>Loading</div>,
  Check: () => <div>Check</div>,
  Download: () => <div>Download</div>,
  Database: () => <div>Database</div>,
  Shield: () => <div>Shield</div>,
  Cloud: () => <div>Cloud</div>,
  Info: () => <div>Info</div>,
  BarChart3: () => <div>BarChart3</div>,
  Users: () => <div>Users</div>,
  Sparkles: () => <div>Sparkles</div>,
  CheckCircle: () => <div>CheckCircle</div>,
  TrendingUp: () => <div>TrendingUp</div>,
  Brain: () => <div>Brain</div>,
}));

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
}));

jest.mock('recharts', () => ({
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
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
}));

// Import after mocks
import { EnhancedNLAudienceBuilder } from '../EnhancedNLAudienceBuilder';

// Mock fetch globally
global.fetch = jest.fn();

describe('EnhancedNLAudienceBuilder - Unit Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('Component Title', () => {
    it('should display "Natural Language Multi-Variate Audience Builder" as the title', () => {
      render(<EnhancedNLAudienceBuilder />);
      expect(screen.getByText('Natural Language Multi-Variate Audience Builder')).toBeInTheDocument();
    });

    it('should display the correct subtitle', () => {
      render(<EnhancedNLAudienceBuilder />);
      expect(screen.getByText('Build sophisticated audiences with AI-powered segmentation')).toBeInTheDocument();
    });
  });

  describe('Responsive UI Classes', () => {
    it('should have responsive height class on main container', () => {
      const { container } = render(<EnhancedNLAudienceBuilder />);
      const mainContainer = container.querySelector('.flex.h-\\[calc\\(100vh-16rem\\)\\].min-h-\\[600px\\]');
      expect(mainContainer).toBeInTheDocument();
    });

    it('should have responsive width classes on workflow sidebar', () => {
      const { container } = render(<EnhancedNLAudienceBuilder />);
      const sidebar = container.querySelector('.w-64.lg\\:w-80.xl\\:w-96');
      expect(sidebar).toBeInTheDocument();
    });

    it('should have responsive padding on chat area', () => {
      const { container } = render(<EnhancedNLAudienceBuilder />);
      const chatArea = container.querySelector('.flex-1.overflow-y-auto.p-6.lg\\:p-8.xl\\:p-10');
      expect(chatArea).toBeInTheDocument();
    });

    it('should have responsive padding on input area', () => {
      const { container } = render(<EnhancedNLAudienceBuilder />);
      const inputArea = container.querySelector('.border-t.border-gray-200.p-4.lg\\:p-6');
      expect(inputArea).toBeInTheDocument();
    });
  });

  describe('Workflow Steps', () => {
    it('should display all 7 workflow steps', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      expect(screen.getByText('Select Data Type')).toBeInTheDocument();
      expect(screen.getByText('Describe Audience')).toBeInTheDocument();
      expect(screen.getByText('Variable Selection')).toBeInTheDocument();
      expect(screen.getByText('Confirm Variables')).toBeInTheDocument();
      expect(screen.getByText('Create Segments')).toBeInTheDocument();
      expect(screen.getByText('Review Results')).toBeInTheDocument();
      expect(screen.getByText('Distribution')).toBeInTheDocument();
    });

    it('should start with step 1 active', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      // First step should have active state (blue background with animation)
      const firstStep = screen.getByText('1');
      const stepContainer = firstStep.closest('div');
      expect(stepContainer).toHaveClass('bg-blue-500', 'text-white', 'animate-pulse');
    });
  });

  describe('Data Type Selection', () => {
    it('should display three data type options', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      expect(screen.getByText('First Party Data')).toBeInTheDocument();
      expect(screen.getByText('Third Party Data')).toBeInTheDocument();
      expect(screen.getByText('Clean Room Data')).toBeInTheDocument();
    });

    it('should display correct descriptions for each data type', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      expect(screen.getByText('Your direct customer data with full activation rights')).toBeInTheDocument();
      expect(screen.getByText('Licensed external data with usage restrictions')).toBeInTheDocument();
      expect(screen.getByText('Privacy-compliant collaborative data environments')).toBeInTheDocument();
    });

    it('should advance to step 2 when data type is selected', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);
      
      // Check that step 2 is now active
      const step2 = screen.getByText('2');
      const stepContainer = step2.closest('div');
      expect(stepContainer).toHaveClass('bg-blue-500', 'text-white');
    });
  });

  describe('Welcome Message', () => {
    it('should display welcome message initially', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      expect(screen.getByText(/Welcome! I'm here to help you build high-performing audience segments/)).toBeInTheDocument();
    });
  });

  describe('Input Area', () => {
    it('should have placeholder text based on current step', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      // Step 1 placeholder
      const input = screen.getByPlaceholderText('Select a data type first...');
      expect(input).toBeInTheDocument();
      expect(input).toBeDisabled();
    });

    it('should enable input after selecting data type', () => {
      render(<EnhancedNLAudienceBuilder />);
      
      // Select data type
      fireEvent.click(screen.getByText('First Party Data'));
      
      // Input should now be enabled with different placeholder
      const input = screen.getByPlaceholderText('Describe your target audience...');
      expect(input).toBeInTheDocument();
      expect(input).not.toBeDisabled();
    });
  });

  describe('Enhanced Variable Picker API Integration', () => {
    beforeEach(() => {
      // Mock session initialization
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/nl/start_session')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ session_id: 'test-session-123' })
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({})
        });
      });
    });

    it('should call enhanced variable picker API on search', async () => {
      render(<EnhancedNLAudienceBuilder />);
      
      // Wait for session
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/nl/start_session'),
          expect.any(Object)
        );
      });

      // Select data type
      fireEvent.click(screen.getByText('First Party Data'));
      
      // Enter search query
      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'test query' } });
      
      // Mock enhanced API response
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              results: [{
                code: 'TEST_VAR',
                name: 'Test Variable',
                score: 0.9
              }],
              total_found: 1
            })
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });
      
      // Submit
      fireEvent.click(screen.getByRole('button', { name: /send icon/i }));
      
      // Verify API was called
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/enhanced-variable-picker/search',
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query: 'test query',
              top_k: 50,
              use_semantic: true,
              use_keyword: true
            })
          })
        );
      });
    });
  });
});