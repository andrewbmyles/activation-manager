/**
 * Unit tests for enhanced features in SavedAudiences component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { SavedAudiences } from '../SavedAudiences';

// Mock the utility functions
jest.mock('../../utils/audienceUtils', () => ({
  getAudienceIcon: jest.fn((query: string) => {
    if (query.includes('gaming')) return 'Gamepad2';
    if (query.includes('fashion')) return 'ShoppingBag';
    if (query.includes('health')) return 'Dumbbell';
    return 'Users';
  }),
  getAudienceIconColor: jest.fn((query: string) => {
    if (query.includes('gaming')) return '#8B5CF6';
    if (query.includes('fashion')) return '#EC4899';
    if (query.includes('health')) return '#10B981';
    return '#6B7280';
  })
}));

// Mock fetch for API calls
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div data-testid="mock-router">{children}</div>,
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/', search: '', hash: '', state: null }),
  useParams: () => ({}),
}));

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <BrowserRouter>{children}</BrowserRouter>;
};

describe('SavedAudiences - Enhanced Features', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
    mockNavigate.mockClear();
  });

  describe('Enhanced Audience Display', () => {
    it('should display audiences as cards in grid layout', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Gaming-Enthusiast Gen Z Males',
          name: 'Original Audience Name',
          description: 'Find males aged 18-24 interested in gaming',
          original_query: 'Find males aged 18-24 interested in gaming',
          natural_language_criteria: 'Males between the ages of 18 and 24 who are interested in video games',
          audience_size: 67842,
          total_audience_size: 67842,
          insights: [
            'Focused audience of 68K+ targeted users',
            'Technology-savvy consumers'
          ],
          segments: [
            { segment_id: 1, name: 'Core Gaming' },
            { segment_id: 2, name: 'Casual Gaming' }
          ],
          created_at: '2025-05-29T10:30:00Z',
          status: 'active'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Gaming-Enthusiast Gen Z Males')).toBeInTheDocument();
      });

      // Verify grid layout class is applied
      const gridContainer = screen.getByTestId('audiences-grid') || 
                           document.querySelector('.grid.grid-cols-1');
      expect(gridContainer).toBeTruthy();
    });

    it('should display enhanced name with fallback to original name', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_enhanced',
          enhanced_name: 'Fashion-Forward Millennial Women',
          name: 'Original Name',
          description: 'Fashion audience',
          audience_size: 84720,
          created_at: '2025-05-29T10:30:00Z'
        },
        {
          audience_id: 'aud_legacy',
          name: 'Legacy Audience Without Enhanced Name',
          description: 'Legacy audience',
          total_audience_size: 56798,
          created_at: '2025-05-28T14:20:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        // Enhanced audience should show enhanced_name
        expect(screen.getByText('Fashion-Forward Millennial Women')).toBeInTheDocument();
        
        // Legacy audience should show fallback to name
        expect(screen.getByText('Legacy Audience Without Enhanced Name')).toBeInTheDocument();
      });
    });

    it('should display natural language criteria with fallback', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Gaming Enthusiasts',
          natural_language_criteria: 'Males between the ages of 18 and 24 who are interested in video games',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        },
        {
          audience_id: 'aud_002',
          name: 'Legacy Audience',
          description: 'Technical description of legacy audience',
          total_audience_size: 56798,
          created_at: '2025-05-28T14:20:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        // Enhanced criteria should be displayed
        expect(screen.getByText(/Males between the ages of 18 and 24/)).toBeInTheDocument();
        
        // Legacy should show description fallback
        expect(screen.getByText(/Technical description of legacy audience/)).toBeInTheDocument();
      });
    });

    it('should display formatted audience sizes', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Large Audience',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        },
        {
          audience_id: 'aud_002',
          name: 'Legacy Audience',
          total_audience_size: 156798,
          created_at: '2025-05-28T14:20:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        // Should display formatted numbers with commas
        expect(screen.getByText('67,842')).toBeInTheDocument();
        expect(screen.getByText('156,798')).toBeInTheDocument();
      });
    });
  });

  describe('Dynamic Icon System', () => {
    it('should select appropriate icons based on audience type', async () => {
      const { getAudienceIcon, getAudienceIconColor } = require('../../utils/audienceUtils');

      const mockAudiences = [
        {
          audience_id: 'aud_gaming',
          enhanced_name: 'Gaming Enthusiasts',
          original_query: 'Find gaming console owners',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        },
        {
          audience_id: 'aud_fashion',
          enhanced_name: 'Fashion Lovers',
          original_query: 'Find fashion shopping enthusiasts',
          audience_size: 84720,
          created_at: '2025-05-29T09:15:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Gaming Enthusiasts')).toBeInTheDocument();
        expect(screen.getByText('Fashion Lovers')).toBeInTheDocument();
      });

      // Verify icon selection was called with correct queries
      expect(getAudienceIcon).toHaveBeenCalledWith('Find gaming console owners');
      expect(getAudienceIcon).toHaveBeenCalledWith('Find fashion shopping enthusiasts');
      
      // Verify color selection
      expect(getAudienceIconColor).toHaveBeenCalledWith('Find gaming console owners');
      expect(getAudienceIconColor).toHaveBeenCalledWith('Find fashion shopping enthusiasts');
    });

    it('should handle missing query data for icon selection', async () => {
      const { getAudienceIcon } = require('../../utils/audienceUtils');

      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Audience Without Query',
          description: 'Some description',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
          // Missing original_query
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Audience Without Query')).toBeInTheDocument();
      });

      // Should fallback to description when original_query is missing
      expect(getAudienceIcon).toHaveBeenCalledWith('Some description');
    });
  });

  describe('Insights Display', () => {
    it('should display first 2 insights when available', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Tech Enthusiasts',
          audience_size: 67842,
          insights: [
            'Focused audience of 68K+ targeted users',
            'Technology-savvy consumers',
            'Digital-native generation',
            'High engagement rates'
          ],
          created_at: '2025-05-29T10:30:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        // Should display first 2 insights
        expect(screen.getByText(/Focused audience of 68K\+ targeted users/)).toBeInTheDocument();
        expect(screen.getByText(/Technology-savvy consumers/)).toBeInTheDocument();
        
        // Should not display 3rd and 4th insights
        expect(screen.queryByText(/Digital-native generation/)).not.toBeInTheDocument();
        expect(screen.queryByText(/High engagement rates/)).not.toBeInTheDocument();
      });
    });

    it('should handle audiences without insights', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Basic Audience',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
          // No insights property
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Basic Audience')).toBeInTheDocument();
        // Should not crash or show insights section
        expect(screen.queryByText('Key Insights:')).not.toBeInTheDocument();
      });
    });
  });

  describe('Card Interactions', () => {
    it('should handle view audience action', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Test Audience',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Audience')).toBeInTheDocument();
      });

      // Click view button
      const viewButton = screen.getByTitle('View Details');
      fireEvent.click(viewButton);

      expect(mockNavigate).toHaveBeenCalledWith('/audience/aud_001');
    });

    it('should handle archive audience action', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Test Audience',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        }
      ];

      // Mock initial fetch and archive response
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, audiences: mockAudiences })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, audiences: [] })
        });

      // Mock window.confirm
      const originalConfirm = window.confirm;
      window.confirm = jest.fn(() => true);

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Audience')).toBeInTheDocument();
      });

      // Click archive button
      const archiveButton = screen.getByTitle('Archive');
      fireEvent.click(archiveButton);

      // Should call archive API
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/audiences/aud_001/status', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: 'demo_user',
            status: 'archived'
          })
        });
      });

      // Restore window.confirm
      window.confirm = originalConfirm;
    });

    it('should handle activate audience action', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Test Audience',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Audience')).toBeInTheDocument();
      });

      // Click activate button
      const activateButton = screen.getByText('Activate Audience');
      fireEvent.click(activateButton);

      expect(mockNavigate).toHaveBeenCalledWith('/distribution?audience=aud_001');
    });
  });

  describe('Loading and Error States', () => {
    it('should show loading state', () => {
      // Mock a never-resolving promise to keep loading state
      mockFetch.mockImplementationOnce(() => new Promise(() => {}));

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      expect(screen.getByRole('status')).toBeInTheDocument(); // Loading spinner
    });

    it('should handle empty audiences list', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: [] })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('No saved audiences yet.')).toBeInTheDocument();
        expect(screen.getByText(/Create your first audience/)).toBeInTheDocument();
      });
    });

    it('should handle API errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('API Error'));

      // Mock console.error to avoid test output noise
      const originalError = console.error;
      console.error = jest.fn();

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        // Should handle error gracefully and stop loading
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
      });

      // Restore console.error
      console.error = originalError;
    });
  });

  describe('Responsive Design', () => {
    it('should apply responsive grid classes', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Test Audience 1',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        },
        {
          audience_id: 'aud_002',
          enhanced_name: 'Test Audience 2',
          audience_size: 84720,
          created_at: '2025-05-29T09:15:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Audience 1')).toBeInTheDocument();
      });

      // Check for responsive grid classes
      const gridContainer = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3');
      expect(gridContainer).toBeTruthy();
    });
  });

  describe('Date Formatting', () => {
    it('should format creation dates correctly', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Test Audience',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        // Should display formatted date
        expect(screen.getByText(/Created 5\/29\/2025/)).toBeInTheDocument();
      });
    });
  });

  describe('Segment Information', () => {
    it('should display segment count', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'Multi-Segment Audience',
          audience_size: 67842,
          segments: [
            { segment_id: 1, name: 'Segment 1' },
            { segment_id: 2, name: 'Segment 2' },
            { segment_id: 3, name: 'Segment 3' }
          ],
          created_at: '2025-05-29T10:30:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('3 segments')).toBeInTheDocument();
      });
    });

    it('should handle audiences without segments', async () => {
      const mockAudiences = [
        {
          audience_id: 'aud_001',
          enhanced_name: 'No Segments Audience',
          audience_size: 67842,
          created_at: '2025-05-29T10:30:00Z'
          // No segments property
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, audiences: mockAudiences })
      });

      render(
        <TestWrapper>
          <SavedAudiences />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('0 segments')).toBeInTheDocument();
      });
    });
  });
});