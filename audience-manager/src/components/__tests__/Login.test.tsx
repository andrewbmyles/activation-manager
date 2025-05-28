import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('Login Component', () => {
  const mockOnLogin = jest.fn();
  const defaultProps = {
    onLogin: mockOnLogin,
  };

  const renderLogin = (props = {}) => {
    return render(
      <BrowserRouter>
        <Login {...defaultProps} {...props} />
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form with all elements', () => {
    renderLogin();
    
    expect(screen.getByText('Welcome to Activation Manager')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('handles input changes', async () => {
    const user = userEvent.setup();
    renderLogin();
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'testpassword');
    
    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('testpassword');
  });

  test('submits form with valid credentials', async () => {
    const user = userEvent.setup();
    renderLogin();
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'andrew@tobermory.ai');
    await user.type(passwordInput, 'admin');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith('andrew@tobermory.ai', 'admin');
    });
  });

  test('prevents submission with empty fields', async () => {
    const user = userEvent.setup();
    renderLogin();
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);
    
    expect(mockOnLogin).not.toHaveBeenCalled();
  });

  test('shows loading state during submission', async () => {
    const user = userEvent.setup();
    renderLogin();
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password');
    
    // Mock a slow login
    mockOnLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));
    
    await user.click(submitButton);
    
    expect(screen.getByText(/signing in/i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  test('displays error message when provided', () => {
    const errorMessage = 'Invalid credentials';
    renderLogin({ error: errorMessage });
    
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toHaveClass('text-red-600');
  });

  test('handles form submission on Enter key', async () => {
    const user = userEvent.setup();
    renderLogin();
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password');
    await user.keyboard('{Enter}');
    
    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith('test@example.com', 'password');
    });
  });

  test('trims whitespace from inputs', async () => {
    const user = userEvent.setup();
    renderLogin();
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, '  test@example.com  ');
    await user.type(passwordInput, '  password  ');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith('test@example.com', 'password');
    });
  });

  test('password field masks input', () => {
    renderLogin();
    
    const passwordInput = screen.getByPlaceholderText('Password');
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('email field has correct type', () => {
    renderLogin();
    
    const emailInput = screen.getByPlaceholderText('Email');
    expect(emailInput).toHaveAttribute('type', 'email');
  });
});