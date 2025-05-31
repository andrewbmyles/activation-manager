import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { EnhancedNLAudienceBuilder } from '../EnhancedNLAudienceBuilder';
import '@testing-library/jest-dom';

// Mock useNavigate at the top
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div data-testid="mock-router">{children}</div>,
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/', search: '', hash: '', state: null }),
  useParams: () => ({}),
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Send: () => <div>Send</div>,
  Loader2: () => <div>Loader2</div>,
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
  ChevronDown: () => <div>ChevronDown</div>,
  Search: () => <div>Search</div>,
  ChevronRight: () => <div>ChevronRight</div>,
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
}));

// Mock recharts
jest.mock('recharts', () => ({
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div />,
  Cell: () => <div />,
  ScatterChart: ({ children }: any) => <div data-testid="scatter-chart">{children}</div>,
  Scatter: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
}));


// Setup fetch mock
global.fetch = jest.fn();

describe('EnhancedNLAudienceBuilder - Enhanced Features', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <EnhancedNLAudienceBuilder />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  describe('Component Naming', () => {
    it('should display "Natural Language Multi-Variate Audience Builder" as the title', () => {
      renderComponent();
      expect(screen.getByText('Natural Language Multi-Variate Audience Builder')).toBeInTheDocument();
    });
  });

  describe('Responsive UI Scaling', () => {
    it('should have responsive height for main container', () => {
      const { container } = renderComponent();
      const mainContainer = container.querySelector('.flex.h-\\[calc\\(100vh-16rem\\)\\].min-h-\\[600px\\]');
      expect(mainContainer).toBeInTheDocument();
    });

    it('should have responsive width classes for workflow sidebar', () => {
      const { container } = renderComponent();
      const sidebar = container.querySelector('.w-64.lg\\:w-80.xl\\:w-96');
      expect(sidebar).toBeInTheDocument();
    });

    it('should have responsive max-width for chat messages', () => {
      renderComponent();
      
      // Check welcome message has responsive classes
      const welcomeMessage = screen.getByText(/Welcome! I'm here to help you build/);
      const messageContainer = welcomeMessage.closest('div');
      expect(messageContainer).toHaveClass('max-w-2xl', 'lg:max-w-3xl', 'xl:max-w-4xl');
    });

    it('should have responsive padding for chat area', () => {
      const { container } = renderComponent();
      const chatArea = container.querySelector('.flex-1.overflow-y-auto.p-6.lg\\:p-8.xl\\:p-10');
      expect(chatArea).toBeInTheDocument();
    });

    it('should have responsive padding for input area', () => {
      const { container } = renderComponent();
      const inputArea = container.querySelector('.border-t.border-gray-200.p-4.lg\\:p-6');
      expect(inputArea).toBeInTheDocument();
    });
  });

  describe('Enhanced Variable Picker Integration', () => {
    beforeEach(() => {
      // Mock successful session start
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/nl/start_session')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ session_id: 'test-session-123' }),
          });
        }
        return Promise.reject(new Error('Not mocked'));
      });
    });

    it('should use enhanced variable picker API when searching variables', async () => {
      renderComponent();

      // Wait for session to initialize
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/nl/start_session'),
          expect.any(Object)
        );
      });

      // Select data type first
      const firstPartyButton = screen.getByText('First Party Data');
      fireEvent.click(firstPartyButton);

      // Enter search query
      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'young millennials who shop online' } });

      // Mock enhanced API response
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              results: [
                {
                  code: 'AGE_25_34',
                  name: 'Age 25-34 (Millennials)',
                  score: 0.95,
                  dataType: 'demographic',
                  category: 'Demographics'
                },
                {
                  code: 'ONLINE_SHOPPER',
                  description: 'Frequent Online Shopper',
                  score: 0.88,
                  dataType: 'behavioral',
                  category: 'Behavior'
                }
              ],
              total_found: 2,
              search_methods: { semantic: true, keyword: true }
            }),
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({}),
        });
      });

      // Submit search
      const sendButton = screen.getByRole('button', { name: /send/i });
      fireEvent.click(sendButton);

      // Verify enhanced API was called
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/enhanced-variable-picker/search',
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query: 'young millennials who shop online',
              top_k: 50,
              use_semantic: true,
              use_keyword: true
            })
          })
        );
      });
    });

    it('should handle dynamic search with enhanced API', async () => {
      renderComponent();

      // Initialize session
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });

      // Select data type
      fireEvent.click(screen.getByText('First Party Data'));

      // Submit initial query to get to variable selection
      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'initial query' } });

      // Mock response for initial query
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              results: [{ code: 'VAR1', name: 'Variable 1', score: 0.8 }],
              total_found: 1
            }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      // Wait for variable selection step
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type to refine your search...')).toBeInTheDocument();
      });

      // Type in refinement input
      const refineInput = screen.getByPlaceholderText('Type to refine your search...');
      fireEvent.change(refineInput, { target: { value: 'health conscious' } });

      // Verify debounced search is triggered
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/enhanced-variable-picker/search',
          expect.objectContaining({
            body: expect.stringContaining('health conscious')
          })
        );
      }, { timeout: 1000 });
    });

    it('should properly transform enhanced API results to Variable interface', async () => {
      renderComponent();

      // Initialize and navigate to variable selection
      await waitFor(() => expect(global.fetch).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));

      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'test query' } });

      // Mock enhanced API with various field formats
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              results: [
                {
                  VarId: 'VAR_ID_FORMAT',
                  Description: 'Description format',
                  DataType: 'DataType format',
                  relevance_score: 0.92,
                  Category: 'Category format'
                },
                {
                  code: 'STANDARD_FORMAT',
                  name: 'Standard name',
                  dataType: 'standard type',
                  score: 0.85,
                  category: 'standard category'
                }
              ],
              total_found: 2
            }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      // Check that variables are properly displayed
      await waitFor(() => {
        expect(screen.getByText('Description format')).toBeInTheDocument();
        expect(screen.getByText('Standard name')).toBeInTheDocument();
      });
    });
  });

  describe('Fallback Mechanisms', () => {
    beforeEach(() => {
      // Mock session initialization
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/nl/start_session')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ session_id: 'test-session' }),
          });
        }
        return Promise.reject(new Error('Not mocked'));
      });
    });

    it('should fallback to original API when enhanced picker fails', async () => {
      renderComponent();

      await waitFor(() => expect(global.fetch).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));

      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'test fallback' } });

      // Mock enhanced API to fail, original API to succeed
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: false,
            statusText: 'Service Unavailable'
          });
        }
        if (url.includes('/nl/process')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              status: 'variables_suggested',
              suggested_variables: {
                category1: [
                  { id: 'FALLBACK_VAR', description: 'Fallback Variable', type: 'test' }
                ]
              }
            }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      // Verify fallback was used
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/nl/process'),
          expect.any(Object)
        );
      });

      // Check fallback variable is displayed
      await waitFor(() => {
        expect(screen.getByText('Fallback Variable')).toBeInTheDocument();
      });
    });

    it('should handle enhanced API returning empty results', async () => {
      renderComponent();

      await waitFor(() => expect(global.fetch).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));

      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'empty results test' } });

      // Mock enhanced API with empty results
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              results: [],
              total_found: 0
            }),
          });
        }
        if (url.includes('/nl/process')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              status: 'variables_suggested',
              suggested_variables: {
                fallback: [{ id: 'FALLBACK', description: 'Fallback from empty', type: 'test' }]
              }
            }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      // Should use fallback when enhanced returns empty
      await waitFor(() => {
        expect(screen.getByText('Fallback from empty')).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading indicator when searching variables', async () => {
      renderComponent();

      // Setup slow response
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({ session_id: 'test' })
        }), 100))
      );

      await waitFor(() => expect(global.fetch).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));

      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'test' } });
      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      // Should show loading spinner
      expect(screen.getByText('Loader2')).toBeInTheDocument();
    });

    it('should disable input during variable loading', async () => {
      renderComponent();

      await waitFor(() => expect(global.fetch).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));

      const input = screen.getByPlaceholderText('Describe your target audience...');
      const sendButton = screen.getByRole('button', { name: /send/i });

      // Setup slow response
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({ results: [] })
        }), 100))
      );

      fireEvent.change(input, { target: { value: 'test' } });
      fireEvent.click(sendButton);

      // Input should be disabled during loading
      expect(input).toBeDisabled();
      expect(sendButton).toBeDisabled();
    });
  });

  describe('Variable Selection Display', () => {
    it('should show enhanced variable details with score and category', async () => {
      renderComponent();

      await waitFor(() => expect(global.fetch).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));

      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'test' } });

      // Mock rich variable data
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              results: [
                {
                  code: 'HIGH_INCOME',
                  name: 'High Income Households',
                  score: 0.95,
                  category: 'Demographics',
                  dataType: 'demographic'
                }
              ]
            }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      // Check variable details are displayed
      await waitFor(() => {
        expect(screen.getByText('High Income Households')).toBeInTheDocument();
        expect(screen.getByText('Score: 0.95')).toBeInTheDocument();
        expect(screen.getByText('Semantic')).toBeInTheDocument();
      });
    });

    it('should have responsive max-height for variable list', async () => {
      const { container } = renderComponent();

      await waitFor(() => expect(global.fetch).toHaveBeenCalled());
      fireEvent.click(screen.getByText('First Party Data'));

      const input = screen.getByPlaceholderText('Describe your target audience...');
      fireEvent.change(input, { target: { value: 'test' } });

      // Mock many variables
      (global.fetch as jest.Mock).mockImplementation((url) => {
        if (url.includes('/enhanced-variable-picker/search')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              results: Array.from({ length: 20 }, (_, i) => ({
                code: `VAR_${i}`,
                name: `Variable ${i}`,
                score: 0.8
              }))
            }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      // Check for responsive height class
      await waitFor(() => {
        const variableList = container.querySelector('.space-y-2.max-h-64.lg\\:max-h-96.xl\\:max-h-\\[32rem\\]');
        expect(variableList).toBeInTheDocument();
      });
    });
  });
});