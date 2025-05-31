import React, { useState } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Layout } from './Layout';
import { Dashboard } from './pages/Dashboard';
import { AudienceBuilder } from './pages/AudienceBuilder';
import { PlatformManagement } from './pages/PlatformManagement';
import { PlatformConfig } from './pages/PlatformConfig';
import { DistributionCenter } from './pages/DistributionCenter';
import { Analytics } from './pages/Analytics';
import VariablePicker from './pages/VariablePicker';
import './ActivationManager.css';

export function ActivationManagerApp() {
  // Use a default user for the activation manager
  const [user] = useState<string>('user@tobermory.ai');
  const navigate = useNavigate();

  const handleLogout = () => {
    // Navigate back to the main Tobermory app
    navigate('/home');
  };

  return (
    <div className="activation-manager-container">
      <Routes>
        <Route path="/" element={<Layout onLogout={handleLogout} user={user} />}>
          <Route index element={<Navigate to="dashboard" replace />} />
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
  );
}