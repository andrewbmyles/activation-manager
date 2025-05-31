import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app without crashing', () => {
  const { container } = render(<App />);
  // Just check that the app renders without crashing
  expect(container).toBeInTheDocument();
});
