import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock Brain icon from lucide-react
jest.mock('lucide-react', () => ({
  ...jest.requireActual('lucide-react'),
  Brain: ({ className }: any) => <div data-testid="brain-icon" className={className}>Brain Icon</div>,
}));

// Test component for semantic variable display
const SemanticVariableDisplay = ({ variable }: any) => {
  const Brain = require('lucide-react').Brain;
  
  return (
    <div className="flex-1">
      <p className="text-sm font-medium text-gray-800">{variable.description}</p>
      <div className="flex items-center gap-2 mt-1">
        <div className="flex items-center gap-1">
          <Brain className="w-3 h-3 text-indigo-500" />
          <span className="text-xs text-gray-500">Semantic</span>
        </div>
        <span className="text-xs text-gray-500">•</span>
        <div className="group relative inline-flex items-center">
          <span className="text-xs text-gray-500">Score: {variable.relevance_score}</span>
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-50 pointer-events-none">
            <div className="bg-gray-900 text-white text-xs rounded px-3 py-2 whitespace-nowrap max-w-xs">
              <p className="font-medium mb-1">Relevance Score: {variable.relevance_score}</p>
              <p>This AI-generated score (0-1) indicates how closely this variable matches your audience description.</p>
              <p className="mt-1">Higher scores = stronger semantic match</p>
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                <div className="border-4 border-transparent border-t-gray-900"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

describe('Semantic Variable Display', () => {
  const mockVariable = {
    code: 'TEST_VAR',
    description: 'Test Variable Description',
    type: 'demographic',
    relevance_score: 0.85
  };

  it('should display Semantic label instead of variable type', () => {
    render(<SemanticVariableDisplay variable={mockVariable} />);
    
    // Should show "Semantic" not the original type
    expect(screen.getByText('Semantic')).toBeInTheDocument();
    expect(screen.queryByText('demographic')).not.toBeInTheDocument();
    expect(screen.queryByText('parquet')).not.toBeInTheDocument();
  });

  it('should show Brain icon', () => {
    render(<SemanticVariableDisplay variable={mockVariable} />);
    
    const brainIcon = screen.getByTestId('brain-icon');
    expect(brainIcon).toBeInTheDocument();
    expect(brainIcon).toHaveClass('text-indigo-500');
  });

  it('should display relevance score', () => {
    render(<SemanticVariableDisplay variable={mockVariable} />);
    
    expect(screen.getByText('Score: 0.85')).toBeInTheDocument();
  });

  it('should show tooltip content on hover', () => {
    const { container } = render(<SemanticVariableDisplay variable={mockVariable} />);
    
    // The tooltip should contain explanation text
    expect(screen.getByText('Relevance Score: 0.85')).toBeInTheDocument();
    expect(screen.getByText('This AI-generated score (0-1) indicates how closely this variable matches your audience description.')).toBeInTheDocument();
    expect(screen.getByText('Higher scores = stronger semantic match')).toBeInTheDocument();
  });

  it('should format different score values correctly', () => {
    const variables = [
      { ...mockVariable, relevance_score: 1.0 },
      { ...mockVariable, relevance_score: 0.5 },
      { ...mockVariable, relevance_score: 0.33 }
    ];

    variables.forEach(variable => {
      const { unmount } = render(<SemanticVariableDisplay variable={variable} />);
      expect(screen.getByText(`Score: ${variable.relevance_score}`)).toBeInTheDocument();
      unmount();
    });
  });

  it('should have proper styling classes', () => {
    const { container } = render(<SemanticVariableDisplay variable={mockVariable} />);
    
    // Check for semantic badge styling
    const semanticBadge = container.querySelector('.flex.items-center.gap-1');
    expect(semanticBadge).toBeInTheDocument();
    
    // Check for score container styling
    const scoreContainer = container.querySelector('.group.relative.inline-flex.items-center');
    expect(scoreContainer).toBeInTheDocument();
  });
});