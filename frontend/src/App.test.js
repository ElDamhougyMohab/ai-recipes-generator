import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

// Basic smoke test
test('renders App component without crashing', () => {
  const { container } = render(<App />);
  expect(container).toBeInTheDocument();
});

// Simple content test
test('App component renders content', () => {
  const { container } = render(<App />);
  expect(container.firstChild).toBeTruthy();
});
