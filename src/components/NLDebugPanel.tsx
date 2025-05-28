import React from 'react';

interface NLDebugPanelProps {
  sessionId: string | null;
  currentStep: number;
  isLoading: boolean;
  lastError?: any;
  apiResponses?: any[];
}

export function NLDebugPanel({ sessionId, currentStep, isLoading, lastError, apiResponses = [] }: NLDebugPanelProps) {
  if (process.env.NODE_ENV === 'production') {
    return null; // Don't show in production
  }

  return (
    <div className="fixed bottom-4 right-4 bg-black text-green-400 p-4 rounded-lg shadow-lg max-w-md font-mono text-xs">
      <div className="mb-2 font-bold">🐛 NL Debug Panel</div>
      <div>Session ID: {sessionId || 'null'}</div>
      <div>Current Step: {currentStep}</div>
      <div>Loading: {isLoading ? 'true' : 'false'}</div>
      {lastError && (
        <div className="text-red-400 mt-2">
          Error: {JSON.stringify(lastError, null, 2)}
        </div>
      )}
      {apiResponses.length > 0 && (
        <div className="mt-2">
          <div>Last API Response:</div>
          <pre className="text-xs overflow-auto max-h-32">
            {JSON.stringify(apiResponses[apiResponses.length - 1], null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}