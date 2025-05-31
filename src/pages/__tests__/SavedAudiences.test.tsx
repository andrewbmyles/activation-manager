import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { SavedAudiences } from '../SavedAudiences';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useNavigate: () => mockNavigate,
}));

// Mock fetch
global.fetch = jest.fn();

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <div>{children}</div>
);

describe('SavedAudiences Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays loading state initially', () => {
    (global.fetch as jest.Mock).mockImplementation(() => 
      new Promise(() => {}) // Never resolves to keep loading
    );

    render(<SavedAudiences />, { wrapper });
    
    // Should show loading spinner
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
  });

  test('displays empty state when no audiences exist', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        audiences: [],
        count: 0,
      }),
    });

    render(<SavedAudiences />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('No saved audiences yet.')).toBeInTheDocument();
      expect(screen.getByText(/Create your first audience/)).toBeInTheDocument();
    });
  });

  test('displays list of saved audiences', async () => {
    const mockAudiences = [
      {
        audience_id: 'aud_123',
        name: 'Test Audience 1',
        description: 'Description 1',
        total_audience_size: 100000,
        segments: [1, 2, 3],
        created_at: '2025-05-28T12:00:00Z',
        selected_variables: ['VAR1', 'VAR2', 'VAR3'],
      },
      {
        audience_id: 'aud_456',
        name: 'Test Audience 2',
        description: 'Description 2',
        total_audience_size: 200000,
        segments: [1, 2],
        created_at: '2025-05-27T12:00:00Z',
        selected_variables: ['VAR4', 'VAR5'],
      },
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        audiences: mockAudiences,
        count: 2,
      }),
    });

    render(<SavedAudiences />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Test Audience 1')).toBeInTheDocument();
      expect(screen.getByText('Test Audience 2')).toBeInTheDocument();
      expect(screen.getByText('100,000 records')).toBeInTheDocument();
      expect(screen.getByText('200,000 records')).toBeInTheDocument();
    });
  });

  test('handles navigation to audience builder', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        audiences: [],
        count: 0,
      }),
    });

    render(<SavedAudiences />, { wrapper });

    await waitFor(() => {
      const createButton = screen.getByText('Create New Audience');
      fireEvent.click(createButton);
      expect(mockNavigate).toHaveBeenCalledWith('/audience-builder');
    });
  });

  test('handles archive audience action', async () => {
    const mockAudiences = [
      {
        audience_id: 'aud_123',
        name: 'Test Audience',
        description: 'Test description',
        total_audience_size: 100000,
        segments: [],
        created_at: '2025-05-28T12:00:00Z',
        selected_variables: ['VAR1'],
      },
    ];

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          audiences: mockAudiences,
          count: 1,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Audience archived',
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          audiences: [],
          count: 0,
        }),
      });

    // Mock window.confirm
    window.confirm = jest.fn(() => true);

    render(<SavedAudiences />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Test Audience')).toBeInTheDocument();
    });

    // Find and click archive button
    const archiveButton = screen.getByTitle('Archive');
    fireEvent.click(archiveButton);

    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to archive this audience?');

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/audiences/aud_123/status'),
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: 'demo_user',
            status: 'archived',
          }),
        })
      );
    });
  });

  test('displays variable tags correctly', async () => {
    const mockAudiences = [
      {
        audience_id: 'aud_123',
        name: 'Test Audience',
        description: 'Test description',
        total_audience_size: 100000,
        segments: [],
        created_at: '2025-05-28T12:00:00Z',
        selected_variables: ['VAR1', 'VAR2', 'VAR3', 'VAR4', 'VAR5', 'VAR6', 'VAR7'],
      },
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        audiences: mockAudiences,
        count: 1,
      }),
    });

    render(<SavedAudiences />, { wrapper });

    await waitFor(() => {
      // Should show first 5 variables
      expect(screen.getByText('VAR1')).toBeInTheDocument();
      expect(screen.getByText('VAR2')).toBeInTheDocument();
      expect(screen.getByText('VAR3')).toBeInTheDocument();
      expect(screen.getByText('VAR4')).toBeInTheDocument();
      expect(screen.getByText('VAR5')).toBeInTheDocument();
      
      // Should show count of remaining variables
      expect(screen.getByText('+2 more')).toBeInTheDocument();
    });
  });

  test('handles view audience action', async () => {
    const mockAudiences = [
      {
        audience_id: 'aud_123',
        name: 'Test Audience',
        description: 'Test description',
        total_audience_size: 100000,
        segments: [],
        created_at: '2025-05-28T12:00:00Z',
        selected_variables: [],
      },
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        audiences: mockAudiences,
        count: 1,
      }),
    });

    render(<SavedAudiences />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Test Audience')).toBeInTheDocument();
    });

    // Find and click view button
    const viewButton = screen.getByTitle('View Details');
    fireEvent.click(viewButton);

    expect(mockNavigate).toHaveBeenCalledWith('/audience/aud_123');
  });

  test('handles API errors gracefully', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();
    
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<SavedAudiences />, { wrapper });

    await waitFor(() => {
      expect(consoleError).toHaveBeenCalledWith('Error fetching audiences:', expect.any(Error));
    });

    consoleError.mockRestore();
  });
});