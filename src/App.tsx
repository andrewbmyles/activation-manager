import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { AudienceBuilder } from './pages/AudienceBuilder';
import { PlatformManagement } from './pages/PlatformManagement';
import { PlatformConfig } from './pages/PlatformConfig';
import { DistributionCenter } from './pages/DistributionCenter';
import { Analytics } from './pages/Analytics';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="min-h-screen bg-gray-100">
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="audiences" element={<AudienceBuilder />} />
                <Route path="platforms" element={<PlatformManagement />} />
                <Route path="platforms/:platformId" element={<PlatformConfig />} />
                <Route path="distribution" element={<DistributionCenter />} />
                <Route path="analytics" element={<Analytics />} />
              </Route>
            </Routes>
          </div>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;