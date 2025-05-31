import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Create a minimal test component that simulates the refine functionality
const RefineTestComponent = () => {
  const [currentStep, setCurrentStep] = React.useState(4);
  const [userInput, setUserInput] = React.useState('');
  const [isTyping, setIsTyping] = React.useState(false);
  const [sessionId] = React.useState('test-session');
  const [suggestedVariables, setSuggestedVariables] = React.useState([
    { code: 'VAR1', description: 'Test Variable 1', type: 'type1', relevance_score: 0.9 },
    { code: 'VAR2', description: 'Test Variable 2', type: 'type2', relevance_score: 0.8 }
  ]);

  const handleDynamicSearch = () => {
    setIsTyping(true);
    // Simulate API call
    setTimeout(() => {
      setSuggestedVariables([
        { code: 'VAR3', description: 'Refined Variable 1', type: 'type1', relevance_score: 0.95 },
        { code: 'VAR4', description: 'Refined Variable 2', type: 'type3', relevance_score: 0.85 }
      ]);
      setIsTyping(false);
    }, 100);
  };

  React.useEffect(() => {
    if (currentStep === 4 && userInput.trim().length > 0) {
      const timer = setTimeout(() => {
        handleDynamicSearch();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [userInput, currentStep]);

  return (
    <div>
      <div className="flex gap-2">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type to refine your search..."
          disabled={(currentStep !== 2 && currentStep !== 4) || !sessionId}
          data-testid="refine-input"
        />
        {currentStep === 4 && (
          <button
            onClick={handleDynamicSearch}
            disabled={!userInput.trim() || !sessionId || isTyping}
            className="px-4 py-2 bg-purple-500 text-white rounded-md"
            data-testid="refine-button"
          >
            {isTyping ? 'Loading...' : 'Refine'}
          </button>
        )}
      </div>
      {isTyping && <div data-testid="loading-indicator">Refining search...</div>}
      <div data-testid="variables-list">
        {suggestedVariables.map(v => (
          <div key={v.code} data-testid={`variable-${v.code}`}>
            {v.description}
          </div>
        ))}
      </div>
    </div>
  );
};

describe('Refine Button Functionality', () => {
  it('should enable input field during step 4', () => {
    render(<RefineTestComponent />);
    
    const input = screen.getByTestId('refine-input');
    expect(input).not.toBeDisabled();
  });

  it('should show refine button during step 4', () => {
    render(<RefineTestComponent />);
    
    const refineButton = screen.getByTestId('refine-button');
    expect(refineButton).toBeInTheDocument();
    expect(refineButton).toHaveClass('bg-purple-500');
  });

  it('should disable refine button when input is empty', () => {
    render(<RefineTestComponent />);
    
    const refineButton = screen.getByTestId('refine-button');
    expect(refineButton).toBeDisabled();
  });

  it('should enable refine button when input has text', () => {
    render(<RefineTestComponent />);
    
    const input = screen.getByTestId('refine-input');
    const refineButton = screen.getByTestId('refine-button');
    
    fireEvent.change(input, { target: { value: 'test search' } });
    
    expect(refineButton).not.toBeDisabled();
  });

  it('should show loading state when refining', async () => {
    render(<RefineTestComponent />);
    
    const input = screen.getByTestId('refine-input');
    const refineButton = screen.getByTestId('refine-button');
    
    fireEvent.change(input, { target: { value: 'test search' } });
    fireEvent.click(refineButton);
    
    // Should show loading state
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.getByText('Refine')).toBeInTheDocument();
    });
  });

  it('should update variables after refinement', async () => {
    render(<RefineTestComponent />);
    
    // Initial variables
    expect(screen.getByText('Test Variable 1')).toBeInTheDocument();
    expect(screen.getByText('Test Variable 2')).toBeInTheDocument();
    
    const input = screen.getByTestId('refine-input');
    const refineButton = screen.getByTestId('refine-button');
    
    fireEvent.change(input, { target: { value: 'refined search' } });
    fireEvent.click(refineButton);
    
    // Wait for refinement to complete
    await waitFor(() => {
      expect(screen.getByText('Refined Variable 1')).toBeInTheDocument();
      expect(screen.getByText('Refined Variable 2')).toBeInTheDocument();
    });
    
    // Original variables should be gone
    expect(screen.queryByText('Test Variable 1')).not.toBeInTheDocument();
    expect(screen.queryByText('Test Variable 2')).not.toBeInTheDocument();
  });

  it('should trigger search automatically after typing', async () => {
    jest.useFakeTimers();
    
    render(<RefineTestComponent />);
    
    const input = screen.getByTestId('refine-input');
    
    // Initial variables
    expect(screen.getByText('Test Variable 1')).toBeInTheDocument();
    
    // Type in the input
    fireEvent.change(input, { target: { value: 'auto search' } });
    
    // Fast forward 500ms
    jest.advanceTimersByTime(500);
    
    // Wait for the update
    await waitFor(() => {
      expect(screen.getByText('Refined Variable 1')).toBeInTheDocument();
    });
    
    jest.useRealTimers();
  });
});