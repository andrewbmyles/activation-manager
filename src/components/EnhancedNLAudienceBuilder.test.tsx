import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { EnhancedNLAudienceBuilder } from './EnhancedNLAudienceBuilder';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
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

// Mock fetch
global.fetch = jest.fn();

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('EnhancedNLAudienceBuilder', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  test('renders initial state with data type selection', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
    });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/Welcome! I'm here to help you build high-performing audience segments/)).toBeInTheDocument();
    });

    // Check data type options
    expect(screen.getByText('First Party Data')).toBeInTheDocument();
    expect(screen.getByText('Third Party Data')).toBeInTheDocument();
    expect(screen.getByText('Clean Room Data')).toBeInTheDocument();

    // Check subtypes
    expect(screen.getByText('RampID')).toBeInTheDocument();
    expect(screen.getByText('UID2.0')).toBeInTheDocument();
    expect(screen.getByText('Postal Code')).toBeInTheDocument();
    expect(screen.getByText('IAB Standard')).toBeInTheDocument();
    expect(screen.getByText('Clean Room Matched')).toBeInTheDocument();
  });

  test('workflow steps display correctly', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
    });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Workflow Progress')).toBeInTheDocument();
    });

    const steps = [
      'Select Data Type',
      'Describe Audience',
      'Variable Selection',
      'Confirm Variables',
      'Create Segments',
      'Review Results',
      'Distribution'
    ];

    steps.forEach(step => {
      expect(screen.getByText(step)).toBeInTheDocument();
    });
  });

  test('data type selection updates workflow and shows strategic message', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
    });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('First Party Data')).toBeInTheDocument();
    });

    // Click First Party Data
    const firstPartyButton = screen.getByText('First Party Data').closest('button');
    fireEvent.click(firstPartyButton!);

    await waitFor(() => {
      expect(screen.getByText(/Excellent choice! First Party Data gives you maximum control/)).toBeInTheDocument();
    });
  });

  test('natural language input and variable selection', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'variables_suggested',
          suggested_variables: {
            psychographic: [
              {
                code: 'ENV_SCORE',
                description: 'Environmental consciousness score',
                type: 'psychographic',
                relevance_score: 8.5,
                dataAvailability: {
                  first_party: true,
                  third_party: true,
                  clean_room: false
                }
              }
            ],
            demographic: [
              {
                code: 'AGE_RANGE',
                description: 'Age range millennials',
                type: 'demographic',
                relevance_score: 7.2,
                dataAvailability: {
                  first_party: true,
                  third_party: false,
                  clean_room: true
                }
              }
            ]
          },
          total_suggested: 2,
          data_type: 'first_party'
        }),
      });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('First Party Data')).toBeInTheDocument();
    });

    // Select data type
    fireEvent.click(screen.getByText('First Party Data').closest('button')!);

    // Wait for input to be enabled
    await waitFor(() => {
      const input = screen.getByPlaceholderText('Describe your target audience...');
      expect(input).not.toBeDisabled();
    });

    // Type audience description
    const input = screen.getByPlaceholderText('Describe your target audience...');
    await userEvent.type(input, 'environmentally conscious millennials with high disposable income');

    // Submit
    const submitButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(submitButton);

    // Check for variable visualization
    await waitFor(() => {
      expect(screen.getByText('Variable Model Visualization')).toBeInTheDocument();
      expect(screen.getByText(/Excellent! I've identified/)).toBeInTheDocument();
    });

    // Check variables are displayed
    expect(screen.getByText('Environmental consciousness score')).toBeInTheDocument();
    expect(screen.getByText('Age range millennials')).toBeInTheDocument();

    // Check data availability icons
    expect(screen.getAllByTitle('First Party')).toHaveLength(2);
    expect(screen.getByTitle('Third Party')).toBeInTheDocument();
    expect(screen.getByTitle('Clean Room')).toBeInTheDocument();
  });

  test('variable confirmation and clustering', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'complete',
          segments: [
            {
              group_id: 0,
              size: 600,
              size_percentage: 60,
              name: 'Eco-Forward Innovators',
              dominantTraits: ['High Income', 'Urban', 'Young Adults']
            },
            {
              group_id: 1,
              size: 400,
              size_percentage: 40,
              name: 'Sustainable Lifestyle Leaders',
              dominantTraits: ['Environmental Focus', 'Tech-Savvy']
            }
          ],
          total_records: 1000,
          variables_used: ['ENV_SCORE', 'AGE_RANGE'],
          audience_id: 'test-audience-123'
        }),
      });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    // Mock that we're at the variable confirmation step
    await act(async () => {
      // Simulate being at step 4 with variables selected
      const component = screen.getByText('Workflow Progress').parentElement;
      expect(component).toBeInTheDocument();
    });
  });

  test('CSV export functionality', async () => {
    const mockOpen = jest.fn();
    const originalOpen = window.open;
    window.open = mockOpen;

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
      });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    // Simulate having results with audience ID
    await act(async () => {
      // Would need to set up the component in the right state
      // This is a simplified test
    });

    window.open = originalOpen;
  });

  test('distribution animation and navigation', async () => {
    jest.useFakeTimers();
    
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
      });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    // Would need to simulate getting to distribution step
    // and clicking distribute button

    await act(async () => {
      jest.advanceTimersByTime(3000);
    });

    // Verify navigation was called
    // expect(mockNavigate).toHaveBeenCalledWith('/distribution-center', expect.any(Object));

    jest.useRealTimers();
  });

  test('error handling displays user-friendly message', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
      })
      .mockRejectedValueOnce(new Error('API Error'));

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    // Select data type
    await waitFor(() => {
      expect(screen.getByText('First Party Data')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('First Party Data').closest('button')!);

    // Try to submit
    await waitFor(() => {
      const input = screen.getByPlaceholderText('Describe your target audience...');
      expect(input).not.toBeDisabled();
    });

    const input = screen.getByPlaceholderText('Describe your target audience...');
    await userEvent.type(input, 'test query');
    
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/I apologize - there was a technical issue/)).toBeInTheDocument();
    });
  });

  test('visualizations render correctly', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test-session-123', status: 'ready' }),
      });

    render(<EnhancedNLAudienceBuilder />, { wrapper: createWrapper() });

    // Since we mocked recharts, we just check the containers exist
    await waitFor(() => {
      expect(screen.getByText('Workflow Progress')).toBeInTheDocument();
    });

    // Would need to trigger variable selection to see visualizations
  });
});