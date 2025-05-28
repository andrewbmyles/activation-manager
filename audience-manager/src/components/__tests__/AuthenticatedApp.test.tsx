import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from '../../App';

// Mock the Login component
jest.mock('../Login', () => ({
  __esModule: true,
  default: ({ onLogin }: any) => (
    <div data-testid="login-component">
      <button onClick={() => onLogin('test@example.com', 'password')}>
        Mock Login
      </button>
    </div>
  ),
}));

// Mock Layout component
jest.mock('../Layout', () => ({
  __esModule: true,
  default: ({ children, user, onLogout }: any) => (
    <div data-testid="layout-component">
      <div data-testid="user-info">{user?.email}</div>
      <button onClick={onLogout}>Logout</button>
      {children}
    </div>
  ),
}));

// Mock fetch
global.fetch = jest.fn();

describe('App Authentication Flow', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    jest.clearAllMocks();
    
    // Reset fetch mock
    (global.fetch as jest.Mock).mockReset();
  });

  const renderApp = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  test('shows loading state initially', () => {
    // Mock auth check to be pending
    (global.fetch as jest.Mock).mockImplementation(() => 
      new Promise(() => {}) // Never resolves
    );

    renderApp();
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('shows login when not authenticated', async () => {
    // Mock auth check to return not authenticated
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ authenticated: false }),
    });

    renderApp();
    
    await waitFor(() => {
      expect(screen.getByTestId('login-component')).toBeInTheDocument();
    });
  });

  test('shows app when authenticated', async () => {
    // Mock auth check to return authenticated
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ 
        authenticated: true,
        user: { email: 'test@example.com' }
      }),
    });

    renderApp();
    
    await waitFor(() => {
      expect(screen.getByTestId('layout-component')).toBeInTheDocument();
      expect(screen.getByTestId('user-info')).toHaveTextContent('test@example.com');
    });
  });

  test('handles successful login', async () => {
    const user = userEvent.setup();
    
    // Mock initial auth check - not authenticated
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ authenticated: false }),
    });

    renderApp();
    
    await waitFor(() => {
      expect(screen.getByTestId('login-component')).toBeInTheDocument();
    });

    // Mock login request
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ 
        success: true,
        user: { email: 'test@example.com' }
      }),
    });

    // Click mock login button
    await user.click(screen.getByText('Mock Login'));

    await waitFor(() => {
      expect(screen.getByTestId('layout-component')).toBeInTheDocument();
    });

    // Verify login API was called
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email: 'test@example.com', password: 'password' }),
      })
    );
  });

  test('handles failed login', async () => {
    const user = userEvent.setup();
    
    // Mock initial auth check - not authenticated
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ authenticated: false }),
    });

    renderApp();
    
    await waitFor(() => {
      expect(screen.getByTestId('login-component')).toBeInTheDocument();
    });

    // Mock failed login request
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ 
        success: false,
        error: 'Invalid credentials'
      }),
    });

    // Since we're using a mock Login component, we need to update the test
    // to check that the login error is handled
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    
    await user.click(screen.getByText('Mock Login'));

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Login failed:', expect.any(Error));
    });

    consoleErrorSpy.mockRestore();
  });

  test('handles logout', async () => {
    const user = userEvent.setup();
    
    // Mock initial auth check - authenticated
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ 
        authenticated: true,
        user: { email: 'test@example.com' }
      }),
    });

    renderApp();
    
    await waitFor(() => {
      expect(screen.getByTestId('layout-component')).toBeInTheDocument();
    });

    // Mock logout request
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Click logout button
    await user.click(screen.getByText('Logout'));

    await waitFor(() => {
      expect(screen.getByTestId('login-component')).toBeInTheDocument();
    });

    // Verify logout API was called
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/logout',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      })
    );
  });

  test('handles auth check error gracefully', async () => {
    // Mock auth check to fail
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    renderApp();
    
    await waitFor(() => {
      expect(screen.getByTestId('login-component')).toBeInTheDocument();
    });

    expect(consoleErrorSpy).toHaveBeenCalledWith('Auth check failed:', expect.any(Error));

    consoleErrorSpy.mockRestore();
  });

  test('includes credentials in all API calls', async () => {
    // Mock auth check
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ authenticated: false }),
    });

    renderApp();

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/status',
        expect.objectContaining({
          credentials: 'include',
        })
      );
    });
  });
});