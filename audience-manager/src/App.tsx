import React, { useState } from 'react';
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
import VariablePicker from './pages/VariablePicker';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  // Hardcode a default user - no login required
  const [user] = useState<string>('user@example.com');

  const handleLogout = async () => {
    // Just refresh the page for now
    window.location.reload();
  };

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="min-h-screen bg-gray-100">
            <Routes>
              <Route path="/" element={<Layout onLogout={handleLogout} user={user} />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="audiences" element={<AudienceBuilder />} />
                <Route path="variable-picker" element={<VariablePicker />} />
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